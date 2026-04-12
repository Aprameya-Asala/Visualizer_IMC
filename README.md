# Testing_Bid_Ask

EDA and strategy development for **IMC Prosperity 4** (algorithmic trading competition).

---

## Quick Start

```bash
# Run EDA on the log file (generates 4 PNG plots)
py -3 eda_viz.py
```

Requires: `matplotlib`, `numpy` (standard Python install).

---

## Data

**`68981.log`** — Day -1 simulation log from a naive market making run with dynamic position sizing.

- **Products**: EMERALDS (~10,000) and TOMATOES (~5,000)
- **Timestamps**: 0 – 199,900 (step 100), 2,000 ticks each
- **Fields**: 3-level bid/ask depth, mid price, cumulative P&L per tick
- **Trade history**: 158 executed trades (buyer/seller/price/quantity)

### Day -1 Summary

| | EMERALDS | TOMATOES |
|---|---|---|
| Mid price range | 9,996 – 10,004 | 4,974.5 – 5,009.0 |
| Mean L1 spread | 15.76 ticks | 13.06 ticks |
| Final P&L | 1,050 | 1,468 |
| Trades (buys / sells) | 41 / 47 | 36 / 34 |

---

## EDA Plots

| File | Description |
|---|---|
| `eda_overview.png` | Bid/ask/mid price over time, spread evolution, cumulative P&L |
| `eda_spread_volume.png` | Spread histogram, order book volume by depth level |
| `eda_fairvalue_pnlrate.png` | WallMid vs Mid (fair value), per-tick P&L delta |
| `eda_executions.png` | Our buy/sell trade executions overlaid on mid-price |

---

## Key Observations

### EMERALDS
- Extremely stable: spread locked at 16 (bid 9992 / ask 10008) almost every tick
- WallMid = 10,000 = true fair value — never deviates
- Pure market-making conditions: inside-spread quoting captures reliable edge
- P&L grows steadily with no drawdowns

### TOMATOES
- More volatile: spread ranges 5–14, mean ~13
- Mid-price drifted down ~30 ticks over the day (5,006 → ~4,975)
- Wider spreads generate more P&L per fill than EMERALDS despite lower trade volume
- Dynamic position sizing helps manage inventory against the downtrend

### Strategy Insight
Inside-spread quoting (`best_bid + 1` / `best_ask - 1`) is the primary edge. Neither product shows exploitable momentum — EMA/momentum strategies significantly underperform on this data (see `STRATEGY_CONTEXT.md`).

---

## Repository Structure

```
Testing_Bid_Ask/
├── 68981.log              # Raw competition log (Day -1)
├── eda_viz.py             # EDA visualization script
├── eda_overview.png       # Generated plot
├── eda_spread_volume.png  # Generated plot
├── eda_fairvalue_pnlrate.png  # Generated plot
├── eda_executions.png     # Generated plot
├── STRATEGY_CONTEXT.md    # Frankfurt Hedgehogs strategy wisdom (IMC P3, 2nd globally)
├── CLAUDE.md              # Claude Code project memory
└── README.md              # This file
```

Strategy scripts (when created) follow the convention:
- `viz/{name}_viz.py` — backtesting with visualizer
- `submit/{name}_submit.py` — clean upload version

---

## References

- `STRATEGY_CONTEXT.md` — core strategy principles, order flow mechanics, product characteristics, and performance benchmarks from the Frankfurt Hedgehogs (IMC Prosperity 3, 2nd place globally)
