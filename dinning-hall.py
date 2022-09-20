import queue
import random
import time

import requests
from flask import Flask, request
import threading
from Menu import *
from Tables import *
from Waiters import *

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

            requests.post('http://kitchen:80/order', json=payload, timeout=0.0000000001)

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
    main_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=80, debug=False, use_reloader=False),
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
