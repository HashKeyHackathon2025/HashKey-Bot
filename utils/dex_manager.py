import os
from web3 import Web3
from typing import Optional
from data.contracts import CONTRACTS 

HASHKEY_CORE_CONTRACT_ADDRESS = CONTRACTS["HASHKEY_CORE"]
SEPOLIA_CORE_CONTRACT_ADDRESS = CONTRACTS["SEPOLIA_CORE"]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
CORE_ABI_PATH = os.path.join(PROJECT_ROOT, "abi", "core.json")

class DexManager:
    def __init__(self, provider):
        self.provider = provider
        self.w3 = provider.w3
        self.private_key = provider.account.key if provider.account else None

        # hashkey or sepolia core address
        self.core_contract_address = HASHKEY_CORE_CONTRACT_ADDRESS if provider.network_type == "hashkey" else SEPOLIA_CORE_CONTRACT_ADDRESS
        
    # 메서드 만들기