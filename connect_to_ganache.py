from web3 import Web3

# Connect to local Ganache instance
ganache_url = 'http://127.0.0.1:7545'
print(f"Connecting to Ganache at {ganache_url}")
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Check if connected
try:
    if w3.is_connected():
        print("Connected to Ganache")
        # Print the first account's balance
        balance = w3.eth.get_balance(w3.eth.accounts[0])
        balance_in_ether = Web3.from_wei(balance, 'ether')
        print(f"Balance of first account: {balance_in_ether} Ether")
    else:
        print("Failed to connect")
except Exception as e:
    print(f"Error: {e}")



