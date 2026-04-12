"""
EDA Visualization — IMC Prosperity 4, Day -1
Log file: 68981.log
Strategy run: Naive market making with dynamic position sizing on EMERALDS + TOMATOES
"""

import json
import io
import csv
import matplotlib
matplotlib.use("Agg")  # non-interactive: saves PNGs without blocking
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from collections import defaultdict

# ── Load data ──────────────────────────────────────────────────────────────────

with open("68981.log", "r") as f:
    raw = json.load(f)

reader = csv.DictReader(io.StringIO(raw["activitiesLog"]), delimiter=";")
rows = list(reader)

trades = raw.get("tradeHistory", [])

# ── Parse into per-product dicts ───────────────────────────────────────────────

def parse_float(v):
    return float(v) if v not in ("", None) else None

def parse_int(v):
    return int(v) if v not in ("", None) else None

data = defaultdict(lambda: defaultdict(list))

for r in rows:
    p = r["product"]
    ts = int(r["timestamp"])
    data[p]["ts"].append(ts)
    data[p]["bid1"].append(parse_float(r["bid_price_1"]))
    data[p]["bid1v"].append(parse_int(r["bid_volume_1"]))
    data[p]["bid2"].append(parse_float(r["bid_price_2"]))
    data[p]["bid2v"].append(parse_int(r["bid_volume_2"]))
    data[p]["bid3"].append(parse_float(r["bid_price_3"]))
    data[p]["bid3v"].append(parse_int(r["bid_volume_3"]))
    data[p]["ask1"].append(parse_float(r["ask_price_1"]))
    data[p]["ask1v"].append(parse_int(r["ask_volume_1"]))
    data[p]["ask2"].append(parse_float(r["ask_price_2"]))
    data[p]["ask2v"].append(parse_int(r["ask_volume_2"]))
    data[p]["ask3"].append(parse_float(r["ask_price_3"]))
    data[p]["ask3v"].append(parse_int(r["ask_volume_3"]))
    data[p]["mid"].append(parse_float(r["mid_price"]))
    data[p]["pnl"].append(parse_float(r["profit_and_loss"]))

for p in data:
    d = data[p]
    d["spread"] = [
        a - b if a is not None and b is not None else None
        for a, b in zip(d["ask1"], d["bid1"])
    ]
    # Wall mid: mid of deepest stable quotes (level 2 bid/ask when available)
    d["wallmid"] = []
    for i in range(len(d["ts"])):
        b = d["bid2"][i] if d["bid2"][i] is not None else d["bid1"][i]
        a = d["ask2"][i] if d["ask2"][i] is not None else d["ask1"][i]
        d["wallmid"].append((b + a) / 2 if b is not None and a is not None else None)

# Parse trades per product
trade_data = defaultdict(lambda: {"ts": [], "price": [], "qty": [], "side": []})
for t in trades:
    sym = t["symbol"]
    side = "BUY" if t["buyer"] == "SUBMISSION" else "SELL"
    trade_data[sym]["ts"].append(t["timestamp"])
    trade_data[sym]["price"].append(t["price"])
    trade_data[sym]["qty"].append(t["quantity"])
    trade_data[sym]["side"].append(side)

products = ["EMERALDS", "TOMATOES"]
colors = {"EMERALDS": "#2ecc71", "TOMATOES": "#e74c3c"}

# ══════════════════════════════════════════════════════════════════════════════
# Figure 1 — Overview: mid-price, bid/ask levels, spread, P&L
# ══════════════════════════════════════════════════════════════════════════════

fig1, axes = plt.subplots(4, 2, figsize=(18, 16))
fig1.suptitle("IMC Prosperity 4 — Day -1 Overview\n(Naive MM + Dynamic Position Sizing)", fontsize=14, fontweight="bold")

