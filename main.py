import time
import random
import statistics
from orderbook import OrderBook

def approx_equal(a, b, tolerance=1e-6):
    if a is None or b is None:
        return a == b
    return abs(a - b) < tolerance

def test_basic_functionality():
    print("\n" + "="*50)
    print("BASIC FUNCTIONALITY TESTS")
    print("="*50)
    
    ob = OrderBook()
    
    print("\nTest 1: Add orders without matching")
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
    ob.add_order('buy', 100.5, 30)
    assert ob.get_total_volume('sell', 100.5) == 70
    print("✓ Pass")
    
    print("\nTest 3: Order matching - complete fill")
    ob.add_order('buy', 100.5, 70)
    assert approx_equal(ob.get_best_ask(), 101.0)
    print("✓ Pass")
    
    print("\nTest 4: Order cancellation")
    order_id = ob.add_order('sell', 102.0, 200)
    assert ob.cancel_order(order_id) == True
    assert ob.cancel_order(999999) == False
    print("✓ Pass")
    
    print("\nTest 5: Price-time priority")
    ob2 = OrderBook()
    ob2.add_order('sell', 100.0, 10)
    ob2.add_order('sell', 100.0, 20)
    ob2.add_order('sell', 100.0, 30)
    ob2.add_order('buy', 100.0, 35)
    assert ob2.get_total_volume('sell', 100.0) == 25
    print("✓ Pass")

def test_edge_cases():
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
    ob2.add_order('buy', 100.0, 50)
    ob2.add_order('sell', 99.0, 100)
    assert ob2.get_best_bid() is None
    assert approx_equal(ob2.get_best_ask(), 99.0)
    assert ob2.get_total_volume('sell', 99.0) == 50
    print("✓ Pass")
    
    print("\nTest 4: Multiple price levels")
    ob3 = OrderBook()
    for i in range(10):
        ob3.add_order('buy', 100 - i * 0.5, 10)
        ob3.add_order('sell', 101 + i * 0.5, 10)
    assert approx_equal(ob3.get_best_bid(), 100.0)
    assert approx_equal(ob3.get_best_ask(), 101.0)
    print("✓ Pass")
    
    print("\nTest 5: Cancelled order in queue")
    ob4 = OrderBook()
    id1 = ob4.add_order('sell', 100.0, 10)
    id2 = ob4.add_order('sell', 100.0, 20)
    ob4.cancel_order(id1)
    ob4.add_order('buy', 100.0, 15)
    assert ob4.get_total_volume('sell', 100.0) == 5
    print("✓ Pass")

def stress_test_performance():
    print("\n" + "="*50)
    print("PERFORMANCE STRESS TESTS")
    print("="*50)
    
    ob = OrderBook()
    
    print("\nTest 1: High volume order insertion")
    start = time.perf_counter()
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
    for _ in range(1000):
        price = random.uniform(95.0, 105.0)
        side = random.choice(['buy', 'sell'])
        quantity = random.randint(1, 100)
        order_ids.append(ob.add_order(side, price, quantity))
    
    start = time.perf_counter()
    for order_id in order_ids[:500]:
        ob.cancel_order(order_id)
    end = time.perf_counter()
    print(f"Cancelled 500 orders in {end - start:.3f} seconds")
    print(f"Average cancellation time: {(end - start) * 1000 / 500:.3f} ms")
    
    print("\nTest 3: Market data retrieval performance")
    times = []
    for _ in range(10000):
        start = time.perf_counter_ns()
        ob.get_best_bid()
        ob.get_best_ask()
        ob.get_spread()
        ob.get_mid_price()
        end = time.perf_counter_ns()
        times.append(end - start)
    
    avg_time = statistics.mean(times) / 1000
    print(f"Average market data retrieval: {avg_time:.3f} µs")
    
    print("\nTest 4: Matching engine performance")
    ob2 = OrderBook()
    for i in range(1000):
        ob2.add_order('sell', 100.0 + i * 0.01, 10)
    
    start = time.perf_counter()
    ob2.add_order('buy', 110.0, 10000)
    end = time.perf_counter()
    print(f"Matched 1000 orders in {end - start:.3f} seconds")

def test_market_simulation():
    print("\n" + "="*50)
    print("MARKET SIMULATION TEST")
    print("="*50)
    
    ob = OrderBook()
    
    initial_spread = 0.10
    mid_price = 100.0
    
    for i in range(10):
        bid_price = mid_price - initial_spread/2 - i * 0.05
        ask_price = mid_price + initial_spread/2 + i * 0.05
        ob.add_order('buy', bid_price, random.randint(50, 200))
        ob.add_order('sell', ask_price, random.randint(50, 200))
    
    print(f"Initial market state:")
    print(f"Best Bid: {ob.get_best_bid():.2f}, Best Ask: {ob.get_best_ask():.2f}")
    print(f"Spread: {ob.get_spread():.2f}, Mid Price: {ob.get_mid_price():.2f}")
    
    trades_executed = 0
    for _ in range(100):
        side = random.choice(['buy', 'sell'])
        if random.random() < 0.3:
            if side == 'buy':
                price = ob.get_best_ask() if ob.get_best_ask() else 100.0
            else:
                price = ob.get_best_bid() if ob.get_best_bid() else 100.0
            trades_executed += 1
        else:
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
    print("\n" + "="*50)
    print("VOLUME ANALYSIS TESTS")
    print("="*50)
    
    ob = OrderBook()
    
    price_levels = [99.5, 99.75, 100.0, 100.25, 100.5]
    volumes = [100, 200, 300, 200, 100]
    
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
    for _ in range(3):
        ids.append(ob.add_order('sell', 100.25, 50))
    
    ob.cancel_order(ids[1])
    remaining_vol = ob.get_total_volume('sell', 100.25)
    assert remaining_vol == 300
    print(f"Volume at 100.25 after cancellation: {remaining_vol}")
    print("✓ Pass")

def benchmark_order_types():
    print("\n" + "="*50)
    print("ORDER TYPE BENCHMARKS")
    print("="*50)
    
    print("\nPassive vs Aggressive Order Performance:")
    
    ob = OrderBook()
    for i in range(100):
        ob.add_order('buy', 99.0 - i * 0.1, 10)
        ob.add_order('sell', 101.0 + i * 0.1, 10)
    
    passive_times = []
    for _ in range(1000):
        start = time.perf_counter_ns()
        ob.add_order('buy', 90.0, 1)
        end = time.perf_counter_ns()
        passive_times.append(end - start)
    
    aggressive_times = []
    for _ in range(1000):
        start = time.perf_counter_ns()
        ob.add_order('buy', 110.0, 1)
        end = time.perf_counter_ns()
        aggressive_times.append(end - start)
    
    print(f"Passive order avg time: {statistics.mean(passive_times)/1000:.2f} µs")
    print(f"Aggressive order avg time: {statistics.mean(aggressive_times)/1000:.2f} µs")
    print(f"Ratio (aggressive/passive): {statistics.mean(aggressive_times)/statistics.mean(passive_times):.2f}x")

def main():
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