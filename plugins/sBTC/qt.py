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
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QWidget, QTabWidget, QInputDialog, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from electrum.gui.qt.util import (read_QIcon, ColorScheme, text_dialog, icon_path, WaitingDialog,
                   WindowModalDialog, ChoicesLayout, HelpLabel, Buttons,
                   OkButton, InfoButton, WWLabel, TaskThread, CancelButton,
                   CloseButton, HelpButton, MessageBoxMixin, EnterButton,
                   import_meta_gui, export_meta_gui,
                   filename_field, address_field, char_width_in_lineedit, webopen,
                   TRANSACTION_FILE_EXTENSION_FILTER_ANY, MONOSPACE_FONT,
                   getOpenFileName, getSaveFileName, BlockingWaitingDialog, font_height)

class BalanceFetcher(QThread):
    balancesFetched = pyqtSignal(str, float, float)

    def __init__(self, address):
        super().__init__()
        self.address = address

    def run(self):
        balance_stx, balance_sBTC = self.get_balance(self.address)
        self.balancesFetched.emit(self.address, balance_stx, balance_sBTC)

    def get_balance(self, address):
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
        icon_path = './sBTC Logo.png'
        sbtc_icon = read_QIcon("sBTC_Logo.png")
        tab_index = window.tabs.addTab(sbtc_tab, sbtc_icon, "sBTC")
        window.tabs.setTabToolTip(tab_index, "sBTC")

