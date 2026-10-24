# EcoRevive local EVM integration

The backend can submit transactions to the included `EcoReviveRegistry` contract on a local Hardhat node. The integration is disabled by default; without EVM settings the app continues to use its existing local hash-chained SQLite ledger.

## 1. Install and start the local blockchain

Open a VS Code terminal:

```powershell
cd blockchain
npm install
npx hardhat compile
npx hardhat node
```

Keep this terminal open. Hardhat prints test accounts and their private keys. Use a local development key only; never use a real wallet key.

## 2. Deploy the contract

Open a second terminal at the project root:

```powershell
cd blockchain
npx hardhat run scripts/deploy.js --network localhost
```

Copy the printed `EcoReviveRegistry` address.

## 3. Configure FastAPI

Copy `backend/.env.example` to `backend/.env`, then replace the private-key and contract-address placeholders. The adapter loads that file automatically. Alternatively, set these environment variables in the same terminal where you start FastAPI:

```text
EVM_ENABLED=true
EVM_RPC_URL=http://127.0.0.1:8545
EVM_PRIVATE_KEY=<private key of a Hardhat local account>
EVM_CONTRACT_ADDRESS=<address printed by deploy>
```

The adapter loads `backend/.env` automatically; the following PowerShell method is an alternative:

```powershell
$env:EVM_ENABLED="true"
$env:EVM_RPC_URL="http://127.0.0.1:8545"
$env:EVM_PRIVATE_KEY="<local Hardhat private key>"
$env:EVM_CONTRACT_ADDRESS="<deployed contract address>"
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 4. Verify

- Visit `http://127.0.0.1:8000/api/blockchain/status` and check `connected: true`.
- Register a new laptop or smartphone in the dashboard. The API response includes registration transaction hashes.
- Record a lifecycle event. The response includes the transaction result.
- Restarting Hardhat resets its local chain; redeploy the contract and update its address after a reset.

## Important

This is a local development chain, not a public blockchain. Do not put personal data or secrets on-chain. Only hashes and lifecycle event types are submitted. The existing SQLite audit trail remains available. If an on-chain transaction fails, the API reports a `blockchain.status` of `error`; check that Hardhat is running, the address matches the current deployment, and the private key belongs to an account funded on that local chain.
