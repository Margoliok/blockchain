import sys
from web3 import Web3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)


class SepoliaWalletApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Connect to Sepolia Network through Infura or Alchemy endpoint
        self.infura_url = 'https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID'
        self.web3 = Web3(Web3.HTTPProvider(self.infura_url))
        self.account = None

    def initUI(self):
        self.setWindowTitle("Sepolia Wallet Interaction")

        # Wallet address display
        self.address_label = QLabel("Wallet Address:")
        self.balance_label = QLabel("Balance: ")

        # Private key input
        self.private_key_input = QLineEdit(self)
        self.private_key_input.setPlaceholderText("Enter Private Key")

        # Connect button
        self.connect_btn = QPushButton("Connect Wallet", self)
        self.connect_btn.clicked.connect(self.connect_wallet)

        # Recipient and amount input
        self.recipient_input = QLineEdit(self)
        self.recipient_input.setPlaceholderText("Recipient Address")

        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Amount in ETH")

        # Send transaction button
        self.send_btn = QPushButton("Send ETH", self)
        self.send_btn.clicked.connect(self.send_transaction)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.address_label)
        layout.addWidget(self.balance_label)
        layout.addWidget(self.private_key_input)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.recipient_input)
        layout.addWidget(self.amount_input)
        layout.addWidget(self.send_btn)

        self.setLayout(layout)
        self.show()

    def connect_wallet(self):
        private_key = self.private_key_input.text().strip()
        if not private_key:
            QMessageBox.warning(self, "Error", "Please enter your private key.")
            return
        try:
            self.account = self.web3.eth.account.from_key(private_key)
            address = self.account.address
            balance_wei = self.web3.eth.get_balance(address)
            balance_eth = self.web3.fromWei(balance_wei, 'ether')
            self.address_label.setText(f"Wallet Address: {address}")
            self.balance_label.setText(f"Balance: {balance_eth} ETH")
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))

    def send_transaction(self):
        if not self.account:
            QMessageBox.warning(self, "Error", "Please connect your wallet first.")
            return

        recipient = self.recipient_input.text().strip()
        amount_eth = self.amount_input.text().strip()

        if not recipient or not amount_eth:
            QMessageBox.warning(self, "Error", "Please enter recipient and amount.")
            return

        try:
            nonce = self.web3.eth.getTransactionCount(self.account.address)
            tx = {
                'nonce': nonce,
                'to': recipient,
                'value': self.web3.toWei(amount_eth, 'ether'),
                'gas': 21000,
                'gasPrice': self.web3.toWei('10', 'gwei')
            }
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            QMessageBox.information(self, "Transaction Sent", f"Transaction Hash: {self.web3.toHex(tx_hash)}")
        except Exception as e:
            QMessageBox.critical(self, "Transaction Failed", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SepoliaWalletApp()
    sys.exit(app.exec_())
