import os
import requests
from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from tronpy import Tron
from time import sleep

# Output file to save results
RESULT_FILE = "result.txt"

# APIs for checking balances
BTC_API = "https://blockchain.info/q/addressbalance/"
ETH_API = "https://api.blockcypher.com/v1/eth/main/addrs/{}/balance"
USDT_ETH_API = "https://api.ethplorer.io/getAddressInfo/{}?apiKey=freekey"  # USDT (ERC20)
TRX_API = "https://api.trongrid.io/v1/accounts/{}"
DOGE_API = "https://dogechain.info/api/v1/address/balance/{}"

# Stopping flag
STOP_FLAG = False

# Check BTC balance
def check_btc_balance(address: str) -> float:
    try:
        response = requests.get(f"{BTC_API}{address}")
        if response.status_code == 200:
            return int(response.text) / 1e8  # Convert satoshis to BTC
    except Exception as e:
        print(f"Error checking BTC balance for {address}: {e}")
    return 0.0

# Check ETH and USDT balance
def check_eth_usdt_balance(address: str):
    eth_balance, usdt_balance = 0.0, 0.0
    try:
        response = requests.get(ETH_API.format(address))
        if response.status_code == 200:
            eth_balance = response.json().get("balance", 0) / 1e18  # Convert wei to ETH
    except Exception as e:
        print(f"Error checking ETH balance for {address}: {e}")

    try:
        response = requests.get(USDT_ETH_API.format(address))
        if response.status_code == 200:
            tokens = response.json().get("tokens", [])
            for token in tokens:
                if token["tokenInfo"]["symbol"] == "USDT":
                    usdt_balance = float(token["balance"]) / 1e6  # Convert USDT to readable format
                    break
    except Exception as e:
        print(f"Error checking USDT balance for {address}: {e}")

    return eth_balance, usdt_balance

# Check TRX balance
def check_trx_balance(address: str) -> float:
    try:
        response = requests.get(TRX_API.format(address))
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                return int(data["data"][0].get("balance", 0)) / 1e6  # Convert sun to TRX
    except Exception as e:
        print(f"Error checking TRX balance for {address}: {e}")
    return 0.0

# Check DOGE balance
def check_doge_balance(address: str) -> float:
    try:
        response = requests.get(DOGE_API.format(address))
        if response.status_code == 200:
            data = response.json()
            return float(data.get("balance", 0))  # DOGE balance is already in DOGE
    except Exception as e:
        print(f"Error checking DOGE balance for {address}: {e}")
    return 0.0

# Generate wallets and check balances
def process_wallet():
    try:
        # Generate mnemonic
        mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

        # BTC Wallet
        btc_wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        btc_address = btc_wallet.PublicKey().ToAddress()
        btc_private_key = btc_wallet.PrivateKey().Raw().ToHex()
        btc_balance = check_btc_balance(btc_address)

        # ETH and USDT Wallet
        eth_wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        eth_address = eth_wallet.PublicKey().ToAddress()
        eth_private_key = eth_wallet.PrivateKey().Raw().ToHex()
        eth_balance, usdt_balance = check_eth_usdt_balance(eth_address)

        # TRX Wallet
        tron = Tron()
        trx_wallet = tron.generate_address()
        trx_address = trx_wallet["base58check_address"]
        trx_private_key = trx_wallet["private_key"]
        trx_balance = check_trx_balance(trx_address)

        # DOGE Wallet
        doge_wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.DOGECOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        doge_address = doge_wallet.PublicKey().ToAddress()
        doge_private_key = doge_wallet.PrivateKey().Raw().ToHex()
        doge_balance = check_doge_balance(doge_address)

        # Log wallets with non-zero balances
        if any(balance > 0 for balance in [btc_balance, eth_balance, usdt_balance, trx_balance, doge_balance]):
            with open(RESULT_FILE, "a") as file:
                file.write(f"Mnemonic: {mnemonic}\n")
                file.write(f"BTC Address: {btc_address}, Private Key: {btc_private_key}, Balance: {btc_balance} BTC\n")
                file.write(f"ETH Address: {eth_address}, Private Key: {eth_private_key}, Balance: {eth_balance} ETH\n")
                file.write(f"USDT Balance: {usdt_balance} USDT\n")
                file.write(f"TRX Address: {trx_address}, Private Key: {trx_private_key}, Balance: {trx_balance} TRX\n")
                file.write(f"DOGE Address: {doge_address}, Private Key: {doge_private_key}, Balance: {doge_balance} DOGE\n")
                file.write("=" * 50 + "\n")
            print(f"Wallet with balance found! BTC: {btc_balance}, ETH: {eth_balance}, USDT: {usdt_balance}, TRX: {trx_balance}, DOGE: {doge_balance}")
    except Exception as e:
        print(f"Error processing wallet: {e}")

# Main function
def main():
    global STOP_FLAG
    os.system("clear")
    print("Generating seed phrases and checking balances. Press Enter to stop.")

    try:
        while not STOP_FLAG:
            process_wallet()
            sleep(1)  # Avoid hitting API rate limits
    except KeyboardInterrupt:
        STOP_FLAG = True
        print("Stopping...")

if __name__ == "__main__":
    main()
