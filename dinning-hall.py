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
Orders_stack = []
Orders_done = []
Order_rating = []
Time_Unit = 1
threads = []

app = Flask(__name__)


@app.route('/distribution', methods=['GET', 'POST'])
def distribution():
    order = request.get_json()
    print(f'Received order from kitchen. Order ID: {order["order_id"]}')
    table_id = next((i for i, table in enumerate(Tables) if table['id'] == order['table_id']), None)
    Tables[table_id]['state'] = "waiting for the order to be served"
    waiter_thread: Waiter = next((w for w in threads if type(w) == Waiter and w.id == order['waiter_id']), None)
    waiter_thread.serve_order(order)
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
            self.search_order()

    def search_order(self):
        try:
            Order = Orders.get()
            Orders.task_done()
            table_id = next((i for i, table in enumerate(Tables) if table['id'] == Order['table_id']), None)
            Tables[table_id]['state'] = "waiting for the order to be served"
            print(
                f'Order with Id:{Order["id"]}, priority: {Order["priority"]} and items: {Order["items"]} picked up by: {threading.current_thread().name} from table {Order["table_id"]}')
            payload = dict({
                'order_id': Order['id'],
                'table_id': Order['table_id'],
                'waiter_id': self.id,
                'items': Order['items'],
                'priority': Order['priority'],
                'max_wait': Order['max_wait'],
                'time_start': time.time()
            })
            time.sleep(random.randint(2, 4) * Time_Unit)

            requests.post('http://kitchen:80/order', json=payload, timeout=0.0000000001)

        except (queue.Empty, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            pass

    def serve_order(self, ordered_order):
        received_order = next(
            (order for i, order in enumerate(Orders_stack) if order['id'] == ordered_order['order_id']), None)
        if received_order is not None and received_order['items'].sort() == ordered_order['items'].sort():
            table_id = next((i for i, table in enumerate(Tables) if table['id'] == ordered_order['table_id']),
                            None)
            Tables[table_id]['state'] = "Free"
            order_served = int(time.time())
            order_picked_up = int(ordered_order['time_start'])
            Total_order_time = order_served - order_picked_up
            
            order_stars = {'order_id': ordered_order['order_id']}
            if ordered_order['max_wait'] > Total_order_time:
                order_stars['star'] = 5
            elif ordered_order['max_wait'] * 1.1 > Total_order_time:
                order_stars['star'] = 4
            elif ordered_order['max_wait'] * 1.2 > Total_order_time:
                order_stars['star'] = 3
            elif ordered_order['max_wait'] * 1.3 > Total_order_time:
                order_stars['star'] = 2
            elif ordered_order['max_wait'] * 1.4 > Total_order_time:
                order_stars['star'] = 1
            else:
                order_stars['star'] = 0

            Order_rating.append(order_stars)
            sum_stars = sum(feedback['star'] for feedback in Order_rating)
            avg = float(sum_stars / len(Order_rating))

            
            served_order = {**ordered_order, 'Serving_time': Total_order_time, 'status': 'DONE', 'Stars_feedback':order_stars}
            Orders_done.append(served_order)
            print( f'Order served: \n'
                      f'Order Id: {served_order["order_id"]}\n'
                      f'Table Id: {served_order["table_id"]}\n'
                      f'Waiter Id: {served_order["waiter_id"]}\n'
                      f'Items: {served_order["items"]}\n'
                      f'Priority: {served_order["priority"]}\n'
                      f'Max Wait: {served_order["max_wait"]}\n'
                      f'Waiting time: {served_order["Serving_time"]}\n'
                      f'Stars: {served_order["Stars_feedback"]}\n'
                      f'Restaurant rating: {avg}'
                      )
# Class for customers which extends thread
class Customers(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(Customers, self).__init__(*args, **kwargs)

    # Make a loop of creating orders
    def run(self):
        while True:
            time.sleep(1)
            self.create_order()

    def create_order(self):
        # Check for tables with free state
        (table_id, table) = next(
            ((idx, table) for idx, table in enumerate(Tables) if table['state'] == "Free"), (None, None))
        if table_id is not None:
            wait_time = 0 
            # generate the random order
            order_id = int(random.randint(1, 1000))
            items = []
            for i in range(random.randint(1, 10)):
                choice = random.choice(Menu)
                if wait_time < choice['preparation-time']:
                    wait_time = choice['preparation-time']
                items.append(choice['id'])
            wait_time = wait_time * 1.3
            order = {
                'table_id': table['id'],
                'id': order_id,
                'items': items,
                'priority': random.randint(1, 5),
                'max_wait': wait_time
            }
            Orders.put(order)
            Orders_stack.append(order)
            Tables[table_id]['state'] = "waiting to make a order"
            Tables[table_id]['order_id'] = order_id
        else:
            time.sleep(random.randint(2, 10) * Time_Unit)
            idxs = [table for table in Tables if table['state'] == "Free"]
            if len(idxs):
                rand_idx = random.randrange(len(idxs))
                Tables[rand_idx]['state'] = "Free"


def run_dinning_hall():
    main_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=80, debug=False, use_reloader=False),
                                   daemon=True)
    threads.append(main_thread)
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


if __name__ == '__main__':
    run_dinning_hall()