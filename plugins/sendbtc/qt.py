# Importing the required libraries and modules for this program.
import os
# Gets the BasePlugin class and the hook decorator from the Electrum plugin module. 
# The BasePlugin class is the parent class for all Electrum plugins, 
# and the @hook decorator is used to define hooks that can respond to certain events in the Electrum application. 
# Here it is used to create a new tab in the Electrum wallet GUI when a wallet is loaded.
from electrum.plugin import BasePlugin, hook
# Used to verify whether the recipient's address, inputted by the user, is a valid Bitcoin address.
from electrum.bitcoin import is_address
# Used for internationalization. 
# It wraps around string literals to make them translatable. 
# Used to make the GUI labels translatable into other languages.
from electrum.i18n import _
# Utility classes used to build the GUI. 
# WindowModalDialog is used to create a dialog window, while EnterButton is used to create the "Send" button.
from electrum.gui.qt.util import WindowModalDialog, EnterButton
# This is the class for the main Electrum wallet window. 
# Used in the load_wallet hook to add a new tab to the wallet window.
from electrum.gui.qt.main_window import ElectrumWindow
# This is an exception class that gets raised if there's a problem with the wallet's internal addresses. 
from electrum.wallet import InternalAddressCorruption
# This is a class used to represent a transaction output.
from electrum.transaction import PartialTxOutput
# These are various classes from the PyQt5 library used to build the GUI. 
# QVBoxLayout is used to arrange the GUI elements vertically, 
# QLabel is used to display static text, 
# QLineEdit is used for text input fields, 
# QPushButton is used to create a button, 
# QMessageBox is used to display message boxes, 
# QInputDialog is used to prompt the user for their password.
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
# Used to set the window flags for the dialog window.
from PyQt5.QtCore import Qt

# Defining a new class named Plugin which is a child class of BasePlugin.
# BasePlugin is a class provided by Electrum which serves as a base for all plugin types.
class Plugin(BasePlugin):

    # The __init__ method is the constructor for the class. It is the method that gets called when you create a new instance of the class.
    # In Python, the 'self' keyword is used in instance methods to refer to the instance of the class.
    def __init__(self, parent, config, name):

        # The 'super()' function is used to call a method in a parent class. In this case, it's used to call the constructor of the BasePlugin class.
        # This allows the Plugin class to inherit all the properties and methods of the BasePlugin class.
        # parent, config, and name are parameters to the BasePlugin constructor.
        # 'parent' is the parent Electrum plugin, 'config' is the configuration of the Electrum application, and 'name' is the name of this plugin.
        super().__init__(parent, config, name)

    @hook
    def load_wallet(self, wallet, window: ElectrumWindow):
        # When a wallet is loaded, add a new tab to the wallet window
        window.tabs.addTab(self.create_send_tab(window), _('Send BTC'))

    def create_send_tab(self, window):
        # This function creates the interface for the new "Send BTC" tab.
        widget = WindowModalDialog(window, _('Send BTC'))  # Create a new dialog window
        widget.setWindowFlags(widget.windowFlags() & ~Qt.Dialog)  # Set the window flags
        vbox = QVBoxLayout(widget)  # Create a new vertical box layout

        # Create the interface elements for the send tab
        vbox.addWidget(QLabel(_("Amount (BTC):")))  
        self.amount_input = QLineEdit()  
        vbox.addWidget(self.amount_input)

        vbox.addWidget(QLabel(_("Recipient Address:")))
        self.address_input = QLineEdit()
        vbox.addWidget(self.address_input)

        vbox.addWidget(QLabel(_("Estimated Fee (BTC):")))
        self.fee_label = QLabel()
        vbox.addWidget(self.fee_label)

        send_button = EnterButton(_('Send'), lambda: self.prompt_password(window))  # Create the send button
        vbox.addWidget(send_button)

        return widget  # Return the created widget

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

            # Check if the recipient address is valid
            if not is_address(recipient_address):
                raise ValueError("Invalid recipient address")

            amount_sat = int(amount_btc * 1e8)  # Convert the amount to satoshis
            wallet = window.wallet  # Get the wallet object
            fee_per_kb = 900  # Set the fee rate
            fee = wallet.config.estimate_fee_for_feerate(fee_per_kb, amount_sat)  # Estimate the fee
            fee_btc = fee / 1e8  # Convert the fee to BTC

            self.fee_label.setText(f"{fee_btc:.8f}")  # Display the estimated fee

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
