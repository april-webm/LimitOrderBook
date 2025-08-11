# Limit Order Book Implementation

A Python implementation of a limit order book (LOB) matching engine with price-time priority, supporting order placement, cancellation, and near instant retrieval.

## Overview

This implementation provides a fully functional limit order book that processes buy and sell orders, matches trades based on price-time priority, and maintains efficient order management using optimised data structures.

## Features

- **Price-Time Priority**: Orders are matched first by price, then by arrival time
- **Efficient Order Management**: O(1) order lookup and cancellation
- **Real-Time Market Data**: Instant access to best bid/ask, spread, and mid-price
- **Partial Fills**: Support for partial order execution
- **Volume Tracking**: Query total volume at any price level
- **High Performance**: Optimised for speed with sorted price levels and deque-based queues

## Installation

No external dependencies required - uses Python standard library only.

```bash
git clone https://github.com/april-webm/LimitOrderBook.git
cd orderbook
python main.py  # Run tests
```

## Core Components

### Order Class
Represents individual orders with:
- Unique order ID generation
- Side (buy/sell), price, and quantity
- Timestamp for time priority
- Cancellation flag for lazy deletion

### OrderBook Class
Main matching engine with:
- Separate bid and ask books
- Sorted price level management
- Order matching logic
- Market data calculation methods

## API Reference

### Creating an Order Book
```python
from orderbook import OrderBook

ob = OrderBook()
```

### Adding Orders
```python
# Returns order_id
order_id = ob.add_order(side='buy', price=100.0, quantity=50)
order_id = ob.add_order(side='sell', price=101.0, quantity=30)
```

### Cancelling Orders
```python
# Returns True if successful, False if order not found
success = ob.cancel_order(order_id)
```

### Market Data Queries
```python
# Get best prices
best_bid = ob.get_best_bid()  # Highest buy price
best_ask = ob.get_best_ask()  # Lowest sell price

# Calculate spread
spread = ob.get_spread()  # Ask - Bid

# Get mid-price
mid_price = ob.get_mid_price()  # (Bid + Ask) / 2

# Query volume at price level
volume = ob.get_total_volume(side='buy', price=100.0)
```

## Order Matching Logic

1. **Incoming Buy Order**: Matches against asks starting from lowest price
2. **Incoming Sell Order**: Matches against bids starting from highest price
3. **Partial Fills**: Order quantity decreases with each match
4. **Remaining Quantity**: Any unmatched portion joins the book

## Data Structure Design

### Price Level Organisation
- **Bids**: Dictionary with price as key, deque of orders as value
- **Asks**: Dictionary with price as key, deque of orders as value
- **Sorted Prices**: Maintained using bisect for O(log n) insertion

### Order Storage
- **Central Order Map**: Dictionary for O(1) order access by ID
- **Price Level Queues**: Deques for FIFO order processing

### Cancellation Strategy
Orders are flagged as cancelled (lazy deletion) and removed when reached at front of queue, ensuring O(1) cancellation time.

## Performance Characteristics

| Operation | Time Complexity |
|-----------|----------------|
| Add Order (no match) | O(log n) |
| Add Order (with matches) | O(m) where m = matched orders |
| Cancel Order | O(1) |
| Get Best Bid/Ask | O(1) |
| Get Spread/Mid | O(1) |
| Get Volume at Price | O(k) where k = orders at price |

## Example Usage

```python
from orderbook import OrderBook

# Initialise order book
ob = OrderBook()

# Add liquidity
ob.add_order('buy', 99.5, 100)
ob.add_order('buy', 99.0, 50)
ob.add_order('sell', 100.5, 100)
ob.add_order('sell', 101.0, 50)

# Check market state
print(f"Spread: {ob.get_spread()}")
print(f"Mid Price: {ob.get_mid_price()}")

# Place aggressive order (will match)
ob.add_order('buy', 100.5, 75)  # Matches 75 units at 100.5

# Cancel an order
order_id = ob.add_order('sell', 102.0, 200)
ob.cancel_order(order_id)
```

## Testing

The included `main.py` provides comprehensive testing:

- **Functionality Tests**: Order operations, matching, cancellations
- **Edge Cases**: Empty books, large prices, crossed spreads
- **Performance Tests**: 10,000+ order stress tests
- **Market Simulation**: Realistic trading scenarios
- **Volume Analysis**: Depth and liquidity testing

Run tests:
```bash
python main.py
```

## Trade Execution Output

When orders match, the system outputs trade details:
```
--- TRADE EXECUTED ---
Incoming: Order(id=5, status='Active', side='buy', qty=30, price=100.5)
Existing: Order(id=3, status='Active', side='sell', qty=100, price=100.5)
Quantity: 30 @ Price: 100.5
----------------------
```

## Limitations and Considerations

- Uses floating-point arithmetic (consider decimal for production)
- No persistence or recovery mechanisms
- Single-threaded execution
- No order modification (only add/cancel)
- No order types beyond limit orders (no market, stop, etc.)

## Future Enhancements

- Decimal arithmetic for precise financial calculations
- Market and stop order types
- Order modification functionality
- Trade history and audit trail
- Multi-threaded order processing
- Network interface for remote access
- Persistence layer for recovery

## Author

April Kidd
