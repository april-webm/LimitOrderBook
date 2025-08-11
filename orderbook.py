import collections
import time
import bisect
from itertools import count

# Order id generation
order_id_counter = count(1)

class Order:
    """
    Represents a single order in the limit order book.
    """
    def __init__(self, side: str, price: float, quantity: int):
        self.order_id = next(order_id_counter) # Generates a unique ID for each order
        self.side = side          # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity

        # Attributes for book-keeping and state management
        self.timestamp = time.time()  # The time the order was created for time priority
        self.is_cancelled = False     # Flag to handle cancellations

    def __repr__(self):
        """Developer-friendly string representation of the order."""
        status = "Cancelled" if self.is_cancelled else "Active"
        return (f"Order(id={self.order_id}, status='{status}', "
                f"side='{self.side}', qty={self.quantity}, price={self.price})")

    def cancel(self):
        """Sets the is_cancelled flag to True for O(1) cancellation."""
        self.is_cancelled = True

class OrderBook:
    """
    A Limit Order Book (LOB) implementation
    """
    def __init__(self):
        self.bids = {}  # For buy orders
        self.asks = {}  # For sell orders

        # Sorted lists of price levels for efficient best price retrieval
        # Bid prices are stored in descending order (highest first)
        self.bid_prices = []
        # Ask prices are stored in ascending order (lowest first)
        self.ask_prices = []

        # Order map for O(1) access to any order by its ID: {order_id: Order}
        self.order_map = {}

    def _add_to_book(self, order: Order):
        """Adds a new, unmatched order to the book."""
        # Add the order to the central order map
        self.order_map[order.order_id] = order

        if order.side == 'buy':
            price_levels = self.bids
            price_list = self.bid_prices
            # Use negative price for ascending sort to become descending
            # This allows bisect.insort to work for both lists
            price = -order.price
        else:
            price_levels = self.asks
            price_list = self.ask_prices
            price = order.price

        # If this is the first order at this price, initialize a deque
        if order.price not in price_levels:
            price_levels[order.price] = collections.deque()
            # Add the new price to the sorted price list
            bisect.insort(price_list, price)

        # Append the order to the queue for its price level (FIFO)
        price_levels[order.price].append(order)

    def _match_order(self, order: Order):
        """Tries to match an incoming order against the existing book."""
        if order.side == 'buy':
            # Check if there are any asks and if the best ask is beatable
            while self.asks and order.price >= self.ask_prices[0] and order.quantity > 0:
                best_ask_price = self.ask_prices[0]
                order_queue = self.asks[best_ask_price]
                
                # Process orders at this price level
                while order_queue and order.quantity > 0:
                    best_ask_order = order_queue[0]

                    # Discard cancelled orders
                    if best_ask_order.is_cancelled:
                        order_queue.popleft()
                        continue

                    trade_quantity = min(order.quantity, best_ask_order.quantity)
                    
                    print(f"--- TRADE EXECUTED ---\nIncoming: {order}\nExisting: {best_ask_order}\nQuantity: {trade_quantity} @ Price: {best_ask_price}\n----------------------")

                    # Update quantities
                    order.quantity -= trade_quantity
                    best_ask_order.quantity -= trade_quantity

                    # If the existing order is filled, remove it
                    if best_ask_order.quantity == 0:
                        order_queue.popleft()
                        del self.order_map[best_ask_order.order_id]
                
                # If the price level is now empty, remove it
                if not order_queue:
                    self._remove_empty_price_level('sell', best_ask_price)

        elif order.side == 'sell':
            # Check if there are bids and if the best bid is beatable
            while self.bids and order.price <= -self.bid_prices[0] and order.quantity > 0:
                best_bid_price = -self.bid_prices[0]
                order_queue = self.bids[best_bid_price]
                
                while order_queue and order.quantity > 0:
                    best_bid_order = order_queue[0]

                    if best_bid_order.is_cancelled:
                        order_queue.popleft()
                        continue
                        
                    trade_quantity = min(order.quantity, best_bid_order.quantity)

                    print(f"--- TRADE EXECUTED ---\nIncoming: {order}\nExisting: {best_bid_order}\nQuantity: {trade_quantity} @ Price: {best_bid_price}\n----------------------")

                    order.quantity -= trade_quantity
                    best_bid_order.quantity -= trade_quantity

                    if best_bid_order.quantity == 0:
                        order_queue.popleft()
                        del self.order_map[best_bid_order.order_id]

                if not order_queue:
                    self._remove_empty_price_level('buy', best_bid_price)

        # If there's remaining quantity, add the rest of the order to the book
        if order.quantity > 0:
            self._add_to_book(order)
            
    def add_order(self, side: str, price: float, quantity: int):
        """
        Main method to add a new order. It will first attempt to match
        the order and then add any remaining quantity to the book.
        """
        if side not in ('buy', 'sell'):
            raise ValueError("Side must be 'buy' or 'sell'.")
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Price must be a positive number.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
            
        order = Order(side=side, price=price, quantity=quantity)
        print(f"Received new order: {order}")
        self._match_order(order)
        return order.order_id

    def cancel_order(self, order_id: int):
        """
        Cancels an order by its ID. It flags the order as cancelled,
        allowing for O(1) time complexity .
        The order is physically removed when it reaches the front of the queue.
        """
        if order_id in self.order_map:
            order = self.order_map[order_id]
            order.cancel()
            print(f"Cancelled order: {order}")
            return True
        print(f"Error: Order ID {order_id} not found.")
        return False
        
    def _remove_empty_price_level(self, side: str, price: float):
        """Internal method to clean up an empty price level."""
        if side == 'buy':
            if price in self.bids and not self.bids[price]:
                del self.bids[price]
                self.bid_prices.remove(-price)
        elif side == 'sell':
            if price in self.asks and not self.asks[price]:
                del self.asks[price]
                self.ask_prices.remove(price)

    def get_best_bid(self) -> float | None:
        """Returns the best (highest) bid price currently available."""
        return -self.bid_prices[0] if self.bid_prices else None

    def get_best_ask(self) -> float | None:
        """Returns the best (lowest) ask price currently available."""
        return self.ask_prices[0] if self.ask_prices else None
        
    def get_spread(self) -> float | None:
        """Returns the difference between the best ask and best bid."""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid is not None and best_ask is not None:
            return best_ask - best_bid
        return None

    def get_mid_price(self) -> float | None:
        """Returns the midpoint price between the best bid and ask."""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid is not None and best_ask is not None:
            return (best_bid + best_ask) / 2
        return None

    def get_total_volume(self, side: str, price: float) -> int:
        """Returns the total volume of all active orders at a specific price level."""
        volume = 0
        if side == 'buy' and price in self.bids:
            volume = sum(order.quantity for order in self.bids[price] if not order.is_cancelled)
        elif side == 'sell' and price in self.asks:
            volume = sum(order.quantity for order in self.asks[price] if not order.is_cancelled)
        return volume