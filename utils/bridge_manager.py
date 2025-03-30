import os
from web3 import Web3
from typing import Optional
from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector

from data.contracts import CONTRACTS 

HASHKEY_CORE_CONTRACT_ADDRESS = CONTRACTS["HASHKEY_CORE"]
SEPOLIA_CORE_CONTRACT_ADDRESS = CONTRACTS["SEPOLIA_CORE"]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
CORE_ABI_PATH = os.path.join(PROJECT_ROOT, "abi", "core.json")

class BridgeManager:
    def __init__(self, provider):
        self.provider = provider
        self.w3 = provider.w3
        self.private_key = provider.account.key if provider.account else None

        # hashkey or sepolia core address
        self.core_contract_address = HASHKEY_CORE_CONTRACT_ADDRESS if provider.network_type == "hashkey" else SEPOLIA_CORE_CONTRACT_ADDRESS
        
    # 브릿지 콜
    def execute_bridge_call(self, telegram_id: int, token_address: str, target_chain_address: str, amount: int, bridge_address: str) -> Optional[dict]:
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)

        function_signature = "deposit(address,address,uint256,address)"
        selector = function_signature_to_4byte_selector(function_signature)
        encoded_args = encode(
            ['address', 'address', 'uint256', 'address'],
            [token_address, target_chain_address, amount, bridge_address]
        )
        encoded_data = selector + encoded_args

        return self.provider.send_transaction(contract.functions.excuteBridgeCall, telegram_id, encoded_data)