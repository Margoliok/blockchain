import hashlib
import time
import tkinter as tk
from tkinter import ttk


# Utility function to hash data
def hash_data(data):
    return hashlib.sha256(data.encode()).hexdigest()


# Merkle Tree implementation
def merkle_root(transactions):
    if len(transactions) == 0:
        return None
    hashes = [hash_data(tx) for tx in transactions]
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])  # Duplicate last hash if odd count
        hashes = [hash_data(hashes[i] + hashes[i + 1]) for i in range(0, len(hashes), 2)]
    return hashes[0]


# Transaction structure
class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        self.tx_hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hash_data(data)

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "tx_hash": self.tx_hash,
            "timestamp": self.timestamp
        }


# Block structure
class Block:
    def __init__(self, previous_hash, transactions):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.merkle_root = merkle_root([tx.tx_hash for tx in transactions])
        self.timestamp = time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.previous_hash}{self.merkle_root}{self.timestamp}"
        return hash_data(data)

    def to_dict(self):
        return {
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "transactions": [tx.to_dict() for tx in self.transactions]
        }


# UTXO model to track balances
class UTXO:
    def __init__(self):
        self.balances = {}

    def update_balances(self, transactions):
        for tx in transactions:
            self.balances.setdefault(tx.sender, 100)  # Default initial balance
            self.balances.setdefault(tx.receiver, 100)

            if self.balances[tx.sender] < tx.amount:
                return False  # Invalid transaction

            self.balances[tx.sender] -= tx.amount
            self.balances[tx.receiver] += tx.amount

        return True


# Blockchain Explorer GUI
class BlockchainExplorer:
    def __init__(self, blocks):
        self.blocks = blocks
        self.root = tk.Tk()
        self.root.title("Blockchain Explorer")

        self.tree = ttk.Treeview(self.root, columns=("Hash", "Merkle Root", "Transactions"), show="headings")
        self.tree.heading("Hash", text="Block Hash")
        self.tree.heading("Merkle Root", text="Merkle Root")
        self.tree.heading("Transactions", text="Transactions Count")
        self.tree.pack(expand=True, fill="both")

        self.populate_tree()

    def populate_tree(self):
        for block in self.blocks:
            self.tree.insert("", "end", values=(block.hash, block.merkle_root, len(block.transactions)))

    def run(self):
        self.root.mainloop()


# Block validation
def validate_block(block, utxo):
    calculated_merkle = merkle_root([tx.tx_hash for tx in block.transactions])
    if calculated_merkle != block.merkle_root:
        return False, "Invalid Merkle Root"

    if not utxo.update_balances(block.transactions):
        return False, "Invalid Transactions (Negative Balance)"

    return True, "Valid Block"


# Main execution
if __name__ == "__main__":
    # Create transactions
    tx1 = Transaction("Alice", "Bob", 30)
    tx2 = Transaction("Bob", "Charlie", 20)
    tx3 = Transaction("Charlie", "Dave", 50)

    # Validate transactions and create block
    utxo = UTXO()
    transactions = [tx1, tx2, tx3]

    if utxo.update_balances(transactions):
        block1 = Block("previous_block_hash", transactions)
        print(block1.to_dict())

        # Launch GUI Explorer
        explorer = BlockchainExplorer([block1])
        explorer.run()
    else:
        print("Invalid Transactions")
