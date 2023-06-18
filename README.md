# sBTC-Bridge

The sBTC-Bridge is a plugin for the Electrum wallet that enables interaction with the Bitcoin sBTC bridge. 

This plugin offers a range of features, including depositing BTC to obtain sBTC, reclaiming deposits, withdrawing sBTC to obtain BTC, reclaiming withdrawals, viewing transaction history, and tracking wallet balances for STX and sBTC.

**Prerequisites**

Before using the sBTC-Bridge plugin, make sure you have the following:

- Python 3.7 or higher
- Electrum Wallet

**Recommended**

Since the plugin is currently in production, all operations are performed on the Testnet. To proceed, obtain testnet BTC from https://coinfaucet.eu/en/btc-testnet/

**Installation**

To install the sBTC-Bridge plugin, follow these steps:

1. Clone the repository: git clone https://github.com/Patotking12/sBTC-Bridge.git

2. Install the Electrum wallet by referring to the instructions available at https://github.com/spesmilo/electrum.

3. Launch Electrum on the testnet by running the command: `python3 run_electrum --testnet`

4. In the Electrum wallet, go to "Tools" > "Plugins" in the menu and enable the "sBTC Plugin".

5. Close and reopen the wallet.

<img width="1271" alt="Screenshot 2023-06-18 at 14 58 48" src="https://github.com/Patotking12/sBTC-Bridge/assets/108552266/6199c32a-fe7c-4d31-b278-ec33ca51c9aa">


<img width="1271" alt="Screenshot 2023-06-18 at 14 58 51" src="https://github.com/Patotking12/sBTC-Bridge/assets/108552266/f3dfc594-ed61-4372-8bf0-e6ebfa39406b">


**Usage**

- The plugin will add a new tab called "sBTC" to the Electrum wallet interface.

Use the different tabs within the "sBTC" tab to perform various operations.

**Deposit**

The "Deposit" tab within the "sBTC" tab provides functionalities for depositing, reclaiming, and tracking peg-in transactions.

**Deposit BTC**

To deposit BTC into the sBTC bridge, follow these steps:

1. Go to the "Deposit BTC" tab.

2. Enter the desired amount of BTC to deposit in the "BTC to Deposit" field.

3. Provide your STX address in the "STX Address" field.

4. The address with the highest BTC amount from withing Electrum will be displayed, since that is the one that Electrum will use to send the BTC.

5. Click the "Generate Script" button, and the plugin will automatically start fetching the information it needs with the information you inputed to create the Script you will send the BTC to.

6. This will take some time, since the plugin is fetching all the information it needs and processing it, please be patient.

7. Manually enter the recipient address in the "Recipient Address" field. (Note: This step is temporary until the API endpoint generates this automatically. For the time being, we can add any BTC address and send BTC)

8. Choose the transaction fee from the "Transaction Fee" dropdown menu, it will have 3 options: Low, Medium and High fee.

9. Click the "Deposit BTC" button.

10. Enter your wallet password when prompted.

11. The transaction will be sent, and a confirmation message will be displayed. You can also check the Electrum History tab for the transaction details. Or add your STX address to the "Tx history peg in" tab to track all transactions related to sBTC Bridge.

<img width="1100" alt="Screenshot 2023-06-17 at 21 30 11" src="https://github.com/Patotking12/sBTC-Bridge/assets/108552266/73159821-1acc-486c-8f58-7854f344de57">


**Tx history peg in**

The "Tx history peg in" tab displays the transaction history for peg-in transactions. You can track a single address at a time.

To interact with the transaction history, follow these steps:

1. Click the "Add" button to add an STX address to the table.

2. You will be prompted to input the STX address you want to track the transactions from.

3. The Plugin will start fetching your transactions, this may take some time, so be patient.

4. All the peg in transactions will be displayed, showing: 
  - ID
  - Originator
  - BTC Address
  - Amount
  - To Script
  - Type
  - Status
  - Action
    
5. If you have a transaction in "reclaimed" status, a "Reclaim" button will be displayed, that when clicked it will start the reclaim action and your BTC will be refunded to the BTC address it was deposited from.

6. Click the "Remove" button to clear the table.

7. Click the "Refresh" button to fetch and update the transaction history for the address.

![Screenshot 2023-06-18 at 15 05 07](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/341510fd-c28a-43fb-9e9d-d9a48d44b64b)


**Withdraw**

The "Withdraw" tab within the "sBTC" tab offers functionalities for withdrawing, reclaiming, and tracking peg-out transactions.

**Withdraw BTC**

To withdraw sBTC and obtain BTC, follow these steps:

1. Go to the "Withdraw BTC" tab.

2. Enter the desired amount of sBTC to withdraw in the "BTC to Withdraw" field.

3. Provide your STX address in the "STX Address" field.

4. Click the "Withdraw BTC" button. (This step is awaiting the API endpoint.)

5. The withdrawal process will be initiated.

<img width="1100" alt="Screenshot 2023-06-17 at 21 30 35" src="https://github.com/Patotking12/sBTC-Bridge/assets/108552266/791f33db-560e-49b9-a347-746b3498f92d">


**Tx history peg out**

The "Tx history peg out" tab displays the transaction history for peg-out transactions. You can track a single address at a time.

To interact with the transaction history, follow these steps:

1. Click the "Add" button to add an STX address to the table.

2. You will be prompted to input the STX address you want to track the transactions from.

3. The Plugin will start fetching your transactions, this may take some time, so be patient.

4. All the peg out transactions will be displayed, showing: 
  - ID
  - Originator
  - BTC Address
  - Amount
  - To Script
  - Type
  - Status
  - Action
    
5. If you have a transaction in "reclaimed" status, a "Reclaim" button will be displayed, that when clicked it will start the reclaim action and your sBTC will be refunded to the STX address it was withdrawed from.

6. Click the "Remove" button to clear the table.

7. Click the "Refresh" button to fetch and update the transaction history for the address.

![Screenshot 2023-06-18 at 15 05 11](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/b47d9699-74c2-431a-8a3a-024b86fadf3b)


**Summary**

The "Summary" tab provides an overview of the wallet balances for Stacks and sBTC associated with your STX addresses.

To utilize the "Summary" tab, follow these steps:

1. Enter an STX address in the "Add STX Address" field.

3. Click the "Add" button to add the address to the summary table. Please note that fetching balances may take some time before they are displayed.

4. The table will present the STX address, STX balance, and sBTC balance.

5. Select a row in the table to remove an address using the "Remove" button.

![Screenshot 2023-06-18 at 15 08 56](https://github.com/Patotking12/sBTC-Bridge/assets/108552266/f4614f7c-a4b1-4e09-a905-817ad4e44f3d)









