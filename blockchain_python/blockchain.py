#%%
'''
Filename: blockchain.py
Author: Luke Rouleau
Date Created: 4/27/2021
Last Edit: 4/27/2021
Dependencies: Flask & requests, you'll also need an HTTP client like Postman
Sources:
        https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
        https://flask.palletsprojects.com/en/1.1.x/tutorial/layout/
Purpose: To create basic blockchain in python
'''


import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

# Create a blockchain class to store the chain:
class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set() # create an empty set for the list of nodes (i.e. like the wallets)
                           # stores the netloc portion of the addresses
                           # We use a set as a cheap way to to guarantee only unique addresses

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    # create a new block to add to the chain
    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        
        # Reset the current list of transactions as we have already inserted it in the new block above
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        # return the index of the block which the transaction will be added to, next one mined
        return self.last_block['index'] + 1

    # calculate the POW number to add into the block
    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(p * p') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0 # starting condition of brute force solution
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof


    # This means we are entering another user into our system
    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address) # takes in a url string and it breaks it 
                                       # into an object with all the url components separated.
        self.nodes.add(parsed_url.netloc) # add only the netloc component
        
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        # entry condition for the iteration
        # basically move two pointers down the chain to verify the correctness
        last_block = chain[0]
        current_index = 1
        while(current_index < len(chain)):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # check that the hash of the block is correct
            if(block['previous_hash'] != self.hash(last_block)):
                return False            
            
            # check if the POW is correct too
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """
        neighbours = self.nodes # the other network access points
        new_chain = None

        # only looking for chains that are longer than our own
        max_length = len(self.chain) # grab the length of our personal chain

        # grab and verify the chains from all the other nodes in our network
        for node in neighbours:
            # res stands for response, which is standard syntax for networking like this
            res = requests.get(f'http://{node}/chain') # remember that we stored the neighbors as netlocs 
            # successful request
            if res.status_code == 200:
                length = response.json()['length']  # how long is this node's chain?
                chain = response.json()['chain']    # grab this node's chain

                # check is the length is longer and if the chain is valid
                if length > max_length and self.valid_chain(chain):
                    # whelp, our chain is not it... but maybe there's a bigger fish too, so keep iterating
                    max_length = length
                    new_chain = chain

        # if new_chain is still None type, we won't enter this if():
        if new_chain:
            self.chain = new_chain
            return true

        # our chain was the GOAT   
        return False

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        # I'm using a python f string here to compute the product inside of the string
        guess = f'{last_proof}*{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000" # increasing this size makes a massive in time


    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        # json.dumps(obj) converts a python obj into a json formatted string
        # 
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Return the last block in the chain
        return self.chain[-1]

#%%

# Instantiate a server as a node in our blockchain
app = Flask(__name__,)

# Generate a globally Universially Unique ID address for this node
node_identifier = str(uuid4()).replace('-','')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Run the POW algorithm
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    
    # Receive a reward for finding the proof
    # Sender = '0' tpo signify that this node has mined a new coin
    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1,
    )

    # Forge new block by adding it to the chain
    previous_hash = blockchain.hash(last_block) # grab the hash of the last block
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    print(values)    
    print(type(values))
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    # when we grab the full chain from a node, make the response the chain and append the chain length
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400

    for node in nodes:
        blockchain.register_node(node)

    res = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(res), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts() # this function does all the work (networking included) itself
                                              # and returns True if we had to change our chain to get consensus
    if replaced:
        res = {
            'message': 'Our chain was replaced to reach consensus.'
            'new_chain': blockchain.chain
        }
    else:
        res = {
            'message': 'Our chain is authoritative'
            'chain': blockchain.chain
        }
    return jsonify(res), 200

    

#%%
# Sandbox:
parsed_url = urlparse('http://192.168.0.5:5000')
print(parsed_url)
# %%
new_chain = None
if new_chain:
    print('This is not how I expect it to behave')
else:
    print('This is what I expect')
# %%
