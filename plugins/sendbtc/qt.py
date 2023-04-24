import os
from electrum.plugin import BasePlugin, hook
from electrum.bitcoin import is_address
from electrum.i18n import _
from electrum.gui.qt.util import WindowModalDialog, EnterButton
from electrum.gui.qt.main_window import ElectrumWindow
from electrum.util import format_satoshis_plain
from electrum.wallet import InternalAddressCorruption
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

class Plugin(BasePlugin):

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

        send_button = EnterButton(_('Send'), lambda: self.send_btc(window))
        vbox.addWidget(send_button)

        return widget

        def send_btc(self, window):
            try:
                amount_btc = float(self.amount_input.text())
                recipient_address = self.address_input.text()

                if not is_address(recipient_address):
                    raise ValueError("Invalid recipient address")

                amount_sat = int(amount_btc * 1e8)
                wallet = window.wallet
                fee_per_kb = wallet.config.fee_per_kb()
                fee = wallet.config.estimate_fee_for_feerate(fee_per_kb, amount_sat)
                fee_btc = fee / 1e8

                self.fee_label.setText(f"{fee_btc:.8f}")

                outputs = [('address', recipient_address, amount_sat)]

                coins = wallet.get_spendable_coins(None)
                tx = wallet.make_unsigned_transaction(coins, outputs, window.config, fee=fee)
                wallet.sign_transaction(tx)
                tx_hash = window.network.broadcast_transaction(tx)

                QMessageBox.information(None, _('Transaction Success'), _('BTC sent successfully! Transaction ID: {}').format(tx_hash))
            except ValueError as e:
                QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))
            except InternalAddressCorruption as e:
                QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))
            except Exception as e:
                QMessageBox.critical(None, _('Transaction Error'), _('Error sending BTC: {}').format(e))

