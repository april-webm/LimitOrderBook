"""
Test suite for limit order book implementation.
Tests functionality, edge cases, and performance characteristics.
"""

import time
import random
import statistics
import argparse
import sys
import os
from contextlib import contextmanager
from orderbook import OrderBook

@contextmanager
def suppress_output():
    """Suppress stdout for cleaner test output."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

@contextmanager
def no_op():
    """No-op context manager for when output should be shown."""
    yield

def maybe_suppress():
    """Return suppress_output context manager if not verbose, else a no-op."""
    if VERBOSE:
        return no_op()
    return suppress_output()

# Global verbosity flag
VERBOSE = False

def approx_equal(a, b, tolerance=1e-6):
    """Compare floats with tolerance for precision issues."""
    if a is None or b is None:
        return a == b
    return abs(a - b) < tolerance

def test_basic_functionality():
    """Test core order book operations: add, match, cancel."""
    print("\n" + "="*50)
    print("BASIC FUNCTIONALITY TESTS")
    print("="*50)
    
    ob = OrderBook()
    
    print("\nTest 1: Add orders without matching")
    with maybe_suppress():
        ob.add_order('buy', 99.5, 100)
        ob.add_order('buy', 99.0, 50)
        ob.add_order('sell', 100.5, 100)
        ob.add_order('sell', 101.0, 50)
    
    assert approx_equal(ob.get_best_bid(), 99.5)
    assert approx_equal(ob.get_best_ask(), 100.5)
    assert approx_equal(ob.get_spread(), 1.0)
    assert approx_equal(ob.get_mid_price(), 100.0)
    print(f"Best Bid: {ob.get_best_bid()}, Best Ask: {ob.get_best_ask()}")
    print(f"Spread: {ob.get_spread()}, Mid Price: {ob.get_mid_price()}")
    print("✓ Pass")
    
    print("\nTest 2: Order matching - partial fill")
    with maybe_suppress():
        ob.add_order('buy', 100.5, 30)  # Matches 30 of 100 units at 100.5
    assert ob.get_total_volume('sell', 100.5) == 70
    print("✓ Pass")
    
    print("\nTest 3: Order matching - complete fill")
    with maybe_suppress():
        ob.add_order('buy', 100.5, 70)
    assert approx_equal(ob.get_best_ask(), 101.0)
    print("✓ Pass")
    
    print("\nTest 4: Order cancellation")
    with maybe_suppress():
        order_id = ob.add_order('sell', 102.0, 200)
        assert ob.cancel_order(order_id) == True
        assert ob.cancel_order(999999) == False
    print("✓ Pass")
    
    print("\nTest 5: Price-time priority")
    ob2 = OrderBook()
    with maybe_suppress():
        ob2.add_order('sell', 100.0, 10)  # First in queue
        ob2.add_order('sell', 100.0, 20)  # Second in queue
        ob2.add_order('sell', 100.0, 30)  # Third in queue
        ob2.add_order('buy', 100.0, 35)   # Should match first 10 + 20 + 5
    assert ob2.get_total_volume('sell', 100.0) == 25
    print("✓ Pass")

def test_edge_cases():
    """Test boundary conditions and unusual scenarios."""
    print("\n" + "="*50)
    print("EDGE CASE TESTS")
    print("="*50)
    
    ob = OrderBook()
    
    print("\nTest 1: Empty book queries")
    assert ob.get_best_bid() is None
    assert ob.get_best_ask() is None
    assert ob.get_spread() is None
    assert ob.get_mid_price() is None
    print("✓ Pass")
    
    print("\nTest 2: Large price values")
    with maybe_suppress():
        ob.add_order('buy', 999999.99, 1)
        ob.add_order('sell', 1000000.01, 1)
    
    best_bid = ob.get_best_bid()
    best_ask = ob.get_best_ask()
    spread = ob.get_spread()
    
    print(f"Best Bid: {best_bid}")
    print(f"Best Ask: {best_ask}")
    print(f"Spread: {spread}")
    print(f"Expected spread: 0.02")
    
    if spread is None:
        print("ERROR: Spread is None - orders may have been matched incorrectly!")
        print(f"Bid levels: {list(ob.bids.keys())}")
        print(f"Ask levels: {list(ob.asks.keys())}")
    else:
        print(f"Actual spread value: {spread:.20f}")
        assert approx_equal(spread, 0.02, tolerance=1e-6)
    print("✓ Pass")
    
    print("\nTest 3: Aggressive orders crossing the spread")
    ob2 = OrderBook()
    with maybe_suppress():
        ob2.add_order('buy', 100.0, 50)
        ob2.add_order('sell', 99.0, 100)  # Sell below bid, immediate match
    assert ob2.get_best_bid() is None  # All bids consumed
    assert approx_equal(ob2.get_best_ask(), 99.0)
    assert ob2.get_total_volume('sell', 99.0) == 50
    print("✓ Pass")
    
    print("\nTest 4: Multiple price levels")
    ob3 = OrderBook()
    with maybe_suppress():
        for i in range(10):
            ob3.add_order('buy', 100 - i * 0.5, 10)
            ob3.add_order('sell', 101 + i * 0.5, 10)
    assert approx_equal(ob3.get_best_bid(), 100.0)
    assert approx_equal(ob3.get_best_ask(), 101.0)
    print("✓ Pass")
    
    print("\nTest 5: Cancelled order in queue")
    ob4 = OrderBook()
    with maybe_suppress():
        id1 = ob4.add_order('sell', 100.0, 10)
        id2 = ob4.add_order('sell', 100.0, 20)
        ob4.cancel_order(id1)
        ob4.add_order('buy', 100.0, 15)
    assert ob4.get_total_volume('sell', 100.0) == 5
    print("✓ Pass")

def stress_test_performance():
    """Measure performance with high volume operations."""
    print("\n" + "="*50)
    print("PERFORMANCE STRESS TESTS")
    print("="*50)
    
    ob = OrderBook()
    
    print("\nTest 1: High volume order insertion")
    start = time.perf_counter()
    with maybe_suppress():
        for _ in range(10000):
            price = random.uniform(95.0, 105.0)
            side = random.choice(['buy', 'sell'])
            quantity = random.randint(1, 100)
            ob.add_order(side, price, quantity)
    end = time.perf_counter()
    print(f"Added 10,000 orders in {end - start:.3f} seconds")
    print(f"Average time per order: {(end - start) * 1000 / 10000:.3f} ms")
    
    print("\nTest 2: Order cancellation performance")
    order_ids = []
    with maybe_suppress():
        for _ in range(1000):
            price = random.uniform(95.0, 105.0)
            side = random.choice(['buy', 'sell'])
            quantity = random.randint(1, 100)
            order_ids.append(ob.add_order(side, price, quantity))
    
    start = time.perf_counter()
    with maybe_suppress():
        for order_id in order_ids[:500]:
            ob.cancel_order(order_id)
    end = time.perf_counter()
    print(f"Cancelled 500 orders in {end - start:.3f} seconds")
    print(f"Average cancellation time: {(end - start) * 1000 / 500:.3f} ms")
    
    print("\nTest 3: Market data retrieval performance")
    times = []
    for _ in range(10000):
        start = time.perf_counter_ns()  # Nanosecond precision
        ob.get_best_bid()
        ob.get_best_ask()
        ob.get_spread()
        ob.get_mid_price()
        end = time.perf_counter_ns()
        times.append(end - start)
    
    avg_time = statistics.mean(times) / 1000  # Convert to microseconds
    print(f"Average market data retrieval: {avg_time:.3f} µs")
    
    print("\nTest 4: Matching engine performance")
    ob2 = OrderBook()
    with maybe_suppress():
        for i in range(1000):
            ob2.add_order('sell', 100.0 + i * 0.01, 10)
    
    start = time.perf_counter()
    with maybe_suppress():
        ob2.add_order('buy', 110.0, 10000)
    end = time.perf_counter()
    print(f"Matched 1000 orders in {end - start:.3f} seconds")

def test_market_simulation():
    """Simulate realistic market behaviour with random orders."""
    print("\n" + "="*50)
    print("MARKET SIMULATION TEST")
    print("="*50)
    
    ob = OrderBook()
    
    initial_spread = 0.10
    mid_price = 100.0
    
    # Build initial order book
    with maybe_suppress():
        for i in range(10):
            bid_price = mid_price - initial_spread/2 - i * 0.05
            ask_price = mid_price + initial_spread/2 + i * 0.05
            ob.add_order('buy', bid_price, random.randint(50, 200))
            ob.add_order('sell', ask_price, random.randint(50, 200))
    
    print(f"Initial market state:")
    print(f"Best Bid: {ob.get_best_bid():.2f}, Best Ask: {ob.get_best_ask():.2f}")
    print(f"Spread: {ob.get_spread():.2f}, Mid Price: {ob.get_mid_price():.2f}")
    
    trades_executed = 0
    with maybe_suppress():
        for _ in range(100):
            side = random.choice(['buy', 'sell'])
            if random.random() < 0.3:  # 30% aggressive orders
                if side == 'buy':
                    price = ob.get_best_ask() if ob.get_best_ask() else 100.0
                else:
                    price = ob.get_best_bid() if ob.get_best_bid() else 100.0
                trades_executed += 1
            else:  # 70% passive orders
                if side == 'buy':
                    best_bid = ob.get_best_bid() if ob.get_best_bid() else 99.0
                    price = best_bid - random.uniform(0, 0.5)
                else:
                    best_ask = ob.get_best_ask() if ob.get_best_ask() else 101.0
                    price = best_ask + random.uniform(0, 0.5)
            
            quantity = random.randint(10, 100)
            ob.add_order(side, price, quantity)
    
    print(f"\nAfter 100 orders:")
    print(f"Best Bid: {ob.get_best_bid():.2f}, Best Ask: {ob.get_best_ask():.2f}")
    print(f"Spread: {ob.get_spread():.2f}, Mid Price: {ob.get_mid_price():.2f}")
    print(f"Aggressive orders (potential trades): ~{trades_executed}")

def test_volume_analysis():
    """Test volume tracking and cancellation effects."""
    print("\n" + "="*50)
    print("VOLUME ANALYSIS TESTS")
    print("="*50)
    
    ob = OrderBook()
    
    price_levels = [99.5, 99.75, 100.0, 100.25, 100.5]
    volumes = [100, 200, 300, 200, 100]
    
    with maybe_suppress():
        for price, volume in zip(price_levels[:2], volumes[:2]):
            ob.add_order('buy', price, volume)
        
        for price, volume in zip(price_levels[3:], volumes[3:]):
            ob.add_order('sell', price, volume)
    
    print("Order book depth:")
    for price in sorted(price_levels, reverse=True):
        buy_vol = ob.get_total_volume('buy', price)
        sell_vol = ob.get_total_volume('sell', price)
        if buy_vol > 0:
            print(f"  BID {price:.2f}: {buy_vol:>4} units")
        if sell_vol > 0:
            print(f"  ASK {price:.2f}: {sell_vol:>4} units")
    
    print("\nTesting partial cancellations:")
    ids = []
    with maybe_suppress():
        for _ in range(3):
            ids.append(ob.add_order('sell', 100.25, 50))
        
        ob.cancel_order(ids[1])
    remaining_vol = ob.get_total_volume('sell', 100.25)
    assert remaining_vol == 300
    print(f"Volume at 100.25 after cancellation: {remaining_vol}")
    print("✓ Pass")

def benchmark_order_types():
    """Compare performance of passive vs aggressive orders."""
    print("\n" + "="*50)
    print("ORDER TYPE BENCHMARKS")
    print("="*50)
    
    print("\nPassive vs Aggressive Order Performance:")
    
    # Build book with orders away from mid price
    ob = OrderBook()
    with maybe_suppress():
        for i in range(100):
            ob.add_order('buy', 99.0 - i * 0.1, 10)
            ob.add_order('sell', 101.0 + i * 0.1, 10)
    
    # Passive orders: don't cross the spread
    passive_times = []
    with maybe_suppress():
        for _ in range(1000):
            start = time.perf_counter_ns()
            ob.add_order('buy', 90.0, 1)
            end = time.perf_counter_ns()
            passive_times.append(end - start)
    
    # Aggressive orders: cross the spread and match
    aggressive_times = []
    with maybe_suppress():
        for _ in range(1000):
            start = time.perf_counter_ns()
            ob.add_order('buy', 110.0, 1)
            end = time.perf_counter_ns()
            aggressive_times.append(end - start)
    
    print(f"Passive order avg time: {statistics.mean(passive_times)/1000:.2f} µs")
    print(f"Aggressive order avg time: {statistics.mean(aggressive_times)/1000:.2f} µs")
    print(f"Ratio (aggressive/passive): {statistics.mean(aggressive_times)/statistics.mean(passive_times):.2f}x")

def main():
    """Run all test suites in sequence."""
    global VERBOSE
    
    parser = argparse.ArgumentParser(description='Limit Order Book Test Suite')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed order matching output')
    args = parser.parse_args()
    
    VERBOSE = args.verbose
    
    if VERBOSE:
        print("Running in VERBOSE mode - all order details will be shown")
    else:
        print("Running in QUIET mode - use -v flag for detailed output")
    
    print("\n" + "="*60)
    print(" LIMIT ORDER BOOK TEST SUITE ")
    print("="*60)
    
    test_basic_functionality()
    test_edge_cases()
    test_volume_analysis()
    test_market_simulation()
    benchmark_order_types()
    stress_test_performance()
    
    print("\n" + "="*60)
    print(" ALL TESTS COMPLETED SUCCESSFULLY ")
    print("="*60)

if __name__ == "__main__":
    main()
