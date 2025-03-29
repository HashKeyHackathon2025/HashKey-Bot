from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account.middleware import signing
import os
from dotenv import load_dotenv
import json

from data.contracts import CONTRACTS

load_dotenv()

# 환경 변수에서 RPC URL 가져오기
HASHKEY_RPC_URL = os.getenv("HASHKEY_RPC_URL")
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")

class Web3Provider:
    def __init__(self):
        # Hashkey provider init
        self.hashkey_w3 = Web3(Web3.HTTPProvider(HASHKEY_RPC_URL))
        self.hashkey_w3.middleware_onion.add(geth_poa_middleware)
        
        # Sepolia provider init
        self.sepolia_w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
        self.sepolia_w3.middleware_onion.add(geth_poa_middleware)

        self.contract_abis = {}
        self.contracts = {}

        self.load_contract_abi('CORE', './abi/core.json')
        self.load_contract_abi('ACCOUNT_IMPL', './abi/accountImpl.json')


    def load_contract_abi(self, contract_name: str, abi_path: str):
        with open(abi_path, 'r') as f:
            self.contract_abis[contract_name] = json.loads(f.read())

    def get_contract(self, network: str, contract_name: str, contract_address: str):
        contract_key = f"{network}_{contract_name}_{contract_address}"
        
        if contract_key in self.contracts:
            return self.contracts[contract_key]
            
        if contract_name not in self.contract_abis:
            raise ValueError(f"Contract ABI for {contract_name} not loaded")
            
        w3 = self.get_provider(network)
        contract = w3.eth.contract(
            address=contract_address,
            abi=self.contract_abis[contract_name]
        )
        
        self.contracts[contract_key] = contract
        return contract

    def get_provider(self, network: str) -> Web3:
        if network.upper() == "HASHKEY":
            return self.hashkey_w3
        elif network.upper() == "SEPOLIA":
            return self.sepolia_w3
        else:
            raise ValueError("not supported network")
         
    # 사용자 지갑 주소 반환        
    async def get_account_address(self, network: str, telegram_id: str) -> str :
        contract = self.get_contract(
            network=network,
            contract_name='CORE', 
            contract_address=CONTRACTS[f"{network.upper()}_CORE"]
        )
        return contract.functions.getAccountAddress(telegram_id).call()
        
    # # 사용자 지갑 생성
    # async def create_account_address(self, network: str, telegram_id) :
    #     contract = self

    # # 사용자의 토큰별 balance
    # async def get_token_balance(self, network: str, token_address: str, wallet)