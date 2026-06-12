# 📊 ForexRank-AI

**Instant Forex Trade Decisions** | ICT + SMC + COT Analysis

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://gitlab.com/razu-group/Forex)

## 🚀 One-Click Deploy to Vercel

1. Click the **Deploy** button above
2. Connect your GitLab account
3. Click **Deploy**
4. Your app will be live in ~1 minute!

## ✨ Features

- **Instant Trade Decisions** - Get EXECUTE/WAIT/MONITOR/ABORT in seconds
- **28-Point Scoring System** - Comprehensive analysis
- **Trade Quality Score** - 100-point quality assessment
- **Auto Trade Levels** - Entry, SL, TP1-TP4 calculated automatically
- **Position Sizing** - Lot size based on your risk
- **Live Session Status** - Sydney, Tokyo, London, New York
- **Weekly Signals** - Top trading opportunities

## 🚦 Decision Thresholds

| Decision | Score | Quality | Action |
|----------|-------|---------|--------|
| 🟢 EXECUTE | ≥22/28 | ≥85% | Enter trade now |
| 🟡 WAIT | 14-21 | - | Wait for confirmation |
| 🟠 MONITOR | 10-13 | ≥70% | Watch for better entry |
| 🔴 ABORT | <10 | <70% | Do not trade |

## 📊 Scoring System (/28 points)

| Component | Points |
|-----------|--------|
| Weekly Direction Valid | +3 |
| Approved In Report | +2 |
| Sure Trade | +1 |
| Live MTF > 50 | +3 |
| Liquidity Sweep | +3 |
| Inside OB/FVG | +2 |
| BOS/CHOCH | +2 |
| RSI Alignment | +2 |
| MACD Alignment | +2 |
| DXY Supports | +2 |
| No News | +2 |
| Prime Session | +1 |
| Pivot Alignment | +1 |
| DXY Unchanged | +1 |
| Premium/Discount | +1 |

## 💰 Supported Pairs

- 🥇 **XAUUSD** (Gold)
- 🥈 **XAGUSD** (Silver)
- 🇪🇺 **EURUSD**
- 🇬🇧 **GBPUSD**
- 🇯🇵 **USDJPY**
- 💷 **GBPJPY**
- 🇦🇺 **AUDUSD**
- 🇨🇦 **USDCAD**
- 🇨🇭 **USDCHF**
- 🇳🇿 **NZDUSD**

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | POST | Analyze a trade |
| `/api/session` | GET | Get session status |
| `/api/signals` | GET | Get weekly signals |

## 📝 How to Use

1. **Select a currency pair** from the dropdown
2. **Choose direction** (BUY or SELL)
3. **Enter your account size** and risk percentage
4. **Click "Analyze Now"**
5. **Get your decision** with entry, SL, and TP levels!

## 📁 Project Structure

```
ForexRank-AI/
├── api/                    # Serverless functions
│   ├── index.py           # Health check
│   ├── analyze.py         # Trade analysis
│   ├── session.py         # Session status
│   └── signals.py         # Weekly signals
├── public/                 # Static files
│   └── index.html         # Main app
└── vercel.json            # Vercel config
```

## 📄 License

Private - Razu Group

---

**Made with ❤️ for traders**