for col, p in enumerate(products):
    d = data[p]
    ts = np.array(d["ts"])
    c = colors[p]

    # Row 0: Bid/Ask levels + mid
    ax = axes[0][col]
    ax.plot(ts, d["bid1"], color=c, alpha=0.5, lw=0.8, label="Bid L1")
    ax.plot(ts, d["ask1"], color=c, alpha=0.9, lw=0.8, ls="--", label="Ask L1")
    ax.plot(ts, d["mid"], color="black", lw=1.2, label="Mid")
    ax.fill_between(ts, d["bid1"], d["ask1"], alpha=0.1, color=c)
    ax.set_title(f"{p} — Bid / Ask / Mid")
    ax.set_ylabel("Price")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    # Row 1: All bid levels stacked
    ax = axes[1][col]
    ax.plot(ts, d["bid1"], color=c, lw=0.8, alpha=1.0, label="Bid L1")
    b2 = [v for v in d["bid2"]]
    b3 = [v for v in d["bid3"]]
    ax.plot(ts, b2, color=c, lw=0.6, alpha=0.6, ls="--", label="Bid L2")
    ax.plot(ts, b3, color=c, lw=0.4, alpha=0.3, ls=":", label="Bid L3")
    a2 = [v for v in d["ask2"]]
    a3 = [v for v in d["ask3"]]
    ax.plot(ts, d["ask1"], color="gray", lw=0.8, alpha=1.0, label="Ask L1")
    ax.plot(ts, a2, color="gray", lw=0.6, alpha=0.6, ls="--", label="Ask L2")
    ax.plot(ts, a3, color="gray", lw=0.4, alpha=0.3, ls=":", label="Ask L3")
    # Overlay trade executions
    td = trade_data[p]
    if td["ts"]:
        buy_ts = [ts_ for ts_, s in zip(td["ts"], td["side"]) if s == "BUY"]
        buy_px = [px for px, s in zip(td["price"], td["side"]) if s == "BUY"]
        sell_ts = [ts_ for ts_, s in zip(td["ts"], td["side"]) if s == "SELL"]
        sell_px = [px for px, s in zip(td["price"], td["side"]) if s == "SELL"]
        ax.scatter(buy_ts, buy_px, marker="^", color="blue", s=20, zorder=5, label=f"Our Buys ({len(buy_ts)})")
        ax.scatter(sell_ts, sell_px, marker="v", color="red", s=20, zorder=5, label=f"Our Sells ({len(sell_ts)})")
    ax.set_title(f"{p} — All Depth Levels + Our Trades")
    ax.set_ylabel("Price")
    ax.legend(fontsize=6)
    ax.grid(alpha=0.3)

    # Row 2: Spread over time
    ax = axes[2][col]
    spread = [s for s in d["spread"] if s is not None]
    ts_spread = [t for t, s in zip(ts, d["spread"]) if s is not None]
    ax.plot(ts_spread, spread, color=c, lw=0.8, alpha=0.7)
    ax.axhline(np.mean(spread), color="black", lw=1, ls="--", label=f"Mean={np.mean(spread):.2f}")
    ax.set_title(f"{p} — Bid-Ask Spread (L1)")
    ax.set_ylabel("Spread (ticks)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Row 3: P&L
    ax = axes[3][col]
    ax.plot(ts, d["pnl"], color=c, lw=1.2)
    ax.fill_between(ts, 0, d["pnl"], alpha=0.2, color=c)
    ax.axhline(0, color="black", lw=0.8, ls="--")
    final_pnl = d["pnl"][-1]
    ax.set_title(f"{p} — Cumulative P&L (final: {final_pnl:.1f})")
    ax.set_ylabel("P&L (SeaShells)")
    ax.set_xlabel("Timestamp")
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("eda_overview.png", dpi=150, bbox_inches="tight")
print("Saved: eda_overview.png")

# ══════════════════════════════════════════════════════════════════════════════
# Figure 2 — Spread Distribution + Volume at each level
# ══════════════════════════════════════════════════════════════════════════════

fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle("IMC Prosperity 4 — Day -1: Spread Distribution & Order Book Volume", fontsize=13, fontweight="bold")

for col, p in enumerate(products):
    d = data[p]
    c = colors[p]

    # Spread histogram
    ax = axes2[0][col]
    spread_vals = [s for s in d["spread"] if s is not None]
    bins = range(int(min(spread_vals)), int(max(spread_vals)) + 2)
    ax.hist(spread_vals, bins=bins, color=c, edgecolor="white", alpha=0.8)
    ax.set_title(f"{p} — Spread Distribution\nMean={np.mean(spread_vals):.2f}, Median={np.median(spread_vals):.1f}, Std={np.std(spread_vals):.2f}")
    ax.set_xlabel("Spread (ticks)")
    ax.set_ylabel("Frequency")
    ax.grid(alpha=0.3)

    # Volume stacked bar: bid L1/L2/L3 vs ask L1/L2/L3 over time (downsampled)
    ax = axes2[1][col]
    ts = np.array(d["ts"])
    step = 20  # downsample every 20th tick for readability
    ts_ds = ts[::step]
    bv1 = np.array([v if v is not None else 0 for v in d["bid1v"]])[::step]
    bv2 = np.array([v if v is not None else 0 for v in d["bid2v"]])[::step]
    bv3 = np.array([v if v is not None else 0 for v in d["bid3v"]])[::step]
    av1 = np.array([v if v is not None else 0 for v in d["ask1v"]])[::step]
    av2 = np.array([v if v is not None else 0 for v in d["ask2v"]])[::step]
    av3 = np.array([v if v is not None else 0 for v in d["ask3v"]])[::step]

    ax.stackplot(ts_ds, bv1, bv2, bv3, labels=["Bid L1", "Bid L2", "Bid L3"],
                 colors=[c, c, c], alpha=[0.9, 0.6, 0.3])
    ax.stackplot(ts_ds, -av1, -av2, -av3, labels=["Ask L1", "Ask L2", "Ask L3"],
                 colors=["gray", "gray", "gray"], alpha=[0.9, 0.6, 0.3])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title(f"{p} — Order Book Volume by Level (bid +, ask −)")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Volume")
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("eda_spread_volume.png", dpi=150, bbox_inches="tight")
print("Saved: eda_spread_volume.png")

# ══════════════════════════════════════════════════════════════════════════════
# Figure 3 — WallMid vs Mid + P&L rate (per-tick delta)
# ══════════════════════════════════════════════════════════════════════════════

fig3, axes3 = plt.subplots(2, 2, figsize=(14, 10))
fig3.suptitle("IMC Prosperity 4 — Day -1: Fair Value & P&L Rate", fontsize=13, fontweight="bold")

for col, p in enumerate(products):
    d = data[p]
    c = colors[p]
    ts = np.array(d["ts"])

    # WallMid vs Mid
    ax = axes3[0][col]
    ax.plot(ts, d["mid"], color="black", lw=1.0, alpha=0.6, label="Mid (L1)")
    ax.plot(ts, d["wallmid"], color=c, lw=1.2, alpha=0.9, label="WallMid (L2)")
    diff = [w - m if w is not None and m is not None else None
            for w, m in zip(d["wallmid"], d["mid"])]
    diff_clean = [x for x in diff if x is not None]
    ax.set_title(f"{p} — Mid vs WallMid\nMean deviation: {np.mean(diff_clean):.3f}")
    ax.set_ylabel("Price")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # P&L rate (tick-by-tick delta)
    ax = axes3[1][col]
    pnl = np.array(d["pnl"])
    pnl_delta = np.diff(pnl)
    ts_delta = ts[1:]
    ax.bar(ts_delta, pnl_delta, width=80, color=[c if v >= 0 else "#e74c3c" for v in pnl_delta], alpha=0.7)
    ax.axhline(0, color="black", lw=0.8)
    pos_ticks = np.sum(pnl_delta > 0)
    neg_ticks = np.sum(pnl_delta < 0)
    ax.set_title(f"{p} — P&L per Tick\n+ve ticks: {pos_ticks}, -ve ticks: {neg_ticks}, zero: {len(pnl_delta)-pos_ticks-neg_ticks}")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("P&L delta")
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("eda_fairvalue_pnlrate.png", dpi=150, bbox_inches="tight")
print("Saved: eda_fairvalue_pnlrate.png")

# ══════════════════════════════════════════════════════════════════════════════
# Figure 4 — Trade execution analysis
# ══════════════════════════════════════════════════════════════════════════════

fig4, axes4 = plt.subplots(1, 2, figsize=(14, 5))
fig4.suptitle("IMC Prosperity 4 — Day -1: Our Trade Executions", fontsize=13, fontweight="bold")

for col, p in enumerate(products):
    d = data[p]
    c = colors[p]
    ax = axes4[col]
    td = trade_data[p]

    if not td["ts"]:
        ax.text(0.5, 0.5, "No trades", transform=ax.transAxes, ha="center")
        continue

    buy_mask = [s == "BUY" for s in td["side"]]
    sell_mask = [s == "SELL" for s in td["side"]]

    buy_prices = [p_ for p_, m in zip(td["price"], buy_mask) if m]
    sell_prices = [p_ for p_, m in zip(td["price"], sell_mask) if m]
    buy_ts = [t for t, m in zip(td["ts"], buy_mask) if m]
    sell_ts = [t for t, m in zip(td["ts"], sell_mask) if m]
    buy_qty = [q for q, m in zip(td["qty"], buy_mask) if m]
    sell_qty = [q for q, m in zip(td["qty"], sell_mask) if m]

    # Plot mid as background
    ts_arr = np.array(d["ts"])
    ax.plot(ts_arr, d["mid"], color="gray", lw=0.8, alpha=0.5, label="Mid")

    ax.scatter(buy_ts, buy_prices, s=[q * 3 for q in buy_qty],
               marker="^", color="blue", alpha=0.8, zorder=5, label=f"Buys ({len(buy_prices)})")
    ax.scatter(sell_ts, sell_prices, s=[q * 3 for q in sell_qty],
               marker="v", color="red", alpha=0.8, zorder=5, label=f"Sells ({len(sell_prices)})")

    all_prices = buy_prices + sell_prices
    ax.set_title(f"{p} — Executions\nAvg buy: {np.mean(buy_prices):.2f} | Avg sell: {np.mean(sell_prices):.2f}" if buy_prices and sell_prices else f"{p} — Executions")
    ax.set_ylabel("Price")
    ax.set_xlabel("Timestamp")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("eda_executions.png", dpi=150, bbox_inches="tight")
print("Saved: eda_executions.png")

# ══════════════════════════════════════════════════════════════════════════════
# Summary stats
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("SUMMARY STATISTICS — Day -1")
print("=" * 60)

for p in products:
    d = data[p]
    spread_vals = [s for s in d["spread"] if s is not None]
    mid_vals = [m for m in d["mid"] if m is not None]
    final_pnl = d["pnl"][-1]
    td = trade_data[p]
    n_buys = sum(1 for s in td["side"] if s == "BUY")
    n_sells = sum(1 for s in td["side"] if s == "SELL")
    total_vol = sum(td["qty"])

    print(f"\n{p}")
    print(f"  Mid price range  : {min(mid_vals):.1f} — {max(mid_vals):.1f}")
    print(f"  Spread (L1)      : min={min(spread_vals):.0f}, max={max(spread_vals):.0f}, mean={np.mean(spread_vals):.2f}, std={np.std(spread_vals):.2f}")
    print(f"  Final P&L        : {final_pnl:.2f}")
    print(f"  Trades (us)      : {n_buys} buys, {n_sells} sells, total vol={total_vol}")
    if td["qty"]:
        print(f"  Avg trade size   : {np.mean(td['qty']):.1f}")

print("\nAll plots saved.")
