import pytest
from web3 import Web3
from provider import Web3Provider
import os
from dotenv import load_dotenv

load_dotenv()

from data.contracts import CONTRACTS

HASHKEY_RPC_URL = os.getenv("HASHKEY_RPC_URL")
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

CORE_CONTRACT_ADDRESS = CONTRACTS["HASHKEY_CORE"]
CORE_ABI_PATH = "./abi/core.json"

TEST_TELEGRAM_ID = 1234567
# TEST_TELEGRAM_ID = 7654321
# TEST_TELEGRAM_ID = 2345678

@pytest.fixture
def provider():
    return Web3Provider(HASHKEY_RPC_URL, PRIVATE_KEY)

def test_connection(provider):
    assert provider.is_connected() == True

def test_get_contract(provider):
    contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
    print(contract.address)
    assert contract.address == CORE_CONTRACT_ADDRESS

# def test_check_ownership(provider):
#     contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
#     owner = contract.functions.owner().call()
#     my_address = provider.w3.eth.account.from_key(PRIVATE_KEY).address
#     print(f"Contract owner: {owner}")
#     print(f"My address: {my_address}")
#     assert owner.lower() == my_address.lower(), "현재 계정이 컨트랙트 소유자가 아닙니다"

# def test_get_account_address(provider):
#     contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
#     owner = contract.functions.owner().call()
#     my_address = provider.w3.eth.account.from_key(PRIVATE_KEY).address

#     owner = Web3.to_checksum_address(owner)
#     my_address = Web3.to_checksum_address(my_address)
#     print(f"Contract owner (checksum): {owner}")
#     print(f"My address (checksum): {my_address}")
#     assert owner == my_address, "현재 계정이 컨트랙트 소유자가 아닙니다"

#     # from 주소를 명시적으로 설정
#     address = contract.functions.getAccountAddress(TEST_TELEGRAM_ID).call({
#         'from': my_address
#     })
#     print(address)
#     assert Web3.is_address(address), "반환된 주소가 유효한 이더리움 주소가 아닙니다"


# def test_create_account_address(provider):
#     provider.account_manager.create_account(TEST_TELEGRAM_ID)


def test_get_amount_out(provider):
    amount = 1 * 10 ** 18
    try:
        print(f"Using Telegram ID: {TEST_TELEGRAM_ID}")
        print(f"Using contract address: {CORE_CONTRACT_ADDRESS}")
        
        contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
        print(f"Contract deployed: {contract.address}")

        account_address = provider.account_manager.get_account_address(TEST_TELEGRAM_ID)
        print(f"Account address for Telegram ID: {account_address}")
        
        amountOut = provider.dex_manager.get_amount_out(
            telegram_id=TEST_TELEGRAM_ID,
            pair_address=CONTRACTS["HASHKEY_WHSK_WETH_POOL"],
            input_amount=amount
        )
        print(f"Amount Out: {amountOut}")
    except Exception as e:
        print(f"Error details: {str(e)}")
        print(f"Pool address: {CONTRACTS['HASHKEY_WHSK_WETH_POOL']}")
        print(f"Input amount: {amount}")
        print(f"Telegram ID: {TEST_TELEGRAM_ID}")
        raise