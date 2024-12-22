Exchange endpoint

The exchange endpoint is used to interact with and trade on the Hyperliquid chain. See the Python SDK for code to generate signatures for these requests.

Many of the requests take asset as an input. For perpetuals this is the index in the universe field returned by themeta response. For spot assets, use 10000 + index where index is the corresponding index in spotMeta.universe. For example, when submitting an order for PURR/USDC, the asset that should be used is 10000 because its asset index in the spot metadata is 0.
Place an order

POST https://api.hyperliquid.xyz/exchange

See Python SDK for full featured examples on the fields of the order request.

For limit orders, TIF (time-in-force) sets the behavior of the order upon first hitting the book.

ALO (add liquidity only, i.e. "post only") will be canceled instead of immediately matching.

IOC (immediate or cancel) will have the unfilled part canceled instead of resting.

GTC (good til canceled) orders have no special behavior.

Client Order ID (cloid) is an optional 128 bit hex string, e.g. 0x1234567890abcdef1234567890abcdef

Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "order",
  "orders": [{

    "a": Number,

    "b": Boolean,

    "p": String,

    "s": String,

    "r": Boolean,

    "t": {

      "limit": {

        "tif": "Alo" | "Ioc" | "Gtc" 

      } or

      "trigger": {

         "isMarket": Boolean,

         "triggerPx": String,

         "tpsl": "tp" | "sl"

       }

    },

    "c": Cloid (optional)

  }],

  "grouping": "na" | "normalTpsl" | "positionTpsl",

  "builder": Optional({"b": "address", "f": Number})

}

Meaning of keys:
a is asset
b is isBuy
p is price
s is size
r is reduceOnly
t is type
c is cloid (client order id)

Meaning of keys in optional builder argument:
b is the address the should receive the additional fee
f is the size of the fee in tenths of a basis point e.g. if f is 10, 1bp of the order notional  will be charged to the user and sent to the builder

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its Onchain address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

{
   "status":"ok",
   "response":{
      "type":"order",
      "data":{
         "statuses":[
            {
               "resting":{
                  "oid":77738308
               }
            }
         ]
      }
   }
}

Cancel order(s)

POST https://api.hyperliquid.xyz/exchange
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "cancel",

  "cancels": [

    {

      "a": Number,

      "o": Number

    }

  ]

}

Meaning of keys:
a is asset
o is oid (order id)

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

{
   "status":"ok",
   "response":{
      "type":"cancel",
      "data":{
         "statuses":[
            "success"
         ]
      }
   }
}

Cancel order(s) by cloid

POST https://api.hyperliquid.xyz/exchange 
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "cancelByCloid",

  "cancels": [

    {

      "asset": Number,

      "cloid": String

    }

  ]

}

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

Schedule Cancel (dead man's switch)

POST https://api.hyperliquid.xyz/exchange 

{"type": "scheduleCancel", "time": <unix milliseconds> | null}

Schedule a cancel-all operation at a future time. Setting time to null will remove any outstanding scheduled cancel operation.
Modify an order

POST https://api.hyperliquid.xyz/exchange  
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "modify",

  "oid": Number | Cloid,

  "order": {

    "a": Number,

    "b": Boolean,

    "p": String,

    "s": String,

    "r": Boolean,

    "t": {

      "limit": {

        "tif": "Alo" | "Ioc" | "Gtc" 

      } or

      "trigger": {

         "isMarket": Boolean,

         "triggerPx": String,

         "tpsl": "tp" | "sl"

       }

    },

    "c": Cloid (optional)

  }

}

Meaning of keys:
a is asset
b is isBuy
p is price
s is size
r is reduceOnly
t is type
c is cloid (client order id)

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its Onchain address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

Modify multiple orders

POST https://api.hyperliquid.xyz/exchange
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "batchModify",

  "modifies": [

    "oid": Number | Cloid,

    "order": {

      "a": Number,

      "b": Boolean,

      "p": String,

      "s": String,

      "r": Boolean,

      "t": {

        "limit": {

          "tif": "Alo" | "Ioc" | "Gtc" 

        } or

        "trigger": {

           "isMarket": Boolean,

           "triggerPx": String,

           "tpsl": "tp" | "sl"

         }

      },

      "c": Cloid (optional)

  }]

}

