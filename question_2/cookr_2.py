import json
from geopy.distance import geodesic
import matplotlib.pyplot as plt

class Order:
    def __init__(self, order_id, kitchen_location, customer_location, ready_time):
        self.order_id = order_id
        self.kitchen_location = kitchen_location
        self.customer_location = customer_location
        self.ready_time = ready_time

class Rider:
    def __init__(self, rider_id):
        self.rider_id = rider_id
        self.orders = []

def load_orders_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        orders_data = data.get('orders', [])
        orders = []
        for order_data in orders_data:
            order = Order(order_data['order_id'], order_data['kitchen_location'], order_data['customer_location'], order_data['ready_time'])
            orders.append(order)
        return orders

def assign_orders_to_riders(orders):
    riders = []
    for order in orders:
        assigned = False
        for rider in riders:
            if can_assign_order(order, rider):
                rider.orders.append(order)
                assigned = True
                break
        if not assigned:
            new_rider = Rider(len(riders) + 1)
            new_rider.orders.append(order)
            riders.append(new_rider)
    return riders


def distance(point1, point2):
    p1=(point1['x'],point1['y'])
    p2=(point2['x'],point2['y'])
    distance_meters = geodesic(p1, p2).meters
    distance_km = distance_meters / 1000000  # Convert meters to kilometers
    return distance_km

def can_assign_order(order, rider):
    for existing_order in rider.orders:
        # RULE 1: Orders from same kitchen to same customer within 10 mins ready time difference
        if order.kitchen_location == existing_order.kitchen_location \
                and order.customer_location == existing_order.customer_location \
                and abs(order.ready_time - existing_order.ready_time) <= 10:
            return True

        # RULE 2/4/5: Orders for same customer from different kitchens within 1km and 10 mins ready time difference
        if order.customer_location == existing_order.customer_location:
            kitchen_distance = distance(order.kitchen_location, existing_order.kitchen_location)
            if kitchen_distance <= 1 and abs(order.ready_time - existing_order.ready_time) <= 10:
                return True

        # RULE 3: Orders from same kitchen to different customers
        if order.kitchen_location == existing_order.kitchen_location \
                and order.customer_location != existing_order.customer_location \
                and abs(order.ready_time - existing_order.ready_time) <= 10:
            customer_distance = distance(order.customer_location, existing_order.customer_location)
            kitchen_to_customer1 = distance(order.kitchen_location, order.customer_location)
            kitchen_to_customer2 = distance(order.kitchen_location, existing_order.customer_location)
            # Check if customer 2 is closer to the kitchen than customer 1 or vice versa
            if customer_distance <= kitchen_to_customer1 or customer_distance <= kitchen_to_customer2:
                return True

        # RULE 6: Orders from different kitchens to the same customer
        if order.customer_location == existing_order.customer_location \
                and order.kitchen_location != existing_order.kitchen_location \
                and abs(order.ready_time - existing_order.ready_time) <= 10:
            kitchen_distance = distance(order.kitchen_location, existing_order.kitchen_location)
            customer_to_kitchen1 = distance(order.customer_location, order.kitchen_location)
            customer_to_kitchen2 = distance(order.customer_location, existing_order.kitchen_location)
            # Check if kitchen 2 is on the way to the customer from kitchen 1
            if kitchen_distance <= customer_to_kitchen1 and kitchen_distance <= customer_to_kitchen2:
                return True
        
        # RULE 7: Orders from different kitchens to different customers
        if order.kitchen_location != existing_order.kitchen_location \
                and order.customer_location != existing_order.customer_location \
                and abs(order.ready_time - existing_order.ready_time) <= 10:
            kitchen_distance = distance(order.kitchen_location, existing_order.kitchen_location)
            customer_to_kitchen1 = distance(order.customer_location, order.kitchen_location)
            customer_to_kitchen2 = distance(order.customer_location, existing_order.kitchen_location)
            last_order = rider.orders[-1] if rider.orders else None
            # Scenario 1: kitchen1 -> kitchen2 -> customer1 -> customer2
            if last_order \
                    and distance(last_order.kitchen_location, order.kitchen_location) >= 10 \
                    and distance(order.kitchen_location, order.customer_location) <= 10 \
                    and distance(order.customer_location, last_order.customer_location) <= 10 \
                    and abs(order.ready_time - last_order.ready_time) <= 10:
                return True
            # Scenario 2: kitchen1 -> kitchen2 -> customer2 -> customer1
            if last_order \
                    and distance(last_order.kitchen_location, order.kitchen_location) >= 10 \
                    and distance(order.kitchen_location, last_order.customer_location) <= 10 \
                    and distance(order.customer_location, last_order.customer_location) <= 10 \
                    and abs(order.ready_time - last_order.ready_time) <= 10:
                return True
        
        # RULE 8: Orders from same kitchen to different customers based on distance
        if order.kitchen_location == existing_order.kitchen_location \
                and order.customer_location != existing_order.customer_location \
                and abs(order.ready_time - existing_order.ready_time) <= 10:
            kitchen_to_customer1 = distance(order.kitchen_location, order.customer_location)
            kitchen_to_customer2 = distance(order.kitchen_location, existing_order.customer_location)
            # Check if customer 2 is closer to the kitchen than customer 1 or vice versa
            if kitchen_to_customer2 < kitchen_to_customer1 or kitchen_to_customer1 < kitchen_to_customer2:
                return True

    return False

def visualize_assignment(riders):
    print("Riders' Assignment Visualization:")
    for rider in riders:
        print(f"Rider {rider.rider_id} assigned orders:")
        for order in rider.orders:
            print(f"Order:{order.order_id} Ready Time: {order.ready_time}")
        print()
        all_kitchen_locations = [order.kitchen_location for order in rider.orders]
        all_customer_locations = [order.customer_location for order in rider.orders]
        visualize_locations(all_kitchen_locations, all_customer_locations)
        print()

def visualize_locations(kitchen_locations, customer_locations):
    kitchen_x = [location['x'] for location in kitchen_locations]
    kitchen_y = [location['y'] for location in kitchen_locations]
    customer_x = [location['x'] for location in customer_locations]
    customer_y = [location['y'] for location in customer_locations]

    plt.scatter(kitchen_x, kitchen_y, marker='*', color='blue', label='Kitchen')
    plt.scatter(customer_x, customer_y, marker='o', color='red', label='Customer')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Order Location Visualization')
    plt.legend()
    plt.show()

orders = load_orders_from_json('data.json')
riders = assign_orders_to_riders(orders)
visualize_assignment(riders)


