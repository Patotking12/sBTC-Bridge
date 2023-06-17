# sBTC-Bridge
This is a plugin for the Electrum wallet that allows you to interact with the Bitcoin sBTC bridge. The plugin provides features such as depositing BTC, reclaiming deposits, revealing deposits, withdrawing sBTC, reclaiming withdrawals, and viewing transaction history.

**Installation**
Clone the repository.
Launch Electrum on testnet `python3 run_electrum --testnet`, go to "Tools" > "Plugins" in the menu, and enable the "sBTC Plugin".

**Requirements**
Python 3.7 or higher
Electrum Wallet

**Usage**
Open Electrum wallet on testnet `python3 run_electrum --testnet`.
Go to "Tools" > "Plugins" in the menu and select "sBTC Plugin".
The plugin will add a new tab called "sBTC" to the Electrum wallet interface.
Use the different tabs within the "sBTC" tab to perform various operations.

**Deposit**
The "Deposit" tab allows you to deposit BTC to the sBTC bridge.

Enter the amount of BTC to deposit in the "Amount (BTC)" field.
Enter your associated STX address in the "Associated STX Address" field.
Your Address with the highest BTC amount will be displayed.
Enter the recipient address in the "Recipient Address" field. (Still working on generating the script to send to, for now we can manually add it)
Select the transaction fee from the "Transaction Fee (BTC)" dropdown.
Click the "Deposit BTC" button.
Enter your wallet password when prompted.
The transaction will be sent, and a confirmation message will be displayed and will show in the Electrum History tab.

**Reclaim Deposit**
The "Reclaim Deposit" tab allows you to reclaim your deposit if it wasn't revealed within 144 blocks.

(Still being worked on)
Click the "Reclaim Deposit" button.
The reclaim process will be initiated.

**Reveal Deposit**
The "Reveal Deposit" tab displays the transaction ID when your deposit is revealed after 144 blocks.

We don't have to do anything here!

**Withdraw**
The "Withdraw" tab allows you to withdraw sBTC for BTC.

(Being worked on)
Enter the amount of sBTC to withdraw in the "BTC Amount to Withdraw" field.
Enter your STX address in the "STX Address" field.
Click the "Withdraw sBTC for BTC" button.
The withdrawal process will be initiated.

**Reclaim Withdrawal**
The "Reclaim Withdrawal" tab allows you to reclaim your withdrawal if it wasn't revealed within 144 blocks.

(Being worked on)
Click the "Reclaim Withdrawal" button.
The reclaim process will be initiated.

**Reveal Withdrawal**
The "Reveal Withdrawal" tab displays the transaction ID when your withdrawal is revealed after 144 blocks.

Nothin to do here!

**Summary**
The "Summary" tab provides an overview of your STX addresses balance.

Enter an STX address in the "Add STX Address" field.
Click the "Add Address" button to add the address to the summary table.
The table will display the STX address, STX balance, and sBTC balance.
Select a row in the table to remove an address using the "Remove Selected Address" button.

**Tx history peg in**
The "Tx history peg in" tab displays the transaction history for peg-in transactions.

Click the "Add Address" button to add an address to the table.
Select a row in the table to remove an address using the "Remove Address" button.
Click the "Refresh" button to fetch and display the transaction history for the addresses.






