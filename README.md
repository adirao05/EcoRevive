# EcoRevive 

### ML-Assisted E-Waste Recovery and Blockchain-Based Reverse Logistics System

## Overview

EcoRevive is a web-based software prototype designed to support electronic waste (e-waste) recovery through product lifecycle tracking, machine-learning-assisted decision support, reverse-logistics functionality, and blockchain-based lifecycle event recording.

The project explores how these technologies can be integrated to improve the traceability and organisation of electronic products throughout their recovery lifecycle.

## Problem Statement

Electronic products such as laptops and smartphones require appropriate handling at the end of their useful life. Collection, inspection, repair, refurbishment, reuse, and recycling involve multiple stages and stakeholders.

EcoRevive demonstrates an integrated approach to product information management, recovery-related decision support, logistics coordination, and lifecycle event recording.

## Key Features

- **Product Lifecycle Tracking:** Maintain product-related information across recovery stages.
- **QR-Linked Product Passports:** Support product lookup through QR-linked identifiers.
- **Recovery Decision Support:** Provide recovery-related outputs using the project's machine-learning-assisted component.
- **Reverse Logistics:** Support recovery operations and logistics-related planning.
- **Blockchain Integration:** Integrate a Solidity smart contract for lifecycle event recording.
- **Audit Mechanism:** Include a local hash-chain mechanism for checking audit-record consistency.
- **Web Dashboard:** Provide a React-based interface for interacting with the application.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Database | SQLite |
| Smart Contracts | Solidity |
| Blockchain Development Environment | Hardhat |
| Decision Support | Machine-learning-assisted component |
| API Documentation | FastAPI / Swagger UI |

## System Architecture

The frontend communicates with the FastAPI backend. The backend coordinates application operations and database access, alongside the recovery-related and logistics components. The blockchain integration uses a Solidity smart contract in a local Hardhat development environment.

## Project Structure

The project is organised into frontend, backend, and blockchain-related components. Refer to the repository folders for the implementation and supporting configuration files.

## Getting Started

### Prerequisites

- Python 3
- Node.js and npm
- Git
- Hardhat and its required dependencies if running the blockchain component

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd EcoRevive
```

### 2. Set Up the Backend

Open a terminal:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed_demo.py
uvicorn app.main:app --reload
```

The API should be available at:

- Application API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 3. Set Up the Frontend

Open a separate terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local address printed by Vite, commonly:

`http://localhost:5173`

### 4. Blockchain Component

The project includes a Solidity smart contract named `EcoReviveRegistry` and a Hardhat-based local blockchain integration. Follow the blockchain component's configuration and deployment scripts before running this part.

## Demo Data and Limitations

The prototype includes synthetic training data and demonstration product records. Outputs from the recovery decision-support component should be interpreted in the context of the implemented prototype and not as independently validated real-world predictions.

The blockchain integration is intended for local development and demonstration. A local development blockchain does not by itself establish production deployment or public-chain verification.

## Future Improvements

- Validate recovery predictions using representative real-world datasets.
- Evaluate model performance with appropriate metrics and documented experiments.
- Strengthen audit-chain validation and automated integrity testing.
- Verify blockchain transactions, emitted events, and recorded contract state.
- Improve logistics optimisation and test the application with larger datasets.
- Deploy the application in a secure production environment.

## Intended Use

EcoRevive is an academic and technical prototype exploring e-waste recovery, product traceability, decision support, reverse logistics, and blockchain integration.

## Author

**Name:** [Aditya Rao B]  
**Project:** EcoRevive

## Links

- **Project Demonstration Video:** [Add your video link]
- **Project Report:** [Add your report link]
- **Presentation:** [Add your presentation link]

