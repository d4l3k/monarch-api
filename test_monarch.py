import sys
from monarch import Client

client = Client(sys.argv[-1])

for transaction in client.transactions():
    print(transaction)

for tag in client.tags():
    print(tag)
