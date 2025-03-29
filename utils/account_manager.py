import os
from web3 import Web3
from typing import Optional
from data.contracts import CONTRACTS 

HASHKEY_CORE_CONTRACT_ADDRESS = CONTRACTS["HASHKEY_CORE"]
SEPOLIA_CORE_CONTRACT_ADDRESS = CONTRACTS["SEPOLIA_CORE"]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
CORE_ABI_PATH = os.path.join(PROJECT_ROOT, "abi", "core.json")

class AccountManager:
    def __init__(self, provider):
        self.provider = provider
        self.w3 = provider.w3
        self.private_key = provider.account.key if provider.account else None

        # hashkey or sepolia core address
        self.core_contract_address = HASHKEY_CORE_CONTRACT_ADDRESS if provider.network_type == "hashkey" else SEPOLIA_CORE_CONTRACT_ADDRESS
        
    def create_account(self, telegram_id: int) -> str:
        my_address = Web3.to_checksum_address(self.w3.eth.account.from_key(self.private_key).address)
        nonce = self.w3.eth.get_transaction_count(my_address)
        
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)
        
        transaction = contract.functions.createAccount(telegram_id).build_transaction({
            'from': my_address,
            'gas': contract.functions.createAccount(telegram_id).estimate_gas({'from': my_address}),
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
            'chainId': self.w3.eth.chain_id
        })

        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt['transactionHash'].hex()
    
    def get_account_address(self, telegram_id: int) -> str:
        my_address = Web3.to_checksum_address(self.w3.eth.account.from_key(self.private_key).address)
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)
        
        address = contract.functions.getAccountAddress(telegram_id).call({
            'from': my_address
        })
        
        if not Web3.is_address(address):
            raise Exception("유효하지 않은 이더리움 주소입니다")
            
        return address