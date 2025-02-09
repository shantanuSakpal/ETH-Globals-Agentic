# Helenus AI – Agentic AI Agents for DeFi Trading

## Overview

Helenus AI is a cutting-edge decentralized trading platform that leverages intelligent, autonomous agents to execute sophisticated on-chain strategies. By combining advanced AI-powered decision making with Coinbase's CDP AgentKit and the Morpho protocol, our system automates yield farming and risk management to maximize returns in the volatile DeFi landscape.

## Features

- **AI-Powered Trading Agents**  
  - Utilizes a ReAct agent architecture with LangChain, integrating memory and dynamic decision components.
  - Adapts to real-time market data and automatically manages strategy execution.

- **DeFi Strategy Execution**  
  - Implements an innovative Morpho Leveraged ETH Strategy:
    - Deposit ETH as collateral and borrow USDC at optimal rates using Morpho's IRM.
    - Loop borrowed funds to progressively enhance yield while maintaining safe LTV.
  - Incorporates sophisticated risk management and emergency protocols (flash loans, multiple oracle support, etc.).

- **Seamless Blockchain Integration**  
  - Integrates with Coinbase's CDP AgentKit and Morpho's lending protocol for robust on-chain interactions.
  - Automatically handles wallet creation, vault deployment, and fund management.

- **Real-Time Monitoring & Analytics**  
  - Modular services continuously monitor market conditions, risk metrics, and overall performance.
  - WebSocket-driven updates ensure live feedback and dynamic adjustments.

- **Modular & Scalable Architecture**  
  - Clean separation into services (WalletService, VaultService, AgentManager, StrategyMonitor), ensuring easy extensibility.
  - Ready for rapid expansion, with potential new strategies and integration with additional protocols.

## Architecture

- **Agentic Trading Engine:**  
  Autonomous agents execute the complete lifecycle of trading strategies—from vault setup and wallet management to continuous on-chain monitoring and trade adjustments.

- **Wallet & Vault Services:**  
  Secure wallet management and vault deployment work seamlessly to ensure safe fund storage and execution, with independent modules handling agent initialization and deposits.

- **Real-Time Data & Risk Control:**  
  Integrated market data feeds, performance monitoring, and risk assessment allow our agents to make evidence-based decisions.

- **CDP & Morpho Integration:**  
  The system leverages Coinbase's CDP AgentKit to interact with Morpho's lending markets, providing enhanced security, optimal interest rates, and advanced liquidity management.

## Getting Started

### Prerequisites

- **Python 3.10+**
- **MongoDB** for persistence
- **Poetry** for dependency management
- Environment configured with the necessary API keys

### Setup and Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/shantanuSakpal/ETH-Globals-Agentic
   cd backend
   ```

2. **Install Dependencies with Poetry**

   If you haven't installed Poetry yet, refer to [Poetry's installation guide](https://python-poetry.org/docs/#installation). Then, run:

   ```bash
   poetry install
   ```

3. **Activate the Virtual Environment**

   Use Poetry to open a shell:

   ```bash
   poetry shell
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the `backend` directory and add:

   ```dotenv
   CDP_API_KEY_NAME=your_cdp_api_key_name
   CDP_API_KEY_PRIVATE_KEY=your_cdp_api_key_private_key
   OPENAI_API_KEY=your_openai_api_key
   NETWORK_ID="base-sepolia"
   LLM_MODEL="gpt-4-turbo-preview"
   MONGODB_URL="mongodb://localhost:27017/your_db"
   ```

### Running the Application

1. **Start the Backend Server**

   Assuming you are using an ASGI server like Uvicorn, run:

   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Initialize Your Trading Agent**

   Use the provided WebSocket or CLI tools to initialize vaults and launch your MorphoAgent, kick-starting the fully automated strategy execution.

## Project Structure

- **/backend/core/agents:**  
  Contains all agent logic and strategy implementations (e.g., MorphoAgent).

- **/backend/services:**  
  Houses integrations for wallet management (WalletService), vault deployment (VaultService), and protocol interactions (MorphoService).

- **/backend/config & /backend/models:**  
  Core configuration files and data models used throughout the ecosystem.

- **/backend/README.md:**  
  Documentation and setup instructions.

## Future Enhancements

- Expand strategy library to include multi-asset and cross-chain trading.
- Enhance the front-end dashboard for deeper real-time analytics.
- Integrate additional DeFi protocols for greater diversification.
- Implement continuous AI-driven optimization based on performance metrics.

## License

This project is licensed under the MIT License.

---

Join us in revolutionizing decentralized finance by combining the power of autonomous agents with state-of-the-art blockchain technologies. With Helenus AI, yield farming and risk management reach a new level of sophistication in the DeFi era! 