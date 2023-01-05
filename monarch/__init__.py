import gql
from gql.transport.aiohttp import AIOHTTPTransport
from typing import List, Optional
import requests

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

_SET_TAGS_MUTATION = gql.gql(
    """
mutation SetTransactionTags($input: SetTransactionTagsInput!) {
    setTransactionTags(input: $input) {
        errors {
            ...PayloadErrorFields
            __typename
        }
        transaction {
            id
            tags {
                id
                __typename
            }
            __typename
        }
        __typename
    }
}
fragment PayloadErrorFields on PayloadError {
    fieldErrors {
        field
        messages
        __typename
    }
    message
    code
    __typename
}
"""
)


class Client:
    def __init__(self, token: str) -> None:
        self._token = token
        transport = AIOHTTPTransport(
            url="https://api.monarchmoney.com/graphql",
            headers={"Authorization": f"Token {token}"},
        )
        self._client = gql.Client(
            transport=transport, fetch_schema_from_transport=False
        )

    @classmethod
    def login(
        cls, username: str, password: str, totp: Optional[str] = None
    ) -> "Client":
        body = {
            "username": username,
            "password": password,
            "trusted_device": False,
            "supports_mfa": True,
        }
        if totp is not None:
            body["totp"] = totp
        r = requests.post("https://api.monarchmoney.com/auth/login/", json=body)
        r.raise_for_status()

        resp = r.json()
        return cls(resp["token"])

    def transactions(self):
        """
        Returns an iterable of all transactions.
        """
        offset = 0
        while True:
            result = self._client.execute(
                _TRANSACTIONS_QUERY,
                variable_values={
                    "limit": 100,
                    "orderBy": "date",
                    "filters": {
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

    def tags(self, search: Optional[str] = None):
        """
        Returns the tags and their IDs.
        """
        result = self._client.execute(_TAGS_QUERY, variable_values={"search": search})
        return result["householdTransactionTags"]

    def set_tags(self, transaction_id: str, tag_ids: List[str]) -> None:
        """
        Sets the entire list of tags on the transaction. Overwrites any existing
        tags. Pass empty list to clear all tags.
        """
        self._client.execute(
            _SET_TAGS_MUTATION,
            variable_values={
                "input": {"transactionId": transaction_id, "tagIds": tag_ids}
            },
        )

    def extend_token(self) -> None:
        """
        Extends the token expiration. Tokens are normally very short lived ~15
        minutes.
        """
        r = requests.post(
            "https://api.monarchmoney.com/auth/extend-token/",
            headers={"Authorization": f"Token {self.token}"},
        )
        r.raise_for_status()
