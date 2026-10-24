# EcoRevive — VS Code Project

AI + blockchain-inspired e-waste reverse logistics prototype for **Laptops and Smartphones**.

Features:
- Product registration and Digital Product Passports (QR-linked)
- ML predictions: return probability, recovery pathway, recovery value
- Product Recovery Priority Score
- Collection route planning baseline
- Tamper-evident hash-chained audit events
- React dashboard + FastAPI + SQLite
- Solidity registry contract


## Requirements
Python 3.11+ and Node.js 20+ recommended.

## Run backend (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed_demo.py
uvicorn app.main:app --reload
```
If activation is blocked:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed_demo.py
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000  
Swagger API docs: http://127.0.0.1:8000/docs

## Run frontend
Open a second VS Code terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:5173

## Try it
- Register a laptop or smartphone.
- Open its passport to view its prediction, QR code and lifecycle history.
- Record `COLLECTED`, then `INSPECTED`, then `REFURBISHED` or `RECYCLED`.
- Open Collection Planning and generate a nearest-neighbour route.
- Open Audit Trail and verify the event hash chain.

## Models
On startup, scikit-learn models are trained from generated synthetic records if model files are absent:
- Random Forest return classifier
- Random Forest recovery pathway classifier
- Random Forest recovery-value regressor


## Solidity contract
```bash
cd blockchain
npm install
npx hardhat compile
npx hardhat node
```
In another terminal:
```bash
cd blockchain
npx hardhat run scripts/deploy.js --network localhost
```

