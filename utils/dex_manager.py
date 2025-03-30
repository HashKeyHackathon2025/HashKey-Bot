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

class DexManager:
    def __init__(self, provider):
        self.provider = provider
        self.w3 = provider.w3
        self.private_key = provider.account.key if provider.account else None

        # hashkey or sepolia core address
        self.core_contract_address = HASHKEY_CORE_CONTRACT_ADDRESS if provider.network_type == "hashkey" else SEPOLIA_CORE_CONTRACT_ADDRESS
        
    # 입력 금액으로 출력 금액을 계산
    def get_amount_out(self, telegram_id: int, pair_address: str, input_amount: int) -> int:
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)
        
        function_signature = "getAmountOut(address,uint256)"
        selector = function_signature_to_4byte_selector(function_signature)
        encoded_args = encode(['address', 'uint256'], [pair_address, input_amount])
        encoded_data = selector + encoded_args
        
        return self.provider.call_function(contract.functions.excuteDexCall, telegram_id, encoded_data)

    # 출력 금액으로 입력 금액을 계산
    def get_amount_out(self, telegram_id: int, pair_address: str, input_amount: int) -> int:
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)

        function_signature = "getAmountOut(address,uint256)"
        selector = function_signature_to_4byte_selector(function_signature)
        encoded_args = encode(['address', 'uint256'], [pair_address, input_amount])
        encoded_data = selector + encoded_args

        return self.provider.call_function(contract.functions.excuteDexCall, telegram_id, encoded_data)

    # 입력값으로 토큰 스왑
    def swap_exact_tokens_for_tokens(self, telegram_id: int, pair_address: str, input_amount: int, slippage_percent: int) -> dict:
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)
        
        function_signature = "swapExactTokensForTokens(address,uint256,uint256)"
        selector = function_signature_to_4byte_selector(function_signature)
        encoded_args = encode(
            ['address', 'uint256', 'uint256'],
            [pair_address, input_amount, slippage_percent]
        )
        encoded_data = selector + encoded_args
        
        return self.provider.send_transaction(contract.functions.excuteDexCall, telegram_id, encoded_data)

    # 출력값으로 토큰 스왑을 실행
    def swap_tokens_for_exact_tokens(self, telegram_id: int, pair_address: str, output_amount: int, slippage_percent: int) -> dict:
        contract = self.provider.get_contract(self.core_contract_address, CORE_ABI_PATH)
        
        function_signature = "swapTokensForExactTokens(address,uint256,uint256)"
        selector = function_signature_to_4byte_selector(function_signature)
        encoded_args = encode(
            ['address', 'uint256', 'uint256'],
            [pair_address, output_amount, slippage_percent]
        )
        encoded_data = selector + encoded_args
        
        return self.provider.send_transaction(contract.functions.excuteDexCall, telegram_id, encoded_data)