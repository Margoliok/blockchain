import hashlib
import time
import tkinter as tk
from tkinter import ttk, messagebox
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import json


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


# Generate RSA key pair
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key


# Digital signature function
def sign_data(private_key, data):
    data_bytes = json.dumps(data, sort_keys=True).encode()
    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature.hex()


# Verify signature
def verify_signature(public_key, data, signature):
    data_bytes = json.dumps(data, sort_keys=True).encode()
    try:
        public_key.verify(
            bytes.fromhex(signature),
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False


# Transaction structure
class Transaction:
    def __init__(self, sender, receiver, amount, private_key):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        self.tx_hash = self.calculate_hash()
        self.signature = sign_data(private_key, self.to_dict())

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


# Wallet GUI
class WalletGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blockchain Wallet")

        self.private_key, self.public_key = generate_key_pair()
        self.address = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        tk.Label(self.root, text="Your Wallet Address:").pack()

        # Fix: Separate widget creation, text insertion, and packing
        text_widget = tk.Text(self.root, height=5, width=60)
        text_widget.insert(tk.END, self.address)
        text_widget.pack()

        self.balance_label = tk.Label(self.root, text="Balance: 100")
        self.balance_label.pack()

        tk.Button(self.root, text="Send Transaction", command=self.send_transaction).pack()

    def send_transaction(self):
        receiver = "Bob"
        amount = 30
        transaction = Transaction(self.address, receiver, amount, self.private_key)
        messagebox.showinfo("Transaction Sent", f"Sent {amount} to {receiver}\nTx Hash: {transaction.tx_hash}")

    def run(self):
        self.root.mainloop()


# Main execution
if __name__ == "__main__":
    wallet = WalletGUI()
    wallet.run()
