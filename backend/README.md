<!-- # CDP Agentkit Langchain Extension Examples - Chatbot Python

This example demonstrates an agent setup as a terminal style chatbot with access to the full set of CDP Agentkit actions.

## Ask the chatbot to engage in the Web3 ecosystem!
- "Transfer a portion of your ETH to john2879.base.eth"
- "Deploy an NFT that will go super viral!"
- "Choose a name for yourself and register a Basename for your wallet"
- "Deploy an ERC-20 token with total supply 1 billion"

## Requirements
- Python 3.10+
- Poetry for package management and tooling
  - [Poetry Installation Instructions](https://python-poetry.org/docs/#installation)
- [CDP API Key](https://portal.cdp.coinbase.com/access/api)
- [OpenAI API Key](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key)

### Checking Python Version
Before using the example, ensure that you have the correct version of Python installed. The example requires Python 3.10 or higher. You can check your Python version by running the following code:

```bash
python --version
poetry --version
```

## Installation
```bash
poetry install
```

## Run the Chatbot

### Set ENV Vars
- Ensure the following ENV Vars are set:
  - "CDP_API_KEY_NAME"
  - "CDP_API_KEY_PRIVATE_KEY"
  - "OPENAI_API_KEY"
  - "NETWORK_ID" (Defaults to `base-sepolia`)

```bash
make run
``` -->

## Backend Overview

### How the Backend Works Now

1. **WebSocket Connection & Authentication**  
   - **Connection:**  
     The backend uses FastAPI WebSocket endpoints (located in `backend/api/websocket/router.py` and `routes.py`) to manage real-time communication.
   - **Authentication:**  
     When a client connects, the WebSocket handler extracts an authentication token (from headers or query parameters) and verifies it using our `ws_auth` middleware. Once authenticated, the connection is registered in the connection manager, which tracks clients and their subscriptions.

2. **Strategy & Vault Initialization**  
   - **Strategy Selection:**  
     When a user selects a strategy (for example, the ETH Loop) and clicks the deposit button on the frontend, a WebSocket message of type `"strategy_select"` is sent to the backend.
   - **Vault Creation & Agent Setup:**  
     The WebSocket service (in `backend/services/websocket.py`) processes this message by:
     - Creating a new vault record via `VaultService`, linking it to the authenticated user.
     - Checking for agent wallet data, and if none is provided, automatically creating one via `WalletService`.
     - Initializing an agent (e.g., a MorphoAgent instance managed through `AgentManager`) that attaches to the vault and begins managing the trading strategy.
   - **Response:**  
     After successful initialization, the backend sends back a `"strategy_init"` message containing details such as the vault ID, the deposit address for the agent's wallet, and instructions to fund the wallet with gas.

3. **Deposit Process & Ongoing Monitoring**  
   - **Deposit & Contract Deployment:**  
     Once the agent's wallet is funded, the frontend sends a `"deposit"` message. This triggers `VaultService.handle_deposit` to deploy the vault contract (if not already deployed), update the vault balance, and execute deposit operations.
   - **Monitoring:**  
     A dedicated monitoring process periodically sends `"monitor_update"` and `"position_update"` messages back to the frontend, ensuring real-time updates on trading metrics, market conditions, health factors, and risk levels.

4. **General Architecture & Configurations**  
   - **Services:**  
     The backend is designed in a modular way with dedicated services:
     - `WalletService` handles wallet creation.
     - `VaultService` manages vault records and deposit operations.
     - `AgentManager` is responsible for initializing and managing trading agents.
     - `StrategyMonitor` oversees ongoing position monitoring.
   - **Environment Variables:**  
     Critical configuration values such as `CDP_API_KEY_NAME`, `CDP_API_KEY_PRIVATE_KEY`, `OPENAI_API_KEY`, and `NETWORK_ID` (which defaults to `"base-sepolia"`) are specified in the `.env` file (refer to `backend/.env.example`).
   - **Security:**  
     Sensitive files like `.env` are excluded from version control as specified in `backend/.gitignore`.

---

In summary, the backend fully implements the lifecycle from authenticating WebSocket connections, to initializing vaults and agents based on strategy selection, processing deposits, and continuously monitoring positions. This modular and secure architecture ensures seamless real-time integration with the frontend for managing trading strategies.
