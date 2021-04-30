# Toy Blockchain
## https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

To use, you will need some sort of HTTP client interfacer like Postman or Curl. I used Postman.

# Create a network of nodes accessing the chain:
to create a network of nodes on the chain, call in the terminal "python blockchain.py 5000" or "python blockchain.py 5001" to create a server on the local host on port 5000 or 5001 respectively. It can be any port, adn you select it via the command line argument. It will not work and it will not throw an error (because Flask is kinda ass) if you create several nodes on the same port, so just don't go there homie.

# Use http requests to interface with the chain:
the requests are : http://localhost:xxxx/mine, http://localhost:xxxx/chain, http://localhost:xxxx/nodes/resolve, http://localhost:xxxx/transactions/new, and http://localhost:xxxx/nodes/register

[GET]  /mine : mines a block by solving the POW and gives the miner a reward amount of 1

[GET]  /chain : returns the whole chain according to the node the request is made from

[GET] /nodes/resolve : call this to resolve any chain conflicts and come to consesus. Must be called from each node independently.

[POST] /transactions/new : prepares a transaction of value "amount" from sender to recipient to be inserted in the next mined block
  use this json format for the request:
  {
    "sender": "uuid",
    "recipient": "uuid",
    "amount": 2
  }
  where uuid is the universally unique identifier for each node in the network (visible in the response from mining a coin from that node).
  This uuid is basically like the "wallet" address. 

[POST] /nodes/register : register a different node on the network. Basically this makes a different node known to the node that makes the request. You have to call this from each node individually if I want to be able to come to consesus from every direction.
  use this json format for the request:
  {
    "nodes": ["http://127.0.0.1:xxxx"]
  }
  
  For example, let's say I have two nodes on ports 5000 and 5001. To be able to check chain length and come to consesus from the 5000 to 5001 or from the 5001 to 5000            
  direction, I have to regitser 5001 with 5000 and 5000 with 5001 by two requests:
  [POST] http://localhost:5000/nodes/register   with JSON input of { "nodes": ["http://127.0.0.1:5001"] } and 
  [POST] http://localhost:5001/nodes/register   with JSON input of { "nodes": ["http://127.0.0.1:5000"] }
  
  
  
  
 # Future work: 
 Transaction Validation Mechanism as well as productionizing your Blockchain so that you don't have to cal everything manually and it becomes a simple-to-use system 
 
 I also want to use Tornado as my Python web server of choice next time. Flask causes many headaches.

  
  
  
