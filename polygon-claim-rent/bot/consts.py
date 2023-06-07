from typing import Dict, Any


POLYGON_CONTRACT_ADDRESS = "0x4e52B73Aa28b7FF84d88eA3A90C0668f46043450"
SUBGRAPH_URL = (
        "https://api.thegraph.com/subgraphs/name"
        "/re-nft/sylvester-v1-polygon-main"
)

ONE_MINUTE_IN_SECONDS = 60
ONE_HOUR_IN_SECONDS = 60 * ONE_MINUTE_IN_SECONDS
ONE_DAY_IN_SECONDS = ONE_HOUR_IN_SECONDS * 24
ID_SEPARATOR = "::"

# raw renting looks like the following
# type Renting @entity {
#   id: ID! < f"{lending_id}::{token_id}::{block.timestamp}::{log_index_offset}"
#   renterAddress: Bytes!
#   rentDuration: BigInt!
#   rentedAt: BigInt!
#   expired: Boolean!
# }
SubgraphRenting = Dict[str, Any]
