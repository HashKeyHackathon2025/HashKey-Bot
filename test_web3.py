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

# TEST_TELEGRAM_ID = 1234567
TEST_TELEGRAM_ID = 7654321

@pytest.fixture
def provider():
    return Web3Provider(HASHKEY_RPC_URL, PRIVATE_KEY)

def test_connection(provider):
    assert provider.is_connected() == True

def test_get_contract(provider):
    contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
    print(contract.address)
    assert contract.address == CORE_CONTRACT_ADDRESS

def test_check_ownership(provider):
    contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
    owner = contract.functions.owner().call()
    my_address = provider.w3.eth.account.from_key(PRIVATE_KEY).address
    print(f"Contract owner: {owner}")
    print(f"My address: {my_address}")
    assert owner.lower() == my_address.lower(), "현재 계정이 컨트랙트 소유자가 아닙니다"

def test_get_account_address(provider):
    contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
    owner = contract.functions.owner().call()
    my_address = provider.w3.eth.account.from_key(PRIVATE_KEY).address

    owner = Web3.to_checksum_address(owner)
    my_address = Web3.to_checksum_address(my_address)
    print(f"Contract owner (checksum): {owner}")
    print(f"My address (checksum): {my_address}")
    assert owner == my_address, "현재 계정이 컨트랙트 소유자가 아닙니다"

    # from 주소를 명시적으로 설정
    address = contract.functions.getAccountAddress(TEST_TELEGRAM_ID).call({
        'from': my_address
    })
    print(address)
    assert Web3.is_address(address), "반환된 주소가 유효한 이더리움 주소가 아닙니다"


def test_create_account_address(provider):
    provider.account_manager.create_account(TEST_TELEGRAM_ID)
    # contract = provider.get_contract(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
    # my_address = Web3.to_checksum_address(provider.w3.eth.account.from_key(PRIVATE_KEY).address)

    # nonce = provider.w3.eth.get_transaction_count(my_address)

    # gas_estimate = contract.functions.createAccount(TEST_TELEGRAM_ID).estimate_gas({
    #     'from': my_address,
    #     'nonce': nonce
    # })

    # transaction = contract.functions.createAccount(TEST_TELEGRAM_ID).build_transaction({
    #     'from': my_address,
    #     'gas': gas_estimate,
    #     'gasPrice': provider.w3.eth.gas_price,
    #     'nonce': nonce,
    #     'chainId' : provider.w3.eth.chain_id
    # })
    # signed_txn = provider.w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
    # tx_hash = provider.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    # tx_receipt = provider.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # print(tx_receipt)
    # assert tx_receipt['status'] == 1, "계정 생성 트랜잭션이 실패했습니다"