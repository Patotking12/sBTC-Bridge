from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QWidget, QTabWidget, QInputDialog
from electrum.plugin import BasePlugin, hook
from electrum.i18n import _
import requests

class BalanceFetcher(QThread):
    balanceFetched = pyqtSignal(str, float)

    def __init__(self, address):
        super().__init__()
        self.address = address

    def run(self):
        balance = self.get_balance(self.address)
        self.balanceFetched.emit(self.address, balance)

    def get_balance(self, address):
        print(address)
        try:
            response = requests.get(f'https://testnet.stx.eco/bridge-api/testnet/v1/sbtc/address/{address}/balance')
            print(response)
            print(response.text)  # Print the response content
            data = response.json()
            print(data)
            balance = data['balance']
            return balance
        except Exception as e:
            print(f"Failed to fetch balance for address {address}: {e}")
            return 0



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
        widget = QWidget()
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("BTC Amount to Deposit:")))
        self.amount_input = QLineEdit()
        vbox.addWidget(self.amount_input)

        vbox.addWidget(QLabel(_("Associated STX Address:")))
        self.stx_address_input = QLineEdit()
        vbox.addWidget(self.stx_address_input)

        vbox.addWidget(QLabel(_("sBTC wallet:")))
        self.wallet_address_label = QLabel()
        vbox.addWidget(self.wallet_address_label)

        vbox.addWidget(QLabel(_("Transaction Fee:")))
        self.fee_label = QLabel()
        vbox.addWidget(self.fee_label)

        send_button = QPushButton(_("Deposit BTC for sBTC"))
        send_button.clicked.connect(self.deposit_btc)
        vbox.addWidget(send_button)

        self.tx_status_label = QLabel()
        vbox.addWidget(self.tx_status_label)

        # Fetch and display the sBTC wallet address
        wallet_address = self.fetch_sbtc_wallet_address()
        self.wallet_address_label.setText(wallet_address)

        widget.setLayout(vbox)
        return widget

    def fetch_sbtc_wallet_address(self):
        try:
            response = requests.get('https://testnet.stx.eco/bridge-api/testnet/v1/sbtc/data')
            data = response.json()
            wallet_address = data['sbtcWalletAddress']
            return wallet_address
        except Exception as e:
            print(f"Failed to fetch sBTC wallet address: {e}")
            return "N/A"


    def deposit_btc(self):
        pass

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
        self.amount_input = QLineEdit()
        vbox.addWidget(self.amount_input)

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
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["STX Address", "sBTC Balance"])
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
        fetcher.balanceFetched.connect(self.update_balance)
        fetcher.finished.connect(lambda: self.cleanup(fetcher))
        fetcher.start()
        self.fetchers.append(fetcher)

        if address in self.balance_btc:  # Display the balance if already fetched
            balance = self.balance_btc[address]
            self.summary_table.setItem(self.summary_table.rowCount() - 1, 1, QTableWidgetItem(str(balance)))


    def update_balance(self, address, balance):
        self.balance_btc[address] = float(balance)  # Update the balance_btc dictionary

        for i in range(self.summary_table.rowCount()):
            if self.summary_table.item(i, 0).text() == address:
                btc_balance_item = QTableWidgetItem(str(balance))
                self.summary_table.setItem(i, 1, btc_balance_item)  # Set the QTableWidgetItem in the "BTC Balance" column
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
