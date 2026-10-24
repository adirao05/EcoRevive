"""Optional Web3 adapter for the local EcoReviveRegistry contract.

Disabled by default. Configure the EVM_* environment variables to enable it.
"""
import json
import os
from functools import lru_cache
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

ABI = [
    {"type":"function","name":"registerProduct","stateMutability":"nonpayable","inputs":[{"name":"productId","type":"bytes32"},{"name":"passportHash","type":"bytes32"}],"outputs":[]},
    {"type":"function","name":"recordLifecycleEvent","stateMutability":"nonpayable","inputs":[{"name":"productId","type":"bytes32"},{"name":"eventType","type":"bytes32"},{"name":"evidenceHash","type":"bytes32"}],"outputs":[]},
    {"type":"function","name":"registeredProducts","stateMutability":"view","inputs":[{"name":"","type":"bytes32"}],"outputs":[{"name":"","type":"bool"}]},
    {"type":"function","name":"latestPassportHash","stateMutability":"view","inputs":[{"name":"","type":"bytes32"}],"outputs":[{"name":"","type":"bytes32"}]},
    {"type":"function","name":"verifyPassport","stateMutability":"view","inputs":[{"name":"productId","type":"bytes32"},{"name":"candidateHash","type":"bytes32"}],"outputs":[{"name":"","type":"bool"}]},
]


def enabled():
    return os.getenv("EVM_ENABLED", "false").lower() in {"1", "true", "yes"}


def _configured():
    return bool(os.getenv("EVM_RPC_URL") and os.getenv("EVM_PRIVATE_KEY") and os.getenv("EVM_CONTRACT_ADDRESS"))

@lru_cache(maxsize=1)
def _client():
    if not enabled():
        raise RuntimeError("EVM integration is disabled")
    if not _configured():
        raise RuntimeError("Set EVM_RPC_URL, EVM_PRIVATE_KEY, and EVM_CONTRACT_ADDRESS")
    w3 = Web3(Web3.HTTPProvider(os.getenv("EVM_RPC_URL")))
    if not w3.is_connected():
        raise RuntimeError("Cannot connect to EVM RPC endpoint")
    account = w3.eth.account.from_key(os.getenv("EVM_PRIVATE_KEY"))
    contract = w3.eth.contract(address=Web3.to_checksum_address(os.getenv("EVM_CONTRACT_ADDRESS")), abi=ABI)
    return w3, account, contract

def _bytes32(text):
    return Web3.keccak(text=str(text))

def _send(fn, w3, account):
    nonce = w3.eth.get_transaction_count(account.address)
    tx = fn.build_transaction({"from": account.address, "nonce": nonce, "chainId": w3.eth.chain_id,
                               "gas": 500000, "gasPrice": w3.eth.gas_price})
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt.status != 1:
        raise RuntimeError(f"Transaction failed: {tx_hash.hex()}")
    return {"transaction_hash": tx_hash.hex(), "block_number": receipt.blockNumber,
            "status": "confirmed", "explorer_url": None}

def register_product(product_id, passport):
    if not enabled():
        return {"status": "disabled", "message": "Local hash-chain ledger only; EVM integration is disabled."}
    w3, account, contract = _client()
    pid_hash = _bytes32(product_id)
    passport_hash = _bytes32(json.dumps(passport, sort_keys=True, separators=(",", ":")))
    reg = _send(contract.functions.registerProduct(pid_hash, passport_hash), w3, account)
    ev_hash = _bytes32(json.dumps({"product_id": product_id, "event_type": "REGISTERED", "passport": passport}, sort_keys=True, default=str))
    ev = _send(contract.functions.recordLifecycleEvent(pid_hash, _bytes32("REGISTERED"), ev_hash), w3, account)
    return {"status": "confirmed", "product_id_hash": pid_hash.hex(), "passport_hash": passport_hash.hex(),
            "registration_transaction": reg, "initial_event_transaction": ev}

def record_lifecycle_event(product_id, event_type, evidence):
    if not enabled():
        return {"status": "disabled", "message": "Local hash-chain ledger only; EVM integration is disabled."}
    w3, account, contract = _client()
    pid_hash = _bytes32(product_id)
    if not contract.functions.registeredProducts(pid_hash).call():
        raise RuntimeError("Product is not registered on the configured contract")
    evidence_hash = _bytes32(json.dumps(evidence, sort_keys=True, default=str))
    tx = _send(contract.functions.recordLifecycleEvent(pid_hash, _bytes32(event_type), evidence_hash), w3, account)
    return {"status": "confirmed", "product_id_hash": pid_hash.hex(), "evidence_hash": evidence_hash.hex(), "transaction": tx}

def status():
    if not enabled():
        return {"enabled": False, "connected": False, "mode": "local hash-chain ledger", "message": "Set EVM_ENABLED=true and configure EVM_* values to enable on-chain transactions."}
    try:
        w3, account, contract = _client()
        return {"enabled": True, "connected": True, "chain_id": w3.eth.chain_id,
                "account": account.address, "contract_address": contract.address, "mode": "EVM smart contract"}
    except Exception as exc:
        return {"enabled": True, "connected": False, "mode": "EVM smart contract", "message": str(exc)}
