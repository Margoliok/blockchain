import time
import socket
import json
import threading


# Manual hash function (instead of hashlib)
def manual_hash(data):
    hash_value = 0
    for char in data:
        hash_value = (hash_value * 31 + ord(char)) % (2 ** 32)
    return str(hash_value)


# Transaction class
class Transaction:
    def __init__(self, sender, receiver, amount, timestamp=None, tx_hash=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp if timestamp else time.time()
        self.tx_hash = tx_hash if tx_hash else self.calculate_hash()

    def calculate_hash(self):
        return manual_hash(f"{self.sender}{self.receiver}{self.amount}{self.timestamp}")

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "tx_hash": self.tx_hash
        }


# Merkle Root Calculation
def merkle_root(transaction_hashes):
    if not transaction_hashes:
        return None

    while len(transaction_hashes) > 1:
        if len(transaction_hashes) % 2 == 1:
            transaction_hashes.append(transaction_hashes[-1])
        transaction_hashes = [manual_hash(transaction_hashes[i] + transaction_hashes[i + 1])
                              for i in range(0, len(transaction_hashes), 2)]
    return transaction_hashes[0]


# Block class
class Block:
    def __init__(self, previous_hash, transactions, timestamp=None, merkle_root=None, block_hash=None):
        self.previous_hash = previous_hash
        self.transactions = [Transaction(**tx) if isinstance(tx, dict) else tx for tx in transactions]
        self.timestamp = timestamp if timestamp else time.time()
        self.merkle_root = merkle_root if merkle_root else self.compute_merkle_root()
        self.block_hash = block_hash if block_hash else self.calculate_hash()

    def compute_merkle_root(self):
        return merkle_root([tx.tx_hash for tx in self.transactions])

    def calculate_hash(self):
        return manual_hash(f"{self.previous_hash}{self.merkle_root}{self.timestamp}")

    def to_dict(self):
        return {
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
            "transactions": [tx.to_dict() for tx in self.transactions]
        }


# P2P Networking
class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.transactions = []
        self.blockchain = []
        self.peers = []
        threading.Thread(target=self.start_server).start()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        while True:
            client, _ = server.accept()
            threading.Thread(target=self.handle_connection, args=(client,)).start()

    def handle_connection(self, client):
        try:
            data = client.recv(1024).decode()
            message = json.loads(data)
            if message["type"] == "transaction":
                self.transactions.append(Transaction(**message["data"]))
            elif message["type"] == "block":
                self.blockchain.append(Block(**message["data"]))
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            client.close()

    def send_data(self, peer, data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(peer)
                s.sendall(json.dumps(data).encode())
        except Exception as e:
            print(f"Error sending data: {e}")

    def broadcast_transaction(self, transaction):
        for peer in self.peers:
            self.send_data(peer, {"type": "transaction", "data": transaction.to_dict()})

    def broadcast_block(self, block):
        for peer in self.peers:
            self.send_data(peer, {"type": "block", "data": block.to_dict()})


# Example execution
if __name__ == "__main__":
    node1 = Node("localhost", 5001)
    node2 = Node("localhost", 5002)
    node1.peers.append(("localhost", 5002))
    node2.peers.append(("localhost", 5001))

    tx1 = Transaction("Alice", "Bob", 10)
    node1.broadcast_transaction(tx1)
    time.sleep(1)
    block1 = Block("genesis_hash", [tx1])
    node1.broadcast_block(block1)
    time.sleep(1)
    print("Alice's balance:", 100 - 10)
    print("Bob's balance:", 100 + 10)
