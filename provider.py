from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv
import json

from data.contracts import CONTRACTS

load_dotenv()

# 환경 변수에서 RPC URL 가져오기
HASHKEY_RPC_URL = os.getenv("HASHKEY_RPC_URL")
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")

class Web3Provider:
    def __init__(self, rpc_url: str, private_key: str = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key) if private_key else None

    def get_contract(self, address: str, abi_path: str):
        with open(abi_path, 'r') as f :
            abi = json.load(f)
        return self.w3.eth.contract(address=address, abi=abi['abi'])

    def send_transaction(self, transaction) :
        if not self.account :
            raise ValueError("Private key not provided")
        
        if 'nonce' not in transaction :
            transaction['nonce'] = self.w3.eth.get_transaction_count(self.account.address)
        if 'gasPrice' not in transaction:
            transaction['gasPrice'] = self.w3.eth.gas_price    
         
        # 트랜잭션 서명
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
        
        # 트랜잭션 전송
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # 트랜잭션 영수증 대기 및 반환
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    def is_connected(self):
        return self.w3.is_connected()
    
    def get_balance(self, address: str):
        return self.w3.eth.get_balance(address)

    # 사용자 지갑 주소 반환        
    # async def get_account_address(self, network: str, telegram_id: str) -> str :
    #     contract = self.get_contract(
    #         network=network,
    #         contract_name='CORE', 
    #         contract_address=CONTRACTS[f"{network.upper()}_CORE"]
    #     )
    #     return contract.functions.getAccountAddress(telegram_id).call()
        
    # # 사용자 지갑 생성
    # async def create_account_address(self, network: str, telegram_id) :
    #     contract = self

    # # 사용자의 토큰별 balance
    # async def get_token_balance(self, network: str, token_address: str, wallet)