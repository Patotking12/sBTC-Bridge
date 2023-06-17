# sBTC-Bridge

This is a plugin for the Electrum wallet that allows you to interact with the Bitcoin sBTC bridge. 

The plugin provides features such as depositing BTC, reclaiming deposits, revealing deposits, withdrawing sBTC, reclaiming withdrawals, and viewing transaction history.

**Recommended**

Since this is still in production we do everything in Testnet so please get some BTC for testnet here: https://coinfaucet.eu/en/btc-testnet/

**Installation**

Clone the repository `git clone https://github.com/Patotking12/sBTC-Bridge.git` 

For installation of electrum wallet please follow the instructions here `https://github.com/spesmilo/electrum`

Launch Electrum on testnet `python3 run_electrum --testnet`, go to "Tools" > "Plugins" in the menu, and enable the "sBTC Plugin", close and reopen the wallet, be patient it takes some time to load all the information.

![Screenshot 2023-06-17 at 13 25 15](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/90514423-0035-43fe-adeb-b21979eb2a65)

**Requirements**

Python 3.7 or higher
Electrum Wallet

**Usage**

Open Electrum wallet on testnet `python3 run_electrum --testnet`.

Go to "Tools" > "Plugins" in the menu and select "sBTC Plugin".

The plugin will add a new tab called "sBTC" to the Electrum wallet interface.

Close and reopen the wallet, be patient it takes some time to load all the information.

Use the different tabs within the "sBTC" tab to perform various operations.

![Screenshot 2023-06-17 at 13 25 37](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/76978117-c1ad-4813-afa3-50ac40f00114)

**Deposit**

The "Deposit" tab contains all the functionalities for depositing, reclaiming and tracking your peg in transactions

**Deposit BTC**

The "Deposit BTC" tab allows you to deposit BTC to the sBTC bridge.

Enter the amount of BTC to deposit in the "Amount (BTC)" field.

Enter your associated STX address in the "Associated STX Address" field.

Your Address with the highest BTC amount will be displayed.

Enter the recipient address in the "Recipient Address" field. (Pending of the API endpoint to generate this, for now we can manually add any address and send BTC to it)

Select the transaction fee from the "Transaction Fee (BTC)" dropdown.

Click the "Deposit BTC" button.

Enter your wallet password when prompted.

The transaction will be sent, and a confirmation message will be displayed and will show in the Electrum History tab.

![Screenshot 2023-06-17 at 13 25 57](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/a6f93944-4392-4a75-9e8d-24fb0909a0ad)

**Tx history peg in**

The "Tx history peg in" tab displays the transaction history for peg-in transactions. You can only track a single address at a time. 

You are able to reclaim a Deposit. 

Click the "Add Address" button to add an address to the table.

Click the "Remove Address" button to clear the table.

Click the "Refresh" button to fetch and display the transaction history for the addresses.

![Screenshot 2023-06-17 at 13 29 41](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/32fcaf29-9f0e-4ff6-933a-244258db748f)

**Withdraw**

The "Withdraw" tab contains all the functionalities for withdrawing, reclaiming and tracking your peg out transactions

**Withdraw BTC**

The "Withdraw BTC" tab allows you to withdraw sBTC for BTC.

Enter the amount of sBTC to withdraw in the "BTC Amount to Withdraw" field. 

Enter your STX address in the "STX Address" field.

Click the "Withdraw sBTC for BTC" button. (Waiting for the API endpoint)

The withdrawal process will be initiated.

![Screenshot 2023-06-17 at 13 30 14](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/9ce43351-9ce4-4c62-9c2e-45d1f1740fec)

**Tx history peg out**

The "Tx history peg in" tab displays the transaction history for peg-in transactions. You can only track a single address at a time

You are able to reclaim a Withdraw. 

Click the "Add Address" button to add an address to the table.

Click the "Remove Address" button to clear the table.

Click the "Refresh" button to fetch and display the transaction history for the addresses.

![Screenshot 2023-06-17 at 14 03 22](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/7f1d766a-1784-4612-853a-d8e5c892f337)

**Summary**

The "Summary" tab provides an overview of your STX addresses balance for Stacks and sBTC.

Enter an STX address in the "Add STX Address" field.

Click the "Add Address" button to add the address to the summary table. It will automatically fetch the balances, it takes some time so it won't display straight away.

The table will display the STX address, STX balance, and sBTC balance.

Select a row in the table to remove an address using the "Remove Selected Address" button.

![Screenshot 2023-06-17 at 13 32 10](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/15b9515b-a179-4743-a5f8-ccc4c1b848b1)








