# Example Bot To Stop Rentals On-Chain

This bot works on our EVM collateral free v1 contract on polygon. You can find
the contract [here](https://polygonscan.com/address/0x4e52b73aa28b7ff84d88ea3a90c0668f46043450).

If the renter does not execute the "stopRent" on our dapp, we are able to
terminate the rental ourselves with the help of the following utility function
on the smart contract:

```solidity
function handleClaimRent(CallData memory cd) private {
    for (uint256 i = cd.left; i < cd.right; i++) {
        bytes32 lendingIdentifier =
            keccak256(abi.encodePacked(cd.nftAddress[cd.left], cd.tokenID[i], cd.lendingID[i]));
        bytes32 rentingIdentifier =
            keccak256(abi.encodePacked(cd.nftAddress[cd.left], cd.tokenID[i], cd.rentingID[i]));
        IRegistry.Lending storage lending = lendings[lendingIdentifier];
        IRegistry.Renting storage renting = rentings[rentingIdentifier];
        ensureIsNotNull(lending);
        ensureIsNotNull(renting);
        ensureIsClaimable(renting, block.timestamp);
        distributeClaimPayment(lending, renting);
        manageWillAutoRenew(
            lending, renting, cd.nftAddress[cd.left], cd.nftStandard[cd.left], cd.tokenID[i], cd.lendingID[i]
        );
        emit IRegistry.RentClaimed(cd.rentingID[i], uint32(block.timestamp));
        delete rentings[rentingIdentifier];
    }
}
```

notice, that, to be able to perform this, we need:

- `ensureIsNotNull(lending)`
- `ensureIsNotNull(renting)`
- `ensureIsClaimable(renting, block.timestamp)`

we are only concerned with the last bullet point. And it will be the case
if the rental runs overdue. This function allows anyone to stop an overdue
rental. In fact, this might be a mechanic in the future to incentivise people
doing it for us. Similar to how aave liquidations can be triggered by anyone.

## Implementation Details

It's a simple python script that runs on our AWS ECS.

It will log the rentals it wants to stop and stops into our corporate discord
channel.

### Development

The discord token id is taken from discord developer portal. You first create
an application there, then create a bot. Then generate an invite link for the
bot to join your discord server. If you have private and public channels, you
might need to give your bot a role so that it can see the private channels.

### Deployment

If running inside of a container on EC2, ensure that the IAM role:

- has permissions to read secrets
- has permissions to pull ecr image
