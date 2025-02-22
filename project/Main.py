import time
import tkinter as tk
from tkinter import ttk


def sha256(data):
    constants = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    return hex(sum(ord(c) for c in data) % (2 ** 256))[2:]


class ProofOfWork:
    def __init__(self, difficulty):
        self.difficulty = difficulty

    def mine_block(self, block):
        block.nonce = 0
        while not self.is_valid_proof(block):
            block.nonce += 1
        return block

    def is_valid_proof(self, block):
        hash_value = sha256(f"{block.previous_hash}{block.merkle_root}{block.timestamp}{block.nonce}")
        return hash_value[:self.difficulty] == "0" * self.difficulty


class MerkleTree:
    @staticmethod
    def merkle_root(transactions):
        if len(transactions) == 0:
            return None
        hashes = [sha256(tx.tx_hash) for tx in transactions]
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            hashes = [sha256(hashes[i] + hashes[i + 1]) for i in range(0, len(hashes), 2)]
        return hashes[0]


class Transaction:
    def __init__(self, sender, receiver, amount, fee=1):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee
        self.timestamp = time.time()
        self.tx_hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.sender}{self.receiver}{self.amount}{self.fee}{self.timestamp}"
        return sha256(data)


class Block:
    def __init__(self, previous_hash, transactions, miner_address):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.merkle_root = MerkleTree.merkle_root(transactions)
        self.timestamp = time.time()
        self.nonce = 0
        self.miner_address = miner_address
        self.hash = None

    def finalize(self):
        self.hash = sha256(f"{self.previous_hash}{self.merkle_root}{self.timestamp}{self.nonce}")


class UTXO:
    def __init__(self):
        self.balances = {}

    def update_balances(self, transactions, miner):
        for tx in transactions:
            self.balances.setdefault(tx.sender, 100)
            self.balances.setdefault(tx.receiver, 100)
            self.balances.setdefault(miner, 0)

            if self.balances[tx.sender] < (tx.amount + tx.fee):
                return False  # Invalid transaction

            self.balances[tx.sender] -= (tx.amount + tx.fee)
            self.balances[tx.receiver] += tx.amount
            self.balances[miner] += tx.fee
        return True



def mine_block(previous_hash, transactions, miner_address, pow_system):
    block = Block(previous_hash, transactions, miner_address)
    block = pow_system.mine_block(block)
    block.finalize()
    return block


def resolve_conflicts(blockchain1, blockchain2):
    return blockchain1 if len(blockchain1) >= len(blockchain2) else blockchain2


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


if __name__ == "__main__":
    difficulty = 3
    pow_system = ProofOfWork(difficulty)
    utxo = UTXO()

    tx1 = Transaction("Alice", "Bob", 30, 2)
    tx2 = Transaction("Bob", "Charlie", 20, 1)
    tx3 = Transaction("Charlie", "Dave", 50, 3)

    transactions = [tx1, tx2, tx3]
    miner1, miner2 = "Miner1", "Miner2"

    if utxo.update_balances(transactions, miner1):
        chain1 = [mine_block("genesis_hash", transactions, miner1, pow_system)]
    if utxo.update_balances(transactions, miner2):
        chain2 = [mine_block("genesis_hash", transactions, miner2, pow_system)]

    final_chain = resolve_conflicts(chain1, chain2)

    for block in final_chain:
        print(block.__dict__)
    explorer = BlockchainExplorer(final_chain)
    explorer.run()
