import random

def generate_multi_rssi(item_names):
    """
    Simulate RSSI for multiple items
    """
    data = {}

    for item in item_names:
        base = -50
        sequence = [base - i * random.randint(2, 5) for i in range(5)]
        data[item] = sequence

    return data