import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수에서 RPC URL 가져오기
HASHKEY_RPC_URL = os.getenv("HASHKEY_RPC_URL")
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")

NETWORKS = {
    "HASHKEY": {
        "name": "Hashkey Testnet",
        "rpc": HASHKEY_RPC_URL,
        "chain_id": 133,
    },
    "SEPOLIA": {
        "name": "Sepolia Testnet",
        "rpc": SEPOLIA_RPC_URL,
        "chain_id": 11155111,
    }
}