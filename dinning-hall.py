from flask import Flask
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

Orders = []


app = Flask(__name__)


def run_dinning_hall():
    main_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8081, debug=False, use_reloader=False),
                                   daemon=True)
    main_thread.start()
    print("Dinning-hall is running!")

    while True:
        pass


if __name__ == '__main__':
    run_dinning_hall()