Meaning of keys:
a is asset
b is isBuy
p is price
s is size
r is reduceOnly
t is type
c is cloid (client order id)

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its Onchain address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000
Update leverage

POST https://api.hyperliquid.xyz/exchange

Update cross or isolated leverage on a coin. 
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "updateLeverage",

  "asset": index of coin,

  "isCross": true or false if updating cross-leverage,

  "leverage": integer representing new leverage, subject to leverage constraints on that coin

}

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its Onchain address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

{'status': 'ok', 'response': {'type': 'default'}}

Update isolated margin

POST https://api.hyperliquid.xyz/exchange

Add or remove margin from isolated position

Note that to target a specific leverage instead of a USDC value of margin change, there is an alternate action {"type": "topUpIsolatedOnlyMargin", "asset": <asset>, "leverage": <float string>}
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "updateIsolatedMargin",

  "asset": index of coin,

  "isBuy": true, (this parameter won't have any effect until hedge mode is introduced)

  "ntli": float representing amount to add or remove,

}

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its Onchain address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

{'status': 'ok', 'response': {'type': 'default'}}

L1 USDC transfer

POST https://api.hyperliquid.xyz/exchange

Send usd to another address. This transfer does not touch the EVM bridge. The signature format is human readable for wallet interfaces.
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "usdSend",

  "hyperliquidChain": "Mainnet" (on testnet use "Testnet" instead),
  "signatureChainId": the id of the chain used when signing in hexadecimal format; e.g. "0xa4b1" for Arbitrum,

  "destination": address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000,

   "amount": amount of usd to send as a string, e.g. "1" for 1 usd,

     "time": current timestamp in milliseconds as a Number, should match nonce

}

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

{'status': 'ok', 'response': {'type': 'default'}}

L1 spot transfer

POST https://api.hyperliquid.xyz/exchange

Send spot assets to another address. This transfer does not touch the EVM bridge. The signature format is human readable for wallet interfaces.
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "spotSend",

  "hyperliquidChain": "Mainnet" (on testnet use "Testnet" instead),
  "signatureChainId": the id of the chain used when signing in hexadecimal format; e.g. "0xa4b1" for Arbitrum,

  "destination": address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000,
  "token": tokenName:tokenId, e.g. "PURR:0xc4bf3f870c0e9465323c0b6ed28096c2"

   "amount": amount of token to send as a string, e.g. "0.01",

     "time": current timestamp in milliseconds as a Number, should match nonce

}

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

{'status': 'ok', 'response': {'type': 'default'}}

Example sign typed data for generating the signature:
{
  "types": {
    "HyperliquidTransaction:SpotSend": [
      {
        "name": "hyperliquidChain",
        "type": "string"
      },
      {
        "name": "destination",
        "type": "string"
      },
      {
        "name": "token",
        "type": "string"
      },
      {
        "name": "amount",
        "type": "string"
      },
      {
        "name": "time",
        "type": "uint64"
      }
    ]
  },
  "primaryType": "HyperliquidTransaction:SpotSend",
  "domain": {
    "name": "HyperliquidSignTransaction",
    "version": "1",
    "chainId": 42161,
    "verifyingContract": "0x0000000000000000000000000000000000000000"
  },
  "message": {
    "destination": "0x0000000000000000000000000000000000000000",
    "token": "PURR:0xc1fb593aeffbeb02f85e0308e9956a90",
    "amount": "0.1",
    "time": 1716531066415,
    "hyperliquidChain": "Mainnet"
  }
}

Initiate a Withdrawal Request

POST https://api.hyperliquid.xyz/exchange

This method is used to initiate the withdrawal flow. After making this request, the L1 validators will sign and send the withdrawal request to the bridge contract. There is a $1 fee for withdrawing at the time of this writing and withdrawals take approximately 5 minutes to finalize.
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{
  "type": "withdraw3",

  "hyperliquidChain": "Mainnet" (on testnet use "Testnet" instead),
  "signatureChainId": the id of the chain used when signing in hexadecimal format; e.g. "0xa4b1" for Arbitrum,

  "amount": amount of usd to send as a string, e.g. "1" for 1 usd,

  "time": current timestamp in milliseconds as a Number, should match nonce,

  "destination": address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

}

