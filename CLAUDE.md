# CLAUDE.md — Testing_Bid_Ask

Project memory for Claude Code. Reference this when continuing work in this repo.

---

## Project Purpose

Exploratory data analysis (EDA) and strategy development for **IMC Prosperity 4** (algorithmic trading competition). This repo holds:
- Raw competition log files
- EDA visualization scripts
- Strategy scripts (see file convention below)
- Strategy reference context

---

## Competition Environment

- **Platform**: IMC Prosperity 4 (tutorial/Round 0)
- **Products**: EMERALDS (stable, ~10,000), TOMATOES (volatile, ~5,000)
- **Position limit**: 80 units per product
- **No fees** in backtester
- **Order processing**: deterministic per-tick (no race conditions; see `STRATEGY_CONTEXT.md`)

See `STRATEGY_CONTEXT.md` for full competition mechanics, strategy principles, and code patterns.

---

## Log File Format (`68981.log`)

JSON with three keys:
- `activitiesLog` — semicolon-delimited CSV, one row per (timestamp, product)
- `tradeHistory` — list of our executed trades `{timestamp, buyer, seller, symbol, price, quantity}`
- `logs` — per-tick lambda output (order book snapshot + submitted orders)

### activitiesLog columns
```
day ; timestamp ; product ;
bid_price_1 ; bid_volume_1 ; bid_price_2 ; bid_volume_2 ; bid_price_3 ; bid_volume_3 ;
ask_price_1 ; ask_volume_1 ; ask_price_2 ; ask_volume_2 ; ask_price_3 ; ask_volume_3 ;
mid_price ; profit_and_loss
```

- Timestamps: 0 – 199,900 (step 100), Day -1 only
- 4,000 data rows (2,000 per product)
- Depth levels 2 and 3 are empty for some ticks

---

## Day -1 Key Stats (from `68981.log`)

| Metric | EMERALDS | TOMATOES |
|---|---|---|
| Mid price range | 9996 – 10004 | 4974.5 – 5009.0 |
| L1 spread (mean) | 15.76 | 13.06 |
| L1 spread (std) | 1.35 | 1.69 |
| Final P&L | 1,050.00 | 1,467.59 |
| Our buys / sells | 41 / 47 | 36 / 34 |
| Total volume traded | 570 | 240 |
| Avg trade size | 6.5 | 3.4 |

**Strategy run**: naive market making with dynamic position sizing on both products.

### Notable observations
- EMERALDS: near-constant spread of 16 (bid L1=9992, ask L1=10008), L2 at 9990/10010. WallMid = true fair value = 10000. Almost no mid-price drift — pure MM conditions.
- TOMATOES: spread more variable (5–14), mid drifted from ~5006 down to ~4975 range. Slight downtrend during Day -1. Inside-spread quoting still profitable.
- P&L grows steadily for both; TOMATOES earns more despite lower volume due to wider spreads.
- Both products: only 2 depth levels active most of the time (L3 empty).

---

## File Convention

| Pattern | Purpose |
|---|---|
| `viz/{name}_viz.py` | Backtest + visualizer (has logger) |
| `submit/{name}_submit.py` | Upload to IMC (no logger) |
| `eda_viz.py` | EDA on raw log files |
| `*.log` | Raw competition log files |
| `*.png` | Generated EDA plots |
| `STRATEGY_CONTEXT.md` | Frankfurt Hedgehogs strategy wisdom |
| `CLAUDE.md` | This file |

---

## EDA Outputs

Run `py -3 eda_viz.py` from the repo root. Produces 4 PNGs:

| File | Contents |
|---|---|
| `eda_overview.png` | Bid/ask/mid over time, all depth levels + our trades, spread over time, P&L curve |
| `eda_spread_volume.png` | Spread histogram, order book volume by level over time |
| `eda_fairvalue_pnlrate.png` | WallMid vs Mid, per-tick P&L delta |
| `eda_executions.png` | Our buy/sell executions overlaid on mid-price |

---

## Strategy Benchmark (Round 0)

From `STRATEGY_CONTEXT.md`:
- Improved MM: **30,321** (best)
- Basic MM: **29,496**
- Message (MM + mean rev): **27,346**
- Attempt2 (EMA momentum): **5,374** (worst)

Current run (Day -1 only): EMERALDS 1,050 + TOMATOES 1,468 = **2,518 total**.
