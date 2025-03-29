import pytest
from web3 import Web3
from provider import Web3Provider
import os

from data.contracts import CONTRACTS

HASHKEY_RPC_URL = os.getenv("HASHKEY_RPC_URL")
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

CORE_CONTRACT_ADDRESS = CONTRACTS["HASHKEY_CORE"]
CORE_ABI_PATH = "./abi/core.json"

TEST_TELEGRAM_ID = "1234567"

@pytest.fixture
def provider():
    return Web3Provider(HASHKEY_RPC_URL, PRIVATE_KEY)

def test_connection(provider):
    assert provider.is_connected() == True

def test_get_contract(provider):
    contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
    print(contract.address)
    assert contract.address == CORE_CONTRACT_ADDRESS

def test_get_account_address(provider):
    contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
    address = contract.functions.getAccountAddress(TEST_TELEGRAM_ID)
    print(address)

# def test_send_transaction(provider):
#     transaction = {
#         'to': Web3.to_checksum_address('0x742d35Cc6634C0532925a3b844Bc454e4438f44e'),
#         'value': Web3.to_wei(0.1, 'ether'),
#         'gas': 21000,
#         'chainId': 1  # 메인넷 체인 ID
#     }
    
#     try:
#         receipt = provider.send_transaction(transaction)
#         assert receipt['status'] == 1  # 트랜잭션 성공
#         assert 'transactionHash' in receipt
#     except Exception as e:
#         pytest.fail(f"트랜잭션 전송 실패: {str(e)}")

# def test_invalid_private_key():
#     with pytest.raises((ValueError, TypeError)):
#         Web3Provider(HASHKEY_RPC_URL, None)

# def test_contract_interaction(provider):
#     # 컨트랙트 인스턴스 가져오기
#     contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
    
#     # owner() 함수 호출 테스트
#     try:
#         owner = contract.functions.owner().call()
#         assert Web3.is_address(owner)
#     except Exception as e:
#         pytest.fail(f"컨트랙트 함수 호출 실패: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v"])