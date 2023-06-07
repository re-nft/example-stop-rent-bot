#!/usr/bin/env python
from typing import List
import requests
import traceback
import time
import threading

from web3 import Web3
from web3.middleware.signing import construct_sign_and_send_raw_middleware
from web3.middleware.geth_poa import geth_poa_middleware

from eth_account import Account
from eth_utils.address import to_checksum_address

from bot.abi import ABI
from bot.renting import Renting
from bot import consts
from bot.secrets import get_env_var
from bot.logs import print_verbose
from bot.diskord import run_discord_bot


# * https://web3py.readthedocs.io/en/stable/middleware.html#signing
acct = Account.from_key(get_env_var("PRIVATE_KEY"))
w3 = Web3(Web3.HTTPProvider(get_env_var("PROVIDER_URL")))
# https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
# ! remove POA for non-POA chains, otherwise txns will fail
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(
    address=to_checksum_address(consts.POLYGON_CONTRACT_ADDRESS),
    abi=ABI
)
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
w3.eth.default_account = acct.address


def get_all_rentings() -> List[Renting]:

    raw_rentings: List[consts.SubgraphRenting] = []
    cursor = 0
    query_result = [""]

    query = (
        lambda cursor: (
            """query {
            rentings(first: 1000, where: {expired: false, cursor_gt: """
            + str(int(cursor))
            + """}, orderBy: cursor, orderDirection: asc) {
                id
                cursor
                rentDuration
                rentedAt
                lending {
                    id
                    tokenID
                    nftAddress
                    is721
                }
            }
        }"""
        )
    )


    def get_batch():
        nonlocal raw_rentings, cursor, query_result

        r = requests.post(consts.SUBGRAPH_URL, json={"query": query(cursor)})
        if r.status_code != 200:
            raise Exception(
                "There was a problem with the request. Waiting and re-running."
            )
        query_result = r.json()["data"]["rentings"]
        # one item would look like:
        # {'id': 1, 'cursor': 1, 'rentDuration': '1',
        # 'rentedAt': 1671617899', 'lending': {
        # 'id': 2, 'tokenId': '23123123', 'nftAddress': '0x...',
        # 'is721': False}}
        if len(query_result) > 0:
            cursor = max([int(r["cursor"]) for r in query_result])
            raw_rentings.extend(query_result)

    # * while there are responses from the subgraph get batch:
    while len(query_result) > 0:
        get_batch()

    rentings: List[Renting] = list(map(Renting.to_renting, raw_rentings))

    return rentings


def stop_rentings() -> None:
    rentings = get_all_rentings()
    stopped = 0

    for renting in rentings:
        if renting.should_stop():
            renting.stop(w3, contract)
            stopped += 1
        else:
            continue
            # print_verbose('INFO', f"[INFO] Not stopping yet: {renting}.")

    print_verbose('INFO', f"scanned {len(rentings)} rentings")
    if stopped != 0:
        print_verbose('INFO', f"stopped {stopped} rentings")


def handle_exception() -> None:
    traceback.print_exc()


def main():
    # in case the bot exited due to error previously,
    # we must make sure to stop any rentings that
    # were not stopped previously. For that reason,
    # the first step is to always check, irrespective
    # of the current time, if any rentings should be stopped.

    while True:
        try:
            print_verbose('INFO', "checking if there are any rentings to stop")
            stop_rentings()
            print_verbose('INFO', "sleeping for 1 hour")
        except: 
            handle_exception()
        finally:
            time.sleep(consts.ONE_HOUR_IN_SECONDS)


if __name__ == "__main__":
    try:
        discord_bot_thread = threading.Thread(target=run_discord_bot)
        discord_bot_thread.start()

        main()
    except KeyboardInterrupt:
        print_verbose('INFO', "KeyboardInterrupt caught. Gracefully exiting.")
        exit(0)
    except:
        handle_exception()
        print_verbose('WARNING', "error occured. shutting down.")
        exit(1)
    finally:
        discord_bot_thread.join()
