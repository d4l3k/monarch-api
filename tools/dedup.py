"""
This finds duplicates in Monarch and prints them.
"""
import monarch
import argparse
import asyncio
from collections import defaultdict

parser = argparse.ArgumentParser(description="dedup transactions")
parser.add_argument("--username", required=True)
parser.add_argument("--password", required=True)
parser.add_argument("--totp")
parser.add_argument("--hide", action="store_true", help="hide duplicate transactions")

args = parser.parse_args()

m = monarch.Client.login(
    username=args.username,
    password=args.password,
    totp=args.totp,
)


async def run():
    collisions = {}
    async for t in m.transactions_async():
        if t["hideFromReports"]:
            continue
        date = t["date"]
        amount = t["amount"]
        key = (date, amount)
        if key in collisions:
            ct = collisions[key]
            if (
                ct["plaidName"] == t["plaidName"]
                and ct["merchant"]["name"] != t["merchant"]["name"]
            ):
                if hide:
                    print(
                        f"hiding https://app.monarchmoney.com/transactions/{t['id']} {t['merchant']['name']}"
                    )
                    await m.hide_transaction(t["id"])
                else:
                    print(f"possible collision - {date} {amount}:")
                    print(
                        f"1. https://app.monarchmoney.com/transactions/{ct['id']} {ct['merchant']['name']}"
                    )
                    print(
                        f"2. https://app.monarchmoney.com/transactions/{t['id']} {t['merchant']['name']}"
                    )
                    print(t)
                    print(ct)
                    print()
        else:
            collisions[key] = t


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
