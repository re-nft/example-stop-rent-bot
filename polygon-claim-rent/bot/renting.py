from datetime import datetime, timezone
from typing import Union, Type
from dataclasses import dataclass
from eth_utils.address import to_checksum_address

from web3 import Web3
from web3.types import TxParams, Wei
from web3.contract import Contract

from bot import consts
from bot.diskord import add_message_to_notify
from bot.logs import print_verbose


@dataclass(frozen=True)
class Renting:
    token_id: int
    lending_id: int
    renting_id: int
    nft_address: str
    is_721: bool

    # - With this information we can decide if we should
    # stop the renting -
    rent_start_timestamp_utc: int
    rent_duration: int  # how many days

    def __repr__(self):
        return (
            f"Renting(token_id={self.token_id!r},"
            f"lending_id={self.lending_id!r},"
            f"renting_id={self.renting_id!r},"
            f"nft_address={self.nft_address!r},"
            f"is_721={self.is_721},"
            f"rent_start_timestamp_utc={self.rent_start_timestamp_utc!r},"
            f"rent_duration={self.rent_duration!r})"#, {self.nft_address!r})"
        )

    # should we stop this renting?
    def should_stop(self) -> bool:
        stop_timestamp_utc = (self.rent_start_timestamp_utc +
                              self.rent_duration * consts.ONE_DAY_IN_SECONDS)
        now_timestamp_utc = datetime.now(timezone.utc).timestamp()

        if now_timestamp_utc > stop_timestamp_utc:
            return True

        return False

    def stop(
        self, w3: Union[Type[Web3], Web3], contract: Union[Type[Contract], Contract]
    ) -> None:
        if not self.should_stop():
            raise Exception(f"Shouldn't stop {self} renting.")

        latest_block = w3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas", None)
        if base_fee is None:
            # better restart the bot than come up with your own base fee
            # which may be completely incorrect and will stall the whole
            # pipeline of transactions
            raise Exception("cannot determine base fee") 
        max_fee_per_gas = int(base_fee * 1.5)  # up to 50% more expensive than base fee

        print_verbose('INFO', 
            (
                f"stopping: {self} with [max_fee_per_gas]:"
                f" {max_fee_per_gas}"
            )
        )

        txn_params: TxParams = {
            # "gas": 500_000,
            "maxFeePerGas": Wei(max_fee_per_gas),
        }

        txn_hash = contract.functions.claimRent(
            [0 if self.is_721 else 1],
            [self.nft_address],
            [self.token_id],
            [self.lending_id],
            [self.renting_id]
        ).transact(txn_params)

        print_verbose('INFO', f"waiting for txn to be mined: {txn_hash.hex()}")
        w3.eth.wait_for_transaction_receipt(txn_hash)
        msg = f"🩸stopped:{self}|https://polygonscan.com/tx/{txn_hash.hex()}"
        print_verbose('INFO', msg)
        add_message_to_notify(msg)

    # converts from subgraph json to Renting
    @classmethod
    def to_renting(cls, raw_renting: consts.SubgraphRenting) -> "Renting":
        return cls(
            token_id=int(raw_renting["lending"]["tokenID"]),
            lending_id=int(raw_renting["lending"]["id"]),
            renting_id=int(raw_renting["id"]),
            is_721=bool(raw_renting["lending"]["is721"]),
            nft_address=to_checksum_address(str(raw_renting["lending"]["nftAddress"])),
            rent_start_timestamp_utc=int(raw_renting["rentedAt"]),
            rent_duration=int(raw_renting["rentDuration"]),
        )

# to claim rent we need the following inputs
#     IRegistry.NFTStandard[] memory nftStandard,
#     address[] memory nftAddress,
#     uint256[] memory tokenID,
#     uint256[] memory _lendingID,
#     uint256[] memory _rentingID
