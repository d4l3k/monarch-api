# monarch-api

An unofficial Monarch Python client. This project is not affiliated with Monarch
and done entirely as a side project.

The goal of this project is to make it easier to do external analysis and
billing for shared expenses. The initial focus is on listing transactions and
setting tags to track paid expenses.

## Install

```shell
pip install git+https://github.com/d4l3k/monarch-api.git
```

## Basic Usage

```py
import monarch

client = monarch.Client(token="...")

for transaction in client.transactions():
    print(transaction)
```

## License

This code is using GraphQL excerpts from the official Monarch web app as the
basis for the queries. There isn't any license on those but they may be
considered fair use as an API. Use at your own risk.

See [LICENSE](LICENSE).
