import requests
import os
import bitcoinlib
from electrum.plugin import BasePlugin, hook
from electrum.bitcoin import is_address
from electrum.i18n import _
from electrum.gui.qt.util import WindowModalDialog, EnterButton
from electrum.gui.qt.main_window import ElectrumWindow
from electrum.wallet import InternalAddressCorruption
from electrum.transaction import PartialTxOutput
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QWidget, QTabWidget, QInputDialog, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class BalanceFetcher(QThread):
    balancesFetched = pyqtSignal(str, float, float)

    def __init__(self, address):
        super().__init__()
        self.address = address

    def run(self):
        balance_stx, balance_sBTC = self.get_balance(self.address)
        self.balancesFetched.emit(self.address, balance_stx, balance_sBTC)


    def get_balance(self, address):
        print(address)
        try:
            url = "https://testnet.stx.eco/bridge-api/testnet/v1/sbtc/address/balances"
            payload = {
                "stxAddress": address
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            balance_stx = float(data["stacksTokenInfo"]["stx"]["balance"])
            balance_sBTC = float(data["sBTCBalance"])
            return balance_stx, balance_sBTC
        except Exception as e:
            print(f"Failed to fetch balance for address {address}: {e}")
            return 0, 0


class Plugin(BasePlugin):
    def __init__(self, parent, config, name):
        super().__init__(parent, config, name)

    @hook
    def load_wallet(self, wallet, window):
        sbtc_tab = SBTC_Tab(window)
        window.tabs.addTab(sbtc_tab, "sBTC")

class SBTC_Tab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.fetchers = []
        self.balance_btc = {}  # Dictionary to store BTC balances for addresses

        layout = QVBoxLayout(self)
        tab_widget = QTabWidget()

        deposit_tab = self.create_deposit_tab(window)
        reclaim_deposit_tab = self.create_reclaim_deposit_tab(window)
        reveal_deposit_tab = self.create_reveal_deposit_tab(window)  
        withdraw_tab = self.create_withdraw_tab(window)
        reclaim_withdrawal_tab = self.create_reclaim_withdrawal_tab(window) 
        reveal_withdrawal_tab = self.create_reveal_withdrawal_tab(window) 
        summary_tab = self.create_summary_tab(window)
        tx_history_tab = self.create_tx_history_tab(window)

        tab_widget.addTab(deposit_tab, "Deposit")
        tab_widget.addTab(reclaim_deposit_tab, "Reclaim Deposit")  
        tab_widget.addTab(reveal_deposit_tab, "Reveal Deposit")  
        tab_widget.addTab(withdraw_tab, "Withdraw")
        tab_widget.addTab(reclaim_withdrawal_tab, "Reclaim Withdrawal")
        tab_widget.addTab(reveal_withdrawal_tab, "Reveal Withdrawal")
        tab_widget.addTab(summary_tab, "Summary")
        tab_widget.addTab(tx_history_tab, "Tx History")

        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def create_deposit_tab(self, window):
        # This function creates the interface for the new "Send BTC" tab.
        widget = WindowModalDialog(window, _('Send BTC'))  # Create a new dialog window
        widget.setWindowFlags(widget.windowFlags() & ~Qt.Dialog)  # Set the window flags
        vbox = QVBoxLayout(widget)  # Create a new vertical box layout

        # Create the interface elements for the send tab
        vbox.addWidget(QLabel(_("Amount (BTC):")))  
        self.amount_input = QLineEdit() 
        vbox.addWidget(self.amount_input)

        vbox.addWidget(QLabel(_("Associated STX Address:")))
        self.stx_address_input = QLineEdit()
        vbox.addWidget(self.stx_address_input)

        vbox.addWidget(QLabel(_("My BTC wallet:")))
        self.btc_wallet_address_label = QLabel()
        vbox.addWidget(self.btc_wallet_address_label)

        vbox.addWidget(QLabel(_("sBTC wallet:")))
        self.wallet_address_label = QLabel()
        vbox.addWidget(self.wallet_address_label)

        vbox.addWidget(QLabel(_("Recipient Address:")))
        self.address_input = QLineEdit()
        vbox.addWidget(self.address_input)

        vbox.addWidget(QLabel(_("Transaction Fee (BTC):")))
        self.fee_label = QLabel()  # Create the fee label
        vbox.addWidget(self.fee_label)  # Add the fee label to the layout

        # Create a combo box for fee selection
        self.fee_combo = QComboBox()
        vbox.addWidget(self.fee_combo)

        send_button = EnterButton(_('Deposit BTC'), lambda: self.prompt_password(window))  # Create the send button
        vbox.addWidget(send_button)

        # Fetch fee estimates and populate the combo box
        fee_estimates = self.fetch_fee_estimates()
        if fee_estimates:
            fee_options = [
                f"Low: {fee_estimates['low_fee_per_kb'] / 1e8} BTC",
                f"Medium: {fee_estimates['medium_fee_per_kb'] / 1e8} BTC",
                f"High: {fee_estimates['high_fee_per_kb'] / 1e8} BTC"
            ]
            self.fee_combo.addItems(fee_options)

        # Fetch and display the sBTC wallet address
        wallet_address = self.fetch_sbtc_wallet_address()
        self.wallet_address_label.setText(wallet_address)

        btc_wallet_address = self.fetch_btc_wallet_address(window)
        self.btc_wallet_address_label.setText(btc_wallet_address)

        self.fetch_and_store_keys()

        self.create_script()


        widget.setLayout(vbox)
        return widget

    def create_script(self):
        data = self.buildData(self.pegInData.stacksAddress, True)
        stacks_address = self.stx_address_input.text()
        reveal_pub_key = bitcoinlib.hex.decode(self.reveal_pub_key)
        reclaim_pub_key = bitcoinlib.hex.decode(self.reclaim_pub_key)

        # Build the script for the first case
        script1 = [
            data,
            'DROP',
            bitcoinlib.hex.decode(reveal_pub_key),
            'CHECKSIG'
        ]
        script1_encoded = bitcoinlib.Script.encode(script1)
        print(script1_encoded)

        # Build the script for the second case
        script2 = [
            bitcoinlib.hex.decode(reclaim_pub_key),
            'CHECKSIG'
        ]
        script2_encoded = bitcoinlib.Script.encode(script2)
        print(script2_encoded)

        # Build the final scripts array
        scripts = [
            {"script": script1_encoded},
            {"script": script2_encoded}
        ]

        # Build the final script
        script = bitcoinlib.p2tr(bitcoinlib.TAPROOT_UNSPENDABLE_KEY, scripts, bitcoinlib.Network.TESTNET, True)
        print(script)

    def fetch_and_store_keys(self):
        try:
            url = "https://testnet.stx.eco/bridge-api/testnet/v1/btc/tx/keys"
            response = requests.get(url)
            data = response.json()
            reveal_pub_key = data['deposits']['revealPubKey']
            reclaim_pub_key = data['deposits']['reclaimPubKey']
            print("reveal", reveal_pub_key)
            print("reclaim", reclaim_pub_key)

            # Store the keys for later use (you can choose how to store them)
            self.reveal_pub_key = reveal_pub_key
            self.reclaim_pub_key = reclaim_pub_key

            print("Keys fetched and stored successfully!")
        except Exception as e:
            print(f"Failed to fetch and store keys: {e}")

    def fetch_fee_estimates(self):
        try:
            response = requests.get('https://testnet.stx.eco/bridge-api/testnet/v1/btc/blocks/fee-estimate')
            data = response.json()
            return data['feeInfo']
        except Exception as e:
            print(f"Failed to fetch fee estimates: {e}")
            return None

    def fetch_sbtc_wallet_address(self):
        try:
            response = requests.get('https://testnet.stx.eco/bridge-api/testnet/v1/sbtc/data')
            data = response.json()
            wallet_address = data['sbtcWalletAddress']
            return wallet_address
        except Exception as e:
            print(f"Failed to fetch sBTC wallet address: {e}")
            return "N/A"

    def fetch_btc_wallet_address(self, window):
        try:
            wallet = window.wallet  # Get the wallet object
            addresses = wallet.get_addresses()  # Get all addresses from the wallet
            max_balance = 0
            address_with_max_balance = None

            for address in addresses:
                balance_tuple = wallet.get_addr_balance(address)
                balance = balance_tuple[0]  # Access the confirmed balance from the tuple
                if balance > max_balance:
                    max_balance = balance
                    address_with_max_balance = address

            print("Address with the largest balance:", address_with_max_balance)
            print("Largest balance:", max_balance)
            return address_with_max_balance

        except Exception as e:
            print(f"Failed to fetch BTC wallet address: {e}")
            return "N/A"

    def prompt_password(self, window):
        # This function is called when the send button is pressed. It prompts the user for their password.
        password, ok = QInputDialog.getText(None, _('Enter Password'), _('Please enter your password'), QLineEdit.Password)
        if ok:
            self.send_btc(window, password)

    def send_btc(self, window, password):
        # This function sends the bitcoin transaction.
        try:
            amount_btc = float(self.amount_input.text())  # Get the amount of bitcoin to send
            recipient_address = self.address_input.text()  # Get the recipient's address
            fee_option = self.fee_combo.currentText()

            # Extract the fee amount from the selected option
            fee_btc = float(fee_option.split(":")[1].strip().split(" ")[0])

            # Validate the BTC amount input
            if not amount_btc:
                raise ValueError("BTC amount is required")
            try:
                amount_btc = float(amount_btc)
            except ValueError:
                raise ValueError("Invalid BTC amount")

            # Check if the recipient address is valid
            if not is_address(recipient_address):
                raise ValueError("Invalid recipient address")

            amount_sat = int(amount_btc * 1e8)  # Convert the amount to satoshis
            wallet = window.wallet  # Get the wallet object

            fee = int(fee_btc * 1e8)  # Convert the fee to satoshis

            self.fee_label.setText(f"{fee_btc:.8f}")  # Display the selected fee

            output = PartialTxOutput.from_address_and_value(recipient_address, amount_sat)  # Create the transaction output
            outputs = [output]

            coins = wallet.get_spendable_coins(None)  # Get the coins that can be spent
            tx = wallet.make_unsigned_transaction(coins=coins, outputs=outputs, fee=fee, rbf=True)  # Create the unsigned transaction
            wallet.sign_transaction(tx, str(password))  # Sign the transaction
            tx_hash = window.network.run_from_another_thread(window.network.broadcast_transaction(tx))  # Broadcast the transaction

            if tx_hash:
                wallet.add_transaction(tx_hash, tx)  # Add the transaction to the wallet
                wallet.save_db()  # Save the wallet

            # Display a message box confirming the transaction
            QMessageBox.information(None, _('Transaction Success'), _('Transaction Success! Please check History to view your transaction, Stacks and sBTC Rules!!'))
        except ValueError as e:
            # If there was an error, display a message box with the error
            QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))
        except InternalAddressCorruption as e:
            # If there was an error, display a message box with the error
            QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))
        except Exception as e:
            # If there was an error, display a message box with the error
            QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))


    def create_reclaim_deposit_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("144 blocks passed and your Deposit wasn't revealed. You can reclaim here.")))

        reclaim_button = QPushButton(_("Reclaim Deposit"))
        reclaim_button.clicked.connect(self.reclaim_deposit)
        vbox.addWidget(reclaim_button)

        widget.setLayout(vbox)
        return widget

    def reclaim_deposit(self):
        # Handle reclaiming of deposit here
        pass

    def create_reveal_deposit_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("144 blocks passed and your Deposit was revealed! Here is you TxID! *****************************************")))

        widget.setLayout(vbox)
        return widget

    def reveal_deposit(self):
        # Handle reclaiming of deposit here
        pass

    def create_withdraw_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("BTC Amount to Withdraw:")))
        self.amount_withdraw_input = QLineEdit()
        vbox.addWidget(self.amount_withdraw_input)

        vbox.addWidget(QLabel(_("STX Address:")))
        self.stx_address_input = QLineEdit()
        vbox.addWidget(self.stx_address_input)

        send_button = QPushButton(_("Withdraw sBTC for BTC"))
        send_button.clicked.connect(self.withdraw_sbtc)
        vbox.addWidget(send_button)

        widget.setLayout(vbox)
        return widget

    def withdraw_sbtc(self):
        pass

    def create_reclaim_withdrawal_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("144 blocks passed and your Withdrawal wasn't revealed. You can reclaim here.")))

        reclaim_withdrawal_button = QPushButton(_("Reclaim Withdrawal"))
        reclaim_withdrawal_button.clicked.connect(self.reclaim_withdrawal)
        vbox.addWidget(reclaim_withdrawal_button)

        widget.setLayout(vbox)
        return widget

    def reclaim_withdrawal(self):
        # Handle reclaiming of deposit here
        pass

    def create_reveal_withdrawal_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("144 blocks passed and your Withdrawal was revealed! Here is you TxID! *****************************************")))

        widget.setLayout(vbox)
        return widget

    def reveal_withdrawal(self):
        # Handle reclaiming of deposit here
        pass

    def create_summary_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("Summary of Transactions")))

        vbox.addWidget(QLabel(_("Add STX Address:")))
        self.add_address_input = QLineEdit()
        vbox.addWidget(self.add_address_input)

        add_button = QPushButton(_("Add Address"))
        add_button.clicked.connect(self.add_address)
        vbox.addWidget(add_button)

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setHorizontalHeaderLabels(["STX Address", "STX Balance", "sBTC Balance"])
        vbox.addWidget(self.summary_table)

        remove_button = QPushButton(_("Remove Selected Address"))
        remove_button.clicked.connect(self.remove_address)
        vbox.addWidget(remove_button)

        widget.setLayout(vbox)
        return widget

    def add_address(self):
        address = self.add_address_input.text()
        self.summary_table.insertRow(self.summary_table.rowCount())
        self.summary_table.setItem(self.summary_table.rowCount() - 1, 0, QTableWidgetItem(address))

        fetcher = BalanceFetcher(address)
        fetcher.balancesFetched.connect(self.update_balance)
        fetcher.finished.connect(lambda: self.cleanup(fetcher))
        fetcher.start()
        self.fetchers.append(fetcher)

        if address in self.balance_btc:  # Display the balance if already fetched
            stx_balance, sbtc_balance = self.balance_btc[address]
            self.summary_table.setItem(self.summary_table.rowCount() - 1, 1, QTableWidgetItem(str(stx_balance)))
            self.summary_table.setItem(self.summary_table.rowCount() - 1, 2, QTableWidgetItem(str(sbtc_balance)))

    def update_balance(self, address, stx_balance, sbtc_balance):
        self.balance_btc[address] = (stx_balance, sbtc_balance)

        for i in range(self.summary_table.rowCount()):
            if self.summary_table.item(i, 0).text() == address:
                stx_balance = stx_balance / 1000000
                stx_balance_item = QTableWidgetItem(str(stx_balance))
                sbtc_balance_item = QTableWidgetItem(str(sbtc_balance))
                self.summary_table.setItem(i, 1, stx_balance_item)
                self.summary_table.setItem(i, 2, sbtc_balance_item)
                break

    def remove_address(self):
        current_row = self.summary_table.currentRow()
        self.summary_table.removeRow(current_row)

    def cleanup(self, fetcher):
        self.fetchers.remove(fetcher)

    def create_tx_history_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("Tx History")))

        self.tx_history_table = QTableWidget()
        self.tx_history_table.setColumnCount(7)
        self.tx_history_table.setHorizontalHeaderLabels(["Date", "From", "To", "Amount", "Tx ID stx", "Tx ID btc", "Status"])
        vbox.addWidget(self.tx_history_table)

        widget.setLayout(vbox)
        return widget
