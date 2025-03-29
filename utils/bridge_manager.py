import os
from web3 import Web3
from typing import Optional
from data.contracts import CONTRACTS 
from eth_abi import encode_abi
from eth_utils import function_signature_to_4byte_selector


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
        
    # 메서드 만들기
    def execute_bridge_call(self, telegram_id: int, token_address: str, target_chain_address: str, amount: int, bridge_connector_address: str, bridge_address: str) -> str:
        # Step 1: Prepare selector + encoded arguments
        function_signature = "deposit(address,address,uint256,address)"
        selector = function_signature_to_4byte_selector(function_signature)
        encoded_args = encode_abi(
            ['address', 'address', 'uint256', 'address'],
            [token_address, target_chain_address, amount, bridge_address]
        )
        encoded_data = selector + encoded_args

        # Step 2: Build transaction
        tx = self.core_contract.functions.executeBridgeCall(
            telegram_id,
            encoded_data
        ).build_transaction({
            'from': self.provider.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.provider.account.address),
            'gas': 500_000,
            'gasPrice': self.w3.eth.gas_price
        })

        # Step 3: Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()