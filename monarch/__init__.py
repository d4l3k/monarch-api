import gql
from gql.transport.aiohttp import AIOHTTPTransport

_TRANSACTIONS_QUERY = gql.gql(
"""
query GetTransactionsList($offset: Int, $limit: Int, $filters: TransactionFilterInput, $orderBy: TransactionOrdering) {
    allTransactions(filters: $filters) {
        totalCount
        results(offset: $offset, limit: $limit, orderBy: $orderBy) {
            id
            ...TransactionsListFields
            __typename
        }
        __typename
    }
    transactionRules {
        id
        __typename
    }
}
fragment TransactionsListFields on Transaction {
    id
    ...TransactionOverviewFields
    __typename
}
fragment TransactionOverviewFields on Transaction {
    id
    amount
    pending
    date
    hideFromReports
    plaidName
    notes
    isRecurring
    reviewStatus
    attachments {
        id
        __typename
    }
    isSplitTransaction
    category {
        id
        name
        icon
        __typename
    }
    merchant {
        name
        id
        transactionsCount
        __typename
    }
    tags {
        id
        name
        color
        order
        __typename
    }
    __typename
}
"""
)

_TAGS_QUERY = gql.gql(
"""
query GetHouseholdTransactionTags($search: String, $limit: Int, $bulkParams: BulkTransactionDataParams) {
    householdTransactionTags(search: $search, limit: $limit, bulkParams: $bulkParams) {
        id
        name
        color
        order
        transactionCount
        __typename
    }
}
"""
)

class Client:
    def __init__(self, token):
        transport = AIOHTTPTransport(
            url="https://api.monarchmoney.com/graphql",
            headers={'Authorization': f'Token {token}'}
        )
        self._client = gql.Client(transport=transport, fetch_schema_from_transport=False)

    def transactions(self):
        offset = 0
        while True:
            result = self._client.execute(
                _TRANSACTIONS_QUERY,
                variable_values={
                    "limit": 100,
                    "orderBy": "date",
                    "filters":{
                        "search": "",
                        "categories": [],
                        "accounts": [],
                        "tags": [],
                    },
                    "offset": offset,
                },
            )
            results = result["allTransactions"]["results"]
            if len(results) == 0:
                break
            offset += len(results)
            for result in results:
                yield result

    def tags(self):
        result = self._client.execute(_TAGS_QUERY)
        return result["householdTransactionTags"]
