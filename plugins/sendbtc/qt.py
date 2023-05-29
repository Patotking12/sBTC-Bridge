import os
from electrum.plugin import BasePlugin, hook
from electrum.bitcoin import is_address
from electrum.i18n import _
from electrum.gui.qt.util import WindowModalDialog, EnterButton
from electrum.gui.qt.main_window import ElectrumWindow
from electrum.util import format_satoshis_plain
from electrum.wallet import InternalAddressCorruption
from electrum.transaction import PartialTxOutput
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt

class Plugin(BasePlugin):
    def __init__(self, parent, config, name):
        super().__init__(parent, config, name)

    @hook
    def load_wallet(self, wallet, window: ElectrumWindow):
        window.tabs.addTab(self.create_send_tab(window), _('Send BTC'))

    def create_send_tab(self, window):
        widget = WindowModalDialog(window, _('Send BTC'))
        widget.setWindowFlags(widget.windowFlags() & ~Qt.Dialog)
        vbox = QVBoxLayout(widget)

        vbox.addWidget(QLabel(_("Amount (BTC):")))
        self.amount_input = QLineEdit()
        vbox.addWidget(self.amount_input)

        vbox.addWidget(QLabel(_("Recipient Address:")))
        self.address_input = QLineEdit()
        vbox.addWidget(self.address_input)

        vbox.addWidget(QLabel(_("Estimated Fee (BTC):")))
        self.fee_label = QLabel()
        vbox.addWidget(self.fee_label)

        send_button = EnterButton(_('Send'), lambda: self.prompt_password(window))
        vbox.addWidget(send_button)

        return widget

    def prompt_password(self, window):
        password, ok = QInputDialog.getText(None, _('Enter Password'), _('Please enter your password'), QLineEdit.Password)
        if ok:
            self.send_btc(window, password)

    def send_btc(self, window, password):
        try:
            amount_btc = float(self.amount_input.text())
            recipient_address = self.address_input.text()

            if not is_address(recipient_address):
                raise ValueError("Invalid recipient address")

            amount_sat = int(amount_btc * 1e8)
            wallet = window.wallet
            fee_per_kb = 200
            fee = wallet.config.estimate_fee_for_feerate(fee_per_kb, amount_sat)
            fee_btc = fee / 1e8

            self.fee_label.setText(f"{fee_btc:.8f}")

            output = PartialTxOutput.from_address_and_value(recipient_address, amount_sat)
            outputs = [output]

            coins = wallet.get_spendable_coins(None)
            tx = wallet.make_unsigned_transaction(coins=coins, outputs=outputs, fee=fee, rbf=True)
            wallet.sign_transaction(tx, str(password))
            tx_hash = window.network.run_from_another_thread(window.network.broadcast_transaction(tx))
            
            if tx_hash:
                wallet.add_transaction(tx_hash, tx)
                wallet.save_db()

            QMessageBox.information(None, _('Transaction Success'), _('Transaction Success! Strata Labs Rules!!'))
        except ValueError as e:
            QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))
        except InternalAddressCorruption as e:
            QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))
        except Exception as e:
            QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))
