ABI = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "uint256",
          "name": "rentingID",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "uint32",
          "name": "collectedAt",
          "type": "uint32"
        }
      ],
      "name": "RentClaimed",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "enum IRegistry.NFTStandard[]",
          "name": "nftStandard",
          "type": "uint8[]"
        },
        {
          "internalType": "address[]",
          "name": "nftAddress",
          "type": "address[]"
        },
        {
          "internalType": "uint256[]",
          "name": "tokenID",
          "type": "uint256[]"
        },
        {
          "internalType": "uint256[]",
          "name": "_lendingID",
          "type": "uint256[]"
        },
        {
          "internalType": "uint256[]",
          "name": "_rentingID",
          "type": "uint256[]"
        }
      ],
      "name": "claimRent",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
]