nonce*

Number

Recommended to use the current timestamp in milliseconds, must match the nonce in the action Object above

signature*

Object

{'status': 'ok', 'response': {'type': 'default'}}

Transfer from Spot account to Perp account (and vice versa)

POST https://api.hyperliquid.xyz/exchange

This method is used to transfer USDC from the user's spot wallet to perp wallet and vice versa.

Headers
Name
Value

Content-Type*

"application/json"

Body
Name
Type
Description

action*

Object

{

  "type": "usdClassTransfer",

  "hyperliquidChain": "Mainnet" (on testnet use "Testnet" instead),
  "signatureChainId": the id of the chain used when signing in hexadecimal format; e.g. "0xa4b1" for Arbitrum,

 "amount": amount of usd to tranfer as a string, e.g. "1" for 1 usd. If you want to use this action for a subaccount, you can include subaccount: address after the amount, e.g. "1 subaccount:0x0000000000000000000000000000000000000000,

  "toPerp": True if (spot -> perp) else False,

"nonce": current timestamp in milliseconds as a Number, must match nonce in outer request body

}

nonce*

Number

Recommended to use the current timestamp in milliseconds, must match the nonce in the action Object above

signature*

Object

Response

{'status': 'ok', 'response': {'type': 'default'}}

Deposit or Withdraw from a Vault

POST https://api.hyperliquid.xyz/exchange

Add or remove funds from a vault.

Headers
Name
Value

Content-Type*

application/json

Body
Name
Type
Description

action*

Object

{

  "type": "vaultTransfer",

  "vaultAddress": address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000,
"isDeposit": boolean,

"usd": number

}

nonce*

number

Recommended to use the current timestamp in milliseconds

signature*

Object

Response

{'status': 'ok', 'response': {'type': 'default'}}

Approve an API Wallet

POST https://api.hyperliquid.xyz/exchange

Approves an API Wallet (also sometimes referred to as an Agent Wallet). See here for more details.

Headers
Name
Value

Content-Type*

application/json

Body
Name
Type
Description

action*

Object

{
  "type": "approveAgent",

  "hyperliquidChain": "Mainnet" (on testnet use "Testnet" instead),
  "signatureChainId": the id of the chain used when signing in hexadecimal format; e.g. "0xa4b1" for Arbitrum,

  "agentAddress": address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000,

"agentName": Optional name for the API wallet. An account can have 1 unnamed approved wallet and up to 3 named ones. And additional 2 named agents are allowed per subaccount,

  "nonce": current timestamp in milliseconds as a Number, must match nonce in outer request body

}

nonce*

number

Recommended to use the current timestamp in milliseconds

signature*

Object

Response

{'status': 'ok', 'response': {'type': 'default'}}

Approve a Builder Fee

POST https://api.hyperliquid.xyz/exchange

Approve a maximum fee rate for a builder.

Headers
Name
Value

Content-Type*

application/json

Body
Name
Type
Description

action*

Object

{
  "type": "approveBuilderFee",

  "hyperliquidChain": "Mainnet" (on testnet use "Testnet" instead),
  "signatureChainId": the id of the chain used when signing in hexadecimal format; e.g. "0xa4b1" for Arbitrum,

  "maxFeeRate": the maximum allowed builder fee rate as a percent string; e.g. "0.001%",

  "builder": address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000,

  "nonce": current timestamp in milliseconds as a Number, must match nonce in outer request body

}

nonce*

number

Recommended to use the current timestamp in milliseconds

signature*

Object

Response

{'status': 'ok', 'response': {'type': 'default'}}

Place a TWAP order

POST https://api.hyperliquid.xyz/exchange
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "twapOrder",
  "twap": {

    "a": Number,

    "b": Boolean,

    "s": String,

    "r": Boolean,

    "m": Number,

    "t": Boolean

  }

  }

Meaning of keys:
a is asset
b is isBuy
s is size
r is reduceOnly

