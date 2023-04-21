import os
import requests
from electrum.plugin import BasePlugin, hook
from electrum.i18n import _
from electrum.gui.qt.util import WindowModalDialog
from electrum.gui.qt.main_window import ElectrumWindow
from electrum.network import Network
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt

class Plugin(BasePlugin):

    # Hook called when a wallet is loaded in Electrum
    @hook
    def load_wallet(self, wallet, window: ElectrumWindow):
        # Add a new tab to the main window
        window.tabs.addTab(self.create_price_tab(window), _('Bitcoin Price'))

    # Create the tab containing the Bitcoin price
    def create_price_tab(self, window):
        # Create a new widget with the main window as its parent
        widget = WindowModalDialog(window, _('Bitcoin Price'))
        # Remove the "Dialog" flag to make the widget act like a regular tab
        widget.setWindowFlags(widget.windowFlags() & ~Qt.Dialog)
        # Create a layout for the widget
        vbox = QVBoxLayout(widget)

        # Create and add the price label to the layout
        self.price_label = QLabel()
        vbox.addWidget(self.price_label)

        # Create and add the refresh button to the layout
        refresh_button = QPushButton(_('Refresh'))
        refresh_button.clicked.connect(self.update_price)
        vbox.addWidget(refresh_button)

        # Update the price label with the current price
        self.update_price()
        # Create a timer to update the price every 5 minutes
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_price)
        self.timer.start(5 * 60 * 1000)

        return widget

    # Fetch and display the current Bitcoin price
    def update_price(self):
        try:
            # Fetch the price from the Coindesk API
            response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json')
            data = response.json()
            price = data["bpi"]["USD"]["rate"]
            # Update the price label with the fetched price
            self.price_label.setText(_("Current Bitcoin price (USD): {}").format(price))
        except Exception as e:
            # Display an error message if fetching the price fails
            self.price_label.setText(_("Error fetching price: {}").format(e))

    # Clean up resources when the plugin is closed
    def clean_up(self):
        self.timer.stop()
