'''
Filename: blockchain.py
Author: Luke Rouleau
Date Created: 4/27/2021
Last Edit: 4/27/2021
Dependencies: Flask & requests, you'll also need an HTTP client like Postman
Purpose: To create basic blockchain in python
'''

# Create a blockchain class to store the chain:
class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        # Create a new block and add it to the chain
        pass

    def new_transaction(self):
        # Add a new transaction to the list of transactions
        pass

    @staticmethod
    def hash(block):
        # Hashes a block
        pass

    @property
    def last_block(self):
        # Return the last block in the chain
        pass

    

