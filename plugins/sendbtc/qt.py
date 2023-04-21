# importing required modules
import os
from electrum.plugin import BasePlugin, hook
from electrum.i18n import _
from electrum.gui.qt.util import WindowModalDialog
from electrum.gui.qt.main_window import ElectrumWindow
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

# Defining the class
class Plugin(BasePlugin):

# Hook called when a wallet is loaded in Electrum
    @hook
    def load_wallet(self, wallet, window: ElectrumWindow):
        # Add a new tab to the main window
        window.tabs.addTab(self.create_price_tab(window), _('Send BTC'))

    # Create the tab containing the Bitcoin price
    def create_price_tab(self, window):
        # Create a new widget with the main window as its parent
        widget = WindowModalDialog(window, _('Send BTC'))
        # Remove the "Dialog" flag to make the widget act like a regular tab
        widget.setWindowFlags(widget.windowFlags() & ~Qt.Dialog)
        # Create a layout for the widget
        vbox = QVBoxLayout(widget)

        # Create input fields for amount and address
        vbox.addWidget(QLabel(_("Amount (BTC):")))
        self.amount_input = QLineEdit()
        vbox.addWidget(self.amount_input)

        vbox.addWidget(QLabel(_("Recipient Address:")))
        self.address_input = QLineEdit()
        vbox.addWidget(self.address_input)

        # Create a button to initiate the transaction
        send_button = QPushButton(_('Send'))
        send_button.clicked.connect(self.send_btc)
        vbox.addWidget(send_button)

        return widget

    def send_btc(self):
        try:
            amount_btc = float(self.amount_input.text())
            recipient_address = self.address_input.text()

            # TODO: Validate the amount and recipient address, and initiate the transaction.
            # You will need to use the wallet and network APIs to perform the transaction.

            QMessageBox.information(None, _('Transaction Success'), _('BTC sent successfully!'))
        except Exception as e:
            QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))

