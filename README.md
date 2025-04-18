# Auto-wallet-cheaker 
Install Required Libraries:
Run the following commands in Termux:

pkg update
pkg install python
pip install requests bip_utils tronpy


Run the Script:
Execute the script in Termux:


python auto_wallet_checker.py  


Stop the Script:
Press Enter to stop the script at any time.

5. Check Results:
Wallets with non-zero balances are saved in result.txt in the same directory. Use the following command to view the results:


cat result.txt
