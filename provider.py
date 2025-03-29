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