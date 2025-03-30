from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv
import json

load_dotenv()

HASHKEY_RPC_URL = os.getenv("HASHKEY_RPC_URL")
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")

class Web3Provider:
    def __init__(self, rpc_url: str, private_key: str = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key) if private_key else None
        self.network_type = "hashkey" if rpc_url == HASHKEY_RPC_URL else "sepolia"

        from utils.account_manager import AccountManager
        self.account_manager = AccountManager(self)
        from utils.bridge_manager import BridgeManager
        self.bridge_manager = BridgeManager(self)
        from utils.dex_manager import DexManager
        self.dex_manager = DexManager(self)

    def get_contract(self, address: str, abi_path: str):
        with open(abi_path, 'r') as f :
            abi = json.load(f)
        return self.w3.eth.contract(address=address, abi=abi['abi'])

    def is_connected(self):
        return self.w3.is_connected()
    
    def call_function(self, contract_function, *args):
        my_address = Web3.to_checksum_address(self.w3.eth.account.from_key(self.account.key).address)
        result = contract_function(*args).call({'from': my_address, 'chainId': self.w3.eth.chain_id})
        return result
    
    def send_transaction(self, contract_function, *args):
        my_address = Web3.to_checksum_address(self.w3.eth.account.from_key(self.account.key).address)
        nonce = self.w3.eth.get_transaction_count(my_address)
        
        transaction = contract_function(*args).build_transaction({
            'from': my_address,
            'gas': contract_function(*args).estimate_gas({'from': my_address}),
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
            'chainId': self.w3.eth.chain_id
        })
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt['transactionHash'].hex()