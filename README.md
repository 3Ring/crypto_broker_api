**FinTech Mock API to simulate brokering crypto-currencies to clients and their users**

**Project Specifications:**

- Currency list: For a given User, get the currencies they can transact    
- Buy: For a given User, buy a selected Currency
- Sell: for a given User, sell a selected Currency
- Balances: For a given User, get a list of Balances
- Given Assumptions:
  - The FinTech companies all have a pre-existing relationship with (this program) and have an API key

**Legend:**

- Client = The company consuming the API
- User = The unique account being accessed by the Client

**Assumptions and Personal Specifications:**

- Clients will be responsible for verification of the Users on their side. This means that as long as the token is correct we can provide full access and we do not need to issue temporary keys on a per user basis
- Clients will not share User accounts. Users are unique.
- Current conversion rates will be stored locally and trusted to be up to date
- Buy/Sell orders handled by this API will only pass those orders on and assumes that they will be handled by a different program. These routes will only respond that the order has been successfully submitted for processing.
- User Buy orders will need to have the payment from the Client be deposited before the order can be executed. This will be tracked through the "Transactions" table as a positive usd\_amount.
- User Sell orders will be tracked through the "Transactions" table as a negative usd\_amount.
- the HTTPS encryption will be assumed to be sufficient for the purposes of this project. Another layer of encryption over the data base would be prudent in the real world
- Security measures such as black-listing IPs and revoking API keys will be assumed to be handled in a different area
- For the purposes of this demo:
  - Only 5 currencies are brokered: ["BTC", "ETH", "DOGE", "USDT", "BNB"].
  - All transactions will be using $USD.
  - User/Client accounts do not need to be created or deleted and will be assumed to be handled in a different api.
  - There is an infinite amount of the currencies to be purchased

- Currency list:
  - Since this specifies 'for a given user', I'm not exactly sure how this is different from balances.  I am going to go with the assumption that specific users will have to be preauthorized to trade in specific currencies, so I added an authorization row for each currency to the database.



**Additional Thoughts:**

1. A potential problem could arise if connection is lost mid-request.
   1. This could lead to a mismatch in records. Ways to mitigate this could be through using websockets instead of REST. This would allow for multiple checks back and forth before executing the orders. It could scale more efficiently in this use case as the Clients could have permanent connections that the users funnel through. The downside of this approach is that it would require clients to all have frameworks on their side that can support it.
   1. Another option would be to return a confirmation key(s) and require that the Clients send them to other internal routes to confirm the request. This would add another layer of security, but would also be less efficient
1. Due to the nature of purchasing crypto-currencies each of these purchases would be more of an order or promise. Where we would be saying that we were going to do the transfer for the client, but for it not to be guaranteed until a future date.
   1. This could allow us to use that crypto/currency until then.
   1. I don't have a professional background in finance/banking, so I don't know of the legal implications of this model


