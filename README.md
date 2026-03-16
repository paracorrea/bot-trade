# Binance Trading Bot (Testnet) 📈

A Python-based automated trading bot developed for executing and monitoring crypto strategies on the **Binance Spot Test Network**. This project is designed to validate trading logic without risking real capital.

## 🚀 Current Implementation Cycle

The bot currently follows a structured execution cycle:
1.  **Market Buy**: Instant entry based on predefined parameters.
2.  **Limit Sell**: Automated placement of profit targets immediately after purchase.
3.  **Execution Monitoring**: Real-time tracking of order status until fulfillment.

## 🛠 Tech Stack

* **Language**: Python 3.10+
* **API**: [python-binance](https://github.com/sammchardy/python-binance)
* **Environment Management**: `python-dotenv`

## ⚙️ Configuration & Setup

### 1. Prerequisites
You must obtain your Testnet API Keys from:
🔗 [testnet.binance.vision](https://testnet.binance.vision/)

### 2. Environment Variables
Create a `.env` file in the root directory and add your credentials:
```env
BINANCE_API_KEY=your_testnet_key_here
BINANCE_API_SECRET=your_testnet_secret_here
SYMBOL=BTCUSDT
CAPITAL_PER_TRADE=100
BUY_DISCOUNT=0.2
SELL_TARGET=0.6