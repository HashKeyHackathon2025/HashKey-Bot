import os
from web3 import Web3
from typing import Optional
from data.contracts import CONTRACTS 

HASHKEY_CORE_CONTRACT_ADDRESS = CONTRACTS["HASHKEY_CORE"]
SEPOLIA_CORE_CONTRACT_ADDRESS = CONTRACTS["SEPOLIA_CORE"]
HASHKEY_ACCOUNT_IMPL_CONTRACT_ADDRESS = CONTRACTS["SEPOLIA_CORE"]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
CORE_ABI_PATH = os.path.join(PROJECT_ROOT, "abi", "core.json")
ACCOUNT_IMPL_ABI_PATH = os.path.join(PROJECT_ROOT, "abi", "accountImpl.json")

class AccountManager:
    def __init__(self, provider):
        self.provider = provider
        self.w3 = provider.w3
        self.private_key = provider.account.key if provider.account else None

        # hashkey or sepolia core address
        self.core_contract_address = HASHKEY_CORE_CONTRACT_ADDRESS if provider.network_type == "hashkey" else SEPOLIA_CORE_CONTRACT_ADDRESS
            
    # 지갑 주소 반환
    def get_account_address(self, telegram_id: int) -> str:
        my_address = Web3.to_checksum_address(self.w3.eth.account.from_key(self.private_key).address)
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)
        
        address = contract.functions.getAccountAddress(telegram_id).call({
            'from': my_address
        })
        
        if not Web3.is_address(address):
            raise Exception("유효하지 않은 이더리움 주소입니다")
            
        return address
    
    # 지갑 생성
    def create_account(self, telegram_id: int) -> str:
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)
        return self.provider.send_transaction(contract.functions.createAccount, telegram_id)
    
    # EOA 등록
    def set_account_user(self, telegram_id: int, address: str) -> str :
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)
        return self._send_transaction(contract.functions.setAccountUser, telegram_id, address)
    
    # EOA 조회
    def get_account_user(self, user_address: str) -> str :
        contract = self.provider.get_contract(user_address, ACCOUNT_IMPL_ABI_PATH)
        return contract.functions.user()