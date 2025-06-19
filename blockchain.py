import hashlib
import time

class Block:
    def __init__(self, index, data, timestamp, previous_hash):
        self.index = index
        self.data = data  # Transaction info (dict)
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        tx = str(self.index) + str(self.data) + str(self.timestamp) + str(self.previous_hash)
        return hashlib.sha256(tx.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, {"info": "Genesis Block"}, time.time(), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            data=data,
            timestamp=time.time(),
            previous_hash=latest.hash
        )
        self.chain.append(new_block)

    def get_chain(self):
        return [vars(block) for block in self.chain]
