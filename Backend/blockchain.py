import hashlib
import time
import json

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create the genesis block
        self.new_block(proof=100, previous_hash='1')

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, herb_id, herb_name, origin, harvest_date, farmer_id,
                        processor_id="", lab_id="", test_results="", status="harvested"):
        tx = {
            "herb_id": herb_id,
            "herb_name": herb_name,
            "origin": origin,
            "harvest_date": harvest_date,
            "farmer_id": farmer_id,
            "processor_id": processor_id,
            "lab_id": lab_id,
            "test_results": test_results,
            "current_status": status
        }
        self.current_transactions.append(tx)
        return tx  # return the transaction itself for clarity

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
