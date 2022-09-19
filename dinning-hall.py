import queue
import random
import time

import requests
from flask import Flask, request
import threading

Menu = [{
    "id": 1,
    "name": "pizza",
    "preparation-time": 20,
    "complexity": 2,
    "cooking-apparatus": "oven"
}, {
    "id": 2,
    "name": "salad",
    "preparation-time": 10,
    "complexity": 1,
    "cooking-apparatus": None
}, {
    "id": 3,
    "name": "zeama",
    "preparation-time": 7,
    "complexity": 1,
    "cooking-apparatus": "stove"
}, {
    "id": 4,
    "name": "Scallop Sashimi with Meyer Lemon Confit",
    "preparation-time": 32,
    "complexity": 3,
    "cooking-apparatus": None

}, {
    "id": 5,
    "name": "Island Duck with Mulberry Mustard",
    "preparation-time": 35,
    "complexity": 3,
    "cooking-apparatus": "oven"
}, {
    "id": 6,
    "name": "Waffles",
    "preparation-time": 10,
    "complexity": 1,
    "cooking-apparatus": "stove"

}, {
    "id": 7,
    "name": "Aubergine",
    "preparation-time": 20,
    "complexity": 2,
    "cooking-apparatus": "oven"
}, {
    "id": 8,
    "name": "Lasagna",
    "preparation-time": 30,
    "complexity": 2,
    "cooking-apparatus": "oven"
}, {
    "id": 9,
    "name": "Burger",
    "preparation-time": 15,
    "complexity": 1,
    "cooking-apparatus": "stove"
}, {
    "id": 10,
    "name": "Gyros",
    "preparation-time": 15,
    "complexity": 1,
    "cooking-apparatus": None
}, {
    "id": 11,
    "name": "Kebab",
    "preparation-time": 15,
    "complexity": 1,
    "cooking-apparatus": None
}, {
    "id": 12,
    "name": "Unagi Maki",
    "preparation-time": 20,
    "complexity": 2,
    "cooking-apparatus": None
}, {
    "id": 13,
    "name": "Tobacco Chicken",
    "preparation-time": 30,
    "complexity": 2,
    "cooking-apparatus": "oven"
}]

Tables = [{
    "id": 1,
    "state": 'Free',
    "order_id": None
}, {
    "id": 2,
    "state": 'Free',
    "order_id": None
}, {
    "id": 3,
    "state": 'Free',
    "order_id": None
}, {
    "id": 4,
    "state": 'Free',
    "order_id": None
}, {
    "id": 5,
    "state": 'Free',
    "order_id": None
}, {
    "id": 6,
    "state": 'Free',
    "order_id": None
}, {
    "id": 7,
    "state": 'Free',
    "order_id": None
}, {
    "id": 8,
    "state": 'Free',
    "order_id": None
}, {
    "id": 9,
    "state": 'Free',
    "order_id": None
}, {
    "id": 10,
    "state": 'Free',
    "order_id": None
}]

Waiters = [{
    'id': 1,
    'name': 'Gordon'
}, {
    'id': 2,
    'name': 'Ramsey'
}, {
    'id': 3,
    'name': 'Jamie'
}, {
    'id': 4,
    'name': 'Oliver'
}]

Orders = queue.Queue()
Orders.join()
Time_Unit = 1
threads = []

app = Flask(__name__)


@app.route('/distribution', methods=['GET', 'POST'])
def distribution():
    order = request.get_json()
    print(f'Received order from kitchen. Order ID: {order["order_id"]}')
    return {'isSuccess': True}


# Waiter class which extends thread
class Waiter(threading.Thread):
    def __init__(self, info, *args, **kwargs):
        super(Waiter, self).__init__(*args, **kwargs)
        self.id = info['id']
        self.name = info['name']
        self.daemon = True

    # Make a loop to search for orders
    def run(self):
        while True:
            time.sleep(2)
            self.search_order()

    def search_order(self):
        try:
            Order = Orders.get()
            Orders.task_done()
            table_id = next((i for i, table in enumerate(Tables) if table['id'] == Order['table_id']), None)
            Tables[table_id]['state'] = "waiting for the order to be served"
            print(
                f'Order with Id:{Order["id"]} and items: {Order["items"]} picked up by: {threading.current_thread().name} from table {Order["table_id"]}')
            payload = dict({
                'order_id': Order['id'],
                'table_id': Order['table_id'],
                'waiter_id': self.id,
                'items': Order['items'],
                'priority': Order['priority']
            })
            time.sleep(random.randint(2, 4) * Time_Unit)

            requests.post('http://localhost:8080/order', json=payload, timeout=0.0000000001)

        except (queue.Empty, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            pass


# Class for customers which extends thread
class Customers(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(Customers, self).__init__(*args, **kwargs)

    # Make a loop of creating orders
    def run(self):
        while True:
            time.sleep(2)
            self.create_order()

    def create_order(self):
        # Check for tables with free state
        (table_id, table) = next(
            ((idx, table) for idx, table in enumerate(Tables) if table['state'] == "Free"), (None, None))
        if table_id is not None:
            # generate the random order
            order_id = int(random.randint(1, 1000))
            items = random.sample(range(1, 14), random.randint(1, 10))
            order = {
                'table_id': table['id'],
                'id': order_id,
                'items': items,
                'priority': random.randint(1, 5)
            }
            Orders.put(order)
            Tables[table_id]['state'] = "waiting to make a order"


def run_dinning_hall():
    main_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8081, debug=False, use_reloader=False),
                                   daemon=True)
    main_thread.start()
    print("Dinning-hall is running!")
    # create customer thread
    customer_thread = Customers()
    threads.append(customer_thread)
    # create waiters thread
    for _, i in enumerate(Waiters):
        waiter_thread = Waiter(i)
        threads.append(waiter_thread)

    for th in threads:
        th.start()
    for th in threads:
        th.join()

    while True:
        pass


if __name__ == '__main__':
    run_dinning_hall()
