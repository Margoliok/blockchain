import hashlib
import datetime
import tkinter as tk
from tkinter import ttk

# Hash function (manual implementation)
def manual_hash(data):
    # Simple manual hash using sum of character codes and mod operation
    hash_value = 0
    for char in data:
        hash_value = (hash_value + ord(char)) % 256  # Limiting hash to 256
    return hex(hash_value)[2:]

# Block class
class Block:
    def __init__(self, data, previous_hash):
        self.timestamp = datetime.datetime.now()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = f"{self.timestamp}{self.data}{self.previous_hash}"
        return manual_hash(block_data)

# Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block("Genesis Block", "0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(data, previous_block.hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Validate block hash
            if current_block.hash != current_block.calculate_hash():
                return False

            # Validate previous hash link
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

# Blockchain Explorer GUI
class BlockchainExplorer:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.root = tk.Tk()
        self.root.title("Blockchain Explorer")
        self.create_gui()

    def create_gui(self):
        self.tree = ttk.Treeview(self.root, columns=("#1", "#2", "#3", "#4"), show="headings")
        self.tree.heading("#1", text="Block Address")
        self.tree.heading("#2", text="Timestamp")
        self.tree.heading("#3", text="Data")
        self.tree.heading("#4", text="Validation Status")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.update_tree_view()

    def update_tree_view(self):
        for block in self.blockchain.chain:
            validation_status = "Valid" if self.blockchain.is_chain_valid() else "Invalid"
            self.tree.insert("", "end", values=(
                block.hash,
                block.timestamp,
                block.data,
                validation_status,
            ))

    def run(self):
        self.root.mainloop()

# Main script
if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.add_block("Block 1 Data")
    blockchain.add_block("Block 2 Data")
    blockchain.add_block("Block 3 Data")

    explorer = BlockchainExplorer(blockchain)
    explorer.run()