m is minutes
t is randomize

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its Onchain address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

{
   "status":"ok",
   "response":{
      "type":"twapOrder",
      "data":{
         "status": {
            "running":{
               "twapId":77738308
            }
         }
      }
   }
}

Cancel a TWAP order

POST https://api.hyperliquid.xyz/exchange
Headers
Name
Type
Description

Content-Type*

String

"application/json"
Request Body
Name
Type
Description

action*

Object

{

  "type": "twapCancel",

   "a": Number,

   "t": Number

}

Meaning of keys:
a is asset
t is twap_id

nonce*

Number

Recommended to use the current timestamp in milliseconds

signature*

Object

vaultAddress

String

If trading on behalf of a vault, its address in 42-character hexadecimal format; e.g. 0x0000000000000000000000000000000000000000

{
   "status":"ok",
   "response":{
      "type":"twapCancel",
      "data":{
         "status": "success"
      }
   }
}

Nonces and API Wallets
Background 

A decentralized L1 must prevent replay attacks. When a user signs a USDC transfer transaction, the receiver cannot broadcast it multiple times to drain the sender's wallet. To solve this Ethereum stores a "nonce" for each address, which is a number that starts at 0. Each transaction must use exactly "nonce + 1" to be included.
API Wallets

These are also known as agent wallets in the docs. A master account can approve API wallets to sign on behalf of the master account or any of the sub-accounts. 

Note that API wallets are only used to sign. To query the account data associated with a master or sub-account, you must pass in the actual address of that account. A common pitfall is to use the agent wallet which leads to an empty result.
API Wallet Pruning

API wallets and their associated nonce state may be pruned in the following cases:

    The wallet is deregistered. This happens to an existing unnamed API Wallet when an ApproveAgent action is sent to register a new unnamed API Wallet. This also happens to an existing named API Wallet when an ApproveAgent action is sent with a matching name.

    The wallet expires.

    The account that registered the agent no longer has funds.

Important: for those using API wallets programmatically, it is strongly suggested to not reuse their addresses. Once an agent is deregistered, its used nonce state may be pruned from the L1. Generate a new agent wallet on future use to avoid unexpected behavior. For example, previously signed actions can be replayed once the nonce set is pruned.
Hyperliquid L1 nonces 

Ethereum's design does not work for an onchain order book. A market making strategy can send thousands of orders and cancels in a second. Requiring a precise ordering of inclusion on the L1 will break any strategy.

On the Hyperliquid L1, the 20 highest nonces are stored per address. One additional nonce is stored per 1M USDC cumulative volume, up to a maximum of 100 nonces. Every new transaction must have nonce larger than the smallest nonce in this set and also never have been used before. Nonces are tracked per signer, which is the user address if signed with private key of the address, or the agent address if signed with an API wallet. 

Nonces must be within 1 day of the unix millisecond timestamp on the L1 block of the transaction.

The following steps may help port over an automated strategy from a centralized exchange:

    Use a API wallet per trading process. Note that nonces are stored per signer (i.e. private key), so separate subaccounts signed by the same API wallet will share the nonce tracker of the API wallet. It's recommended to use separate API wallets for different subaccounts.

    In each trading process, have a task that periodically batches order and cancel requests every 0.1 seconds. It is recommended to batch IOC and GTC orders separately from ALO orders because ALO order-only batches are prioritized by the validators.

    The trading logic tasks send orders and cancels to the batching task.

    For each batch of orders or cancels, fetch and increment an atomic counter that ensures a unique nonce for the address. The atomic counter can be fast-forwarded to current unix milliseconds if needed.

This structure is robust to out-of-order transactions within 2 seconds, which should be sufficient for an automated strategy geographically near an API server.
Suggestions for subaccount and vault users

Note that nonces are stored per signer, which is the address of the private key used to sign the transaction. Therefore, it's recommended that each trading process or frontend session use a separate private key for signing. In particular, a single API wallet signing for a user, vault, or subaccount all share the same nonce set.

If users want to use multiple subaccounts in parallel, it would easier to generate two separate API wallets under the master account, and use one API wallet for each subaccount. This avoids collisions between the nonce set used by each subaccount.

