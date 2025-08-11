# Limit Order Book Implementation

A Python implementation of a limit order book matching engine created as practice for Optiver's Future Focus Technology Program 2025.

## Overview

A fully functional limit order book that processes buy and sell orders, matches trades based on price-time priority, and maintains efficient order management using optimised data structures.

## Features

- Price-time priority matching
- O(1) order cancellation
- Real-time market data (best bid/ask, spread, mid-price)
- Partial order fills
- Volume tracking at price levels

## Quick Start

```bash
# Run tests in quiet mode (default)
python main.py

# Run tests with verbose output (shows all order details)
python main.py -v
python main.py --verbose
```

## Usage

```python
from orderbook import OrderBook

# Create order book
ob = OrderBook()

# Add orders (returns order_id)
order_id = ob.add_order('buy', 100.0, 50)
ob.add_order('sell', 101.0, 30)

# Cancel order
ob.cancel_order(order_id)

# Market data
best_bid = ob.get_best_bid()
best_ask = ob.get_best_ask()
spread = ob.get_spread()
mid_price = ob.get_mid_price()
volume = ob.get_total_volume('buy', 100.0)
```

## Implementation Details

### Data Structures
- **Order Storage**: Central dictionary for O(1) order access
- **Price Levels**: Sorted bid/ask prices using bisect
- **Order Queues**: Deques for FIFO processing at each price level
- **Lazy Cancellation**: Orders flagged as cancelled, removed when reached

### Performance
| Operation | Complexity |
|-----------|------------|
| Add Order | O(log n) |
| Cancel Order | O(1) |
| Get Best Price | O(1) |
| Match Orders | O(m) where m = matched orders |

## Testing

The test suite (`main.py`) includes:
- Basic functionality tests
- Edge case handling
- Performance benchmarks (10,000+ orders)
- Market simulation scenarios

**Verbosity Control**: By default, tests run in quiet mode, suppressing order matching details. Use the `-v` flag to see all order execution output:
```bash
python main.py -v  # Shows all trade executions and order details
```

## Example Output

```
--- TRADE EXECUTED ---
Incoming: Order(id=5, status='Active', side='buy', qty=30, price=100.5)
Existing: Order(id=3, status='Active', side='sell', qty=100, price=100.5)
Quantity: 30 @ Price: 100.5
----------------------
```