class SBTC_Tab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.fetchers = []
        self.balance_btc = {}  # Dictionary to store BTC balances for addresses

        layout = QVBoxLayout(self)
        tab_widget = QTabWidget()

        deposit_all_tab = self.create_deposit_all_tab(window)
        withdraw_all_tab = self.create_withdraw_all_tab(window)
        summary_tab = self.create_summary_tab(window)

        deposit_icon = read_QIcon("deposit.png")
        withdraw_icon = read_QIcon("withdraw.png")
        summary_icon = read_QIcon("tab_addresses.png")

        tab_widget.addTab(deposit_all_tab, deposit_icon, "Deposit")  # Add icon to deposit_all_tab
        tab_widget.addTab(withdraw_all_tab, withdraw_icon, "Withdraw")  # Add icon to withdraw_all_tab
        tab_widget.addTab(summary_tab, summary_icon, "Summary")  # Add icon to summary_tab

        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def create_deposit_all_tab(self, window):
        deposit_all_tab = QWidget()
        vbox = QVBoxLayout(deposit_all_tab)
        tab_widget = QTabWidget()

        deposit_tab = self.create_deposit_tab(window)
        tx_history_peg_in_tab = self.create_tx_history_peg_in_tab(window)

        deposit_icon = read_QIcon("deposit.png")
        pegin_icon = read_QIcon("tab_addresses.png")

        tab_widget.addTab(deposit_tab,deposit_icon, "Deposit BTC")
        tab_widget.addTab(tx_history_peg_in_tab, pegin_icon, "Tx history peg in")

        vbox.addWidget(tab_widget)
        deposit_all_tab.setLayout(vbox)

        return deposit_all_tab
    
    def create_withdraw_all_tab(self, window):
        withdraw_all_tab = QWidget()
        vbox = QVBoxLayout(withdraw_all_tab)
        tab_widget = QTabWidget()

        withdraw_icon = read_QIcon("withdraw.png")
        pegout_icon = read_QIcon("tab_addresses.png")

        withdraw_tab = self.create_withdraw_tab(window)
        tx_history_peg_out_tab = self.create_tx_history_peg_out_tab(window)

        tab_widget.addTab(withdraw_tab, withdraw_icon, "Withdraw BTC")
        tab_widget.addTab(tx_history_peg_out_tab, pegout_icon, "Tx history peg out")

        vbox.addWidget(tab_widget)
        withdraw_all_tab.setLayout(vbox)

        return withdraw_all_tab

    def create_deposit_tab(self, window):
        # This function creates the interface for the new "Send BTC" tab.
        widget = WindowModalDialog(window, _('Send BTC'))  # Create a new dialog window
        widget.setWindowFlags(widget.windowFlags() & ~Qt.Dialog)  # Set the window flags
        vbox = QVBoxLayout(widget)  # Create a new vertical box layout
        vbox.setContentsMargins(50, 20, 0, 0)

        # Create the interface elements for the send tab
        amount_layout = QHBoxLayout()  # Create a horizontal layout for amount input
        amount_label = QLabel(_("BTC to Deposit:"))
        self.amount_input = QLineEdit()
        self.amount_input.setMaximumWidth(100)
        self.amount_input.setPlaceholderText("BTC")
        amount_layout.addWidget(amount_label) 
        amount_layout.addSpacing(23) 
        amount_layout.addWidget(self.amount_input)
        amount_layout.addStretch()  # Add a stretch to push the input field to the right
        vbox.addLayout(amount_layout)
        vbox.addSpacing(10)

        stx_address_layout = QHBoxLayout()
        stx_address_label = QLabel(_("STX Address:"))
        self.stx_address_input = QLineEdit()
        self.stx_address_input.setMaximumWidth(500)
        self.stx_address_input.setPlaceholderText("STX Address")  
        stx_address_layout.addWidget(stx_address_label)
        stx_address_layout.addSpacing(36)
        stx_address_layout.addWidget(self.stx_address_input)
        stx_address_layout.addStretch()  
        vbox.addLayout(stx_address_layout)
        vbox.addSpacing(10)

        btc_wallet_address_layout = QHBoxLayout()
        btc_wallet_address_label = QLabel(_("My BTC wallet:"))
        self.btc_wallet_address_label = QLabel()
        self.btc_wallet_address_label.setMaximumWidth(500)  # Set the maximum width for the label
        btc_wallet_address_layout.addWidget(btc_wallet_address_label)
        btc_wallet_address_layout.addSpacing(30)
        btc_wallet_address_layout.addWidget(self.btc_wallet_address_label)
        btc_wallet_address_layout.addStretch()  
        vbox.addLayout(btc_wallet_address_layout)
        vbox.addSpacing(10)

        wallet_address_layout = QHBoxLayout()
        wallet_address_label = QLabel(_("sBTC wallet:"))
        self.wallet_address_label = QLabel()
        self.wallet_address_label.setMaximumWidth(500)  # Set the maximum width for the label
        wallet_address_layout.addWidget(wallet_address_label)
        wallet_address_layout.addSpacing(35)
        wallet_address_layout.addWidget(self.wallet_address_label)
        wallet_address_layout.addStretch() 
        vbox.addLayout(wallet_address_layout)
        vbox.addSpacing(10)

        address_layout = QHBoxLayout()
        address_label = QLabel(_("Recipient Address:"))
        self.address_input = QLineEdit()
        self.address_input.setMaximumWidth(500)  
        self.address_input.setPlaceholderText("Will be automatically generated") 
        address_layout.addWidget(address_label)
        address_layout.addSpacing(5)
        address_layout.addWidget(self.address_input)
        address_layout.addStretch()  # Add a stretch to push the input field to the right
        vbox.addLayout(address_layout)
        vbox.addSpacing(10)
        
        fee_layout = QHBoxLayout()
        fee_label = QLabel(_("Transaction Fee:"))
        self.fee_label = QLabel()
        self.fee_combo = QComboBox()
        fee_layout.addWidget(fee_label)
        fee_layout.addWidget(self.fee_label)
        fee_layout.addWidget(self.fee_combo)
        fee_layout.addStretch()  
        vbox.addLayout(fee_layout)
        vbox.addSpacing(10)

        generate_script_button = QPushButton("Generate Script")  
        generate_script_button.clicked.connect(self.generate_script)  # Connect the button click signal to the generate_script method
        generate_script_button.setMaximumWidth(150)  # Set the maximum width for the button
        vbox.addWidget(generate_script_button)
        vbox.addSpacing(10)

        send_button = EnterButton(_('Deposit BTC'), lambda: self.prompt_password(window))  # Create the send button
        send_button.setMaximumWidth(150)  # Set the maximum width for the button
        vbox.addWidget(send_button)


        btc_wallet_address = self.fetch_btc_wallet_address(window)
        self.btc_wallet_address_label.setText(btc_wallet_address)

        vbox.addStretch()

        widget.setLayout(vbox)
        return widget

    def generate_script(self):
        # Fetch fee estimates and populate the combo box
        fee_estimates = self.fetch_fee_estimates()
        if fee_estimates:
            fee_options = [
                f"{fee_estimates['low_fee_per_kb'] / 1e8}",
                f"{fee_estimates['medium_fee_per_kb'] / 1e8}",
                f"{fee_estimates['high_fee_per_kb'] / 1e8}"
            ]
            self.fee_combo.addItems(fee_options)

       # Fetch and display the sBTC wallet address
        wallet_address = self.fetch_sbtc_wallet_address()
        self.wallet_address_label.setText(wallet_address)

        self.fetch_and_store_keys()

    def fetch_and_store_keys(self):
        try:
            url = "https://testnet.stx.eco/bridge-api/testnet/v1/btc/tx/keys"
            response = requests.get(url)
            data = response.json()
            reveal_pub_key = data['deposits']['revealPubKey']
            reclaim_pub_key = data['deposits']['reclaimPubKey']

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
                balance = balance_tuple[0] 
                if balance > max_balance:
                    max_balance = balance
                    address_with_max_balance = address

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

    def reclaim_deposit(self):
        # Handle reclaiming of deposit here
        pass

    def create_withdraw_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        amount_withdraw_layout = QHBoxLayout()  # Create a horizontal layout for amount input
        amount_withdraw_label = QLabel(_("BTC to Withdraw:"))
        self.amount_withdraw_input = QLineEdit()
        self.amount_withdraw_input.setMaximumWidth(100)
        self.amount_withdraw_input.setPlaceholderText("BTC")
        amount_withdraw_layout.addWidget(amount_withdraw_label) 
        amount_withdraw_layout.addSpacing(23) 
        amount_withdraw_layout.addWidget(self.amount_withdraw_input)
        amount_withdraw_layout.addStretch()  # Add a stretch to push the input field to the right
        vbox.addLayout(amount_withdraw_layout)
        vbox.addSpacing(10)

        stx_address_layout = QHBoxLayout()  # Create a horizontal layout for amount input
        stx_address_label = QLabel(_("STX Address"))
        self.stx_address_input = QLineEdit()
        self.stx_address_input.setMaximumWidth(500)
        self.stx_address_input.setPlaceholderText("STX Address")
        stx_address_layout.addWidget(stx_address_label) 
        stx_address_layout.addSpacing(50) 
        stx_address_layout.addWidget(self.stx_address_input)
        stx_address_layout.addStretch()  # Add a stretch to push the input field to the right
        vbox.addLayout(stx_address_layout)
        vbox.addSpacing(10)

        btc_withdraw_wallet_address_layout = QHBoxLayout()
        btc_withdraw_wallet_address_label = QLabel(_("My BTC wallet:"))
        self.btc_withdraw_wallet_address_label = QLabel()
        self.btc_withdraw_wallet_address_label.setMaximumWidth(500)  # Set the maximum width for the label
        btc_withdraw_wallet_address_layout.addWidget(btc_withdraw_wallet_address_label)
        btc_withdraw_wallet_address_layout.addSpacing(30)
        btc_withdraw_wallet_address_layout.addWidget(self.btc_withdraw_wallet_address_label)
        btc_withdraw_wallet_address_layout.addStretch()  
        vbox.addLayout(btc_withdraw_wallet_address_layout)
        vbox.addSpacing(10)

        btc_withdraw_wallet_address = self.fetch_btc_wallet_address(window)
        self.btc_withdraw_wallet_address_label.setText(btc_withdraw_wallet_address)

        withdraw_button = EnterButton(_('Withdraw BTC'), lambda: self.prompt_password_withdraw(window))  # Create the withdraw button
        withdraw_button.setMaximumWidth(150)  # Set the maximum width for the button
        vbox.addWidget(withdraw_button)

        vbox.addStretch()

        widget.setLayout(vbox)
        return widget

    def prompt_password_withdraw(self, window):
        pass

    def withdraw_sbtc(self):
        pass

    def reclaim_withdrawal(self):
        # Handle reclaiming of withdrawal here
        pass

    def create_summary_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("Balances")))
        vbox.addSpacing(20)

        add_address_layout = QHBoxLayout()  # Create a horizontal layout for amount input
        add_address_label = QLabel(_("Add STX Address:"))
        self.add_address_input = QLineEdit()
        self.add_address_input.setMaximumWidth(500)
        self.add_address_input.setPlaceholderText("STX Address")
        add_address_layout.addWidget(add_address_label) 
        add_address_layout.addSpacing(10) 
        add_address_layout.addWidget(self.add_address_input)
        add_address_layout.addStretch()  # Add a stretch to push the input field to the right
        vbox.addLayout(add_address_layout)
        vbox.addSpacing(10)

        add_button = QPushButton(_("Add Address"))
        add_button.clicked.connect(self.add_address)
        add_button.setMaximumWidth(100)  # Set maximum width for the button
        vbox.addWidget(add_button)

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setHorizontalHeaderLabels(["STX Address", "STX Balance", "sBTC Balance"])
        vbox.addWidget(self.summary_table)

        refresh_summary_button = QPushButton(_("Refresh"))
        refresh_summary_button.clicked.connect(self.refresh_addresses)
        refresh_summary_button.setMaximumWidth(100)
        vbox.addWidget(refresh_summary_button)

        remove_button = QPushButton(_("Remove"))
        remove_button.clicked.connect(self.remove_address)
        remove_button.setMaximumWidth(100)
        vbox.addWidget(remove_button)

        vbox.addStretch()

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

        self.adjust_column_summary_widths()  # Adjust column widths after adding the address

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

        self.adjust_column_summary_widths()  # Adjust column widths after updating the balance

    def remove_address(self):
        current_row = self.summary_table.currentRow()
        self.summary_table.removeRow(current_row)

    def refresh_addresses(self):
        for row in range(self.summary_table.rowCount()):
            address = self.summary_table.item(row, 0).text()
            fetcher = BalanceFetcher(address)
            fetcher.balancesFetched.connect(self.update_balance)
            fetcher.finished.connect(lambda: self.cleanup(fetcher))
            fetcher.start()
            self.fetchers.append(fetcher)
        
        self.adjust_column_summary_widths()

    def adjust_column_summary_widths(self):
        self.summary_table.resizeColumnsToContents()

    def cleanup(self, fetcher):
        self.fetchers.remove(fetcher)

    def create_tx_history_peg_in_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("Tx history Deposit")))

        self.tx_history_peg_in_table = QTableWidget()
        self.tx_history_peg_in_table.setColumnCount(8)
        self.tx_history_peg_in_table.setHorizontalHeaderLabels(["ID", "Originator", "BTC Address", "Amount", "To Script", "Type", "Status", "Action"])
        vbox.addWidget(self.tx_history_peg_in_table)

        add_address_button = QPushButton("Add")
        add_address_button.clicked.connect(self.add_address_tx_history_peg_in)
        add_address_button.setMaximumWidth(100)
        vbox.addWidget(add_address_button)

        remove_address_button = QPushButton("Remove")
        remove_address_button.clicked.connect(self.remove_address_tx_history_peg_in)
        remove_address_button.setMaximumWidth(100)
        vbox.addWidget(remove_address_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_tx_history_peg_in)
        refresh_button.setMaximumWidth(100)
        vbox.addWidget(refresh_button)

        vbox.addStretch()

        widget.setLayout(vbox)
        return widget

    def add_address_tx_history_peg_in(self):
        address_tx_history_peg_in, ok = QInputDialog.getText(self, "Add Address", "Enter an address:")
        if ok:
            self.tx_history_peg_in_table.insertRow(self.tx_history_peg_in_table.rowCount())
            self.tx_history_peg_in_table.setItem(self.tx_history_peg_in_table.rowCount() - 1, 0, QTableWidgetItem(address_tx_history_peg_in))

            self.adjust_column_widths()
            self.fetch_tx_history_peg_in(address_tx_history_peg_in)

    def fetch_tx_history_peg_in(self, address):
        url_history = f"https://testnet.stx.eco/bridge-api/testnet/v1/sbtc/pegins/search/{address}"
        response_history = requests.get(url_history)
        data_history = response_history.json()

        if isinstance(data_history, list):
            # Handle the case where data is a list
            transactions = data_history
        elif isinstance(data_history, dict):
            # Handle the case where data is a dictionary
            transactions = data_history.get('transactions', [])
        else:
            transactions = []

        # Set the number of rows based on the number of transactions
        self.tx_history_peg_in_table.setRowCount(len(transactions))

        filtered_transactions = [
            transaction for transaction in transactions if transaction.get('status') == 3
        ]  

        self.filtered_transactions = filtered_transactions 

        # Populate the table with transaction data
        for row, transaction in enumerate(transactions):
            # Extracting the required fields: _id, originator, fromBtcAddress, amount, commitTxScript.address
            _id = transaction.get('_id', '')
            originator = transaction.get('originator', '')
            fromBtcAddress = transaction.get('fromBtcAddress', '')
            amount = transaction.get('amount', '')
            commitTxScript_address = transaction.get('commitTxScript', {}).get('address', '')
            type_ = transaction.get('requestType')
            status_tx = transaction.get('status')

            # Mapping the type_ value to the corresponding string
            if status_tx == 1:
                status_str = "pending"
            elif status_tx == 2:
                status_str = "committed"
            elif status_tx == 3:
                status_str = "reclaimed"
            elif status_tx == 4:
                status_str = "revealed"
            else:
                status_str = "op_return"  # Handle any other values not covered

            # Inserting the extracted data into the table
            self.tx_history_peg_in_table.setItem(row, 0, QTableWidgetItem(_id))
            self.tx_history_peg_in_table.setItem(row, 1, QTableWidgetItem(originator))
            self.tx_history_peg_in_table.setItem(row, 2, QTableWidgetItem(fromBtcAddress))
            self.tx_history_peg_in_table.setItem(row, 3, QTableWidgetItem(str(amount)))
            self.tx_history_peg_in_table.setItem(row, 4, QTableWidgetItem(commitTxScript_address))
            self.tx_history_peg_in_table.setItem(row, 5, QTableWidgetItem(type_))
            self.tx_history_peg_in_table.setItem(row, 6, QTableWidgetItem(status_str))

            if status_tx == 3:
                reclaim_button = QPushButton("Reclaim")
                reclaim_button.clicked.connect(lambda _, id=_id: self.reclaim_deposit(id))
                self.tx_history_peg_in_table.setCellWidget(row, 7, reclaim_button)

        self.adjust_column_widths()

    def remove_address_tx_history_peg_in(self):
        self.tx_history_peg_in_table.clearContents()
        self.tx_history_peg_in_table.setRowCount(0)

    def refresh_tx_history_peg_in(self):
        for row in range(self.tx_history_peg_in_table.rowCount()):
            address = self.tx_history_peg_in_table.item(row, 0).text()
            self.fetch_tx_history_peg_in(address)
    
    def adjust_column_widths(self):
        self.tx_history_peg_in_table.resizeColumnsToContents()

    def create_tx_history_peg_out_tab(self, window):
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("Tx history Deposit")))

        self.tx_history_peg_out_table = QTableWidget()
        self.tx_history_peg_out_table.setColumnCount(8)
        self.tx_history_peg_out_table.setHorizontalHeaderLabels(["ID", "Originator", "BTC Address", "Amount", "To Script", "Type", "Status", "Action"])
        vbox.addWidget(self.tx_history_peg_out_table)

        add_address_out_button = QPushButton("Add")
        add_address_out_button.clicked.connect(self.add_address_tx_history_peg_out)
        add_address_out_button.setMaximumWidth(100)
        vbox.addWidget(add_address_out_button)

        remove_address_out_button = QPushButton("Remove")
        remove_address_out_button.clicked.connect(self.remove_address_tx_history_peg_out)
        remove_address_out_button.setMaximumWidth(100)
        vbox.addWidget(remove_address_out_button)

        refresh_out_button = QPushButton("Refresh")
        refresh_out_button.clicked.connect(self.refresh_tx_history_peg_out)
        refresh_out_button.setMaximumWidth(100)
        vbox.addWidget(refresh_out_button)

        vbox.addStretch()

        widget.setLayout(vbox)
        return widget

    def add_address_tx_history_peg_out(self):
        address_tx_history_peg_out, ok = QInputDialog.getText(self, "Add Address", "Enter an address:")
        if ok:
            self.tx_history_peg_out_table.insertRow(self.tx_history_peg_out_table.rowCount())
            self.tx_history_peg_out_table.setItem(self.tx_history_peg_out_table.rowCount() - 1, 0, QTableWidgetItem(address_tx_history_peg_out))

            self.adjust_column_out_widths()
            self.fetch_tx_history_peg_out(address_tx_history_peg_out)

    def fetch_tx_history_peg_out(self, address_tx_history_peg_out):
        url_history = f"https://testnet.stx.eco/bridge-api/testnet/v1/sbtc/pegins/search/{address_tx_history_peg_out}"
        response_history = requests.get(url_history)
        data_history = response_history.json()

        if isinstance(data_history, list):
            # Handle the case where data is a list
            transactions = data_history
        elif isinstance(data_history, dict):
            # Handle the case where data is a dictionary
            transactions = data_history.get('transactions', [])
        else:
            transactions = [] 

        # Set the number of rows based on the number of transactions
        self.tx_history_peg_out_table.setRowCount(len(transactions))

        # Populate the table with transaction data
        for row, transaction in enumerate(transactions):
            # Extracting the required fields: _id, originator, fromBtcAddress, amount, commitTxScript.address
            _id = transaction.get('_id', '')
            originator = transaction.get('originator', '')
            fromBtcAddress = transaction.get('fromBtcAddress', '')
            amount = transaction.get('amount', '')
            commitTxScript_address = transaction.get('commitTxScript', {}).get('address', '')
            type_ = transaction.get('requestType')
            status_tx = transaction.get('status')

            # Mapping the type_ value to the corresponding string
            if status_tx == 1:
                status_str = "pending"
            elif status_tx == 2:
                status_str = "committed"
            elif status_tx == 3:
                status_str = "reclaimed"
            elif status_tx == 4:
                status_str = "revealed"
            else:
                status_str = "op_return"  # Handle any other values not covered

            # Inserting the extracted data into the table
            self.tx_history_peg_out_table.setItem(row, 0, QTableWidgetItem(_id))
            self.tx_history_peg_out_table.setItem(row, 1, QTableWidgetItem(originator))
            self.tx_history_peg_out_table.setItem(row, 2, QTableWidgetItem(fromBtcAddress))
            self.tx_history_peg_out_table.setItem(row, 3, QTableWidgetItem(str(amount)))
            self.tx_history_peg_out_table.setItem(row, 4, QTableWidgetItem(commitTxScript_address))
            self.tx_history_peg_out_table.setItem(row, 5, QTableWidgetItem("witdraw"))
            self.tx_history_peg_out_table.setItem(row, 6, QTableWidgetItem(status_str))

            if status_tx == 3:
                reclaim_withdraw_button = QPushButton("Reclaim")
                reclaim_withdraw_button.clicked.connect(lambda _, id=_id: self.reclaim_withdraw(id))
                self.tx_history_peg_out_table.setCellWidget(row, 7, reclaim_withdraw_button)

            self.adjust_column_out_widths()

    def remove_address_tx_history_peg_out(self):
        self.tx_history_peg_out_table.clearContents()
        self.tx_history_peg_out_table.setRowCount(0)

    def refresh_tx_history_peg_out(self):
        for row in range(self.tx_history_peg_out_table.rowCount()):
            address = self.tx_history_peg_out_table.item(row, 0).text()
            self.fetch_tx_history_peg_out(address)
    
    def adjust_column_out_widths(self):
        self.tx_history_peg_out_table.resizeColumnsToContents()

