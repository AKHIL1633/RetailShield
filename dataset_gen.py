import pandas as pd
import random

NUM_ROWS = 1000

def generate_transaction():
    amount = random.randint(50, 1000)
    frequency = random.randint(1, 10)
    location_match = random.choices([1, 0], weights=[85, 15])[0]  # 15% are mismatches
    payment_method = random.randint(1, 3)
    time_of_day = random.choices([1, 0], weights=[80, 20])[0]  # 20% at odd hours
    device_known = random.choices([1, 0], weights=[90, 10])[0]
    is_return = random.choices([0, 1], weights=[85, 15])[0]
    return [amount, frequency, location_match, payment_method, time_of_day, device_known, is_return]

columns = ['amount', 'frequency', 'location_match', 'payment_method', 'time_of_day', 'device_known', 'is_return']

data = [generate_transaction() for _ in range(NUM_ROWS)]

df = pd.DataFrame(data, columns=columns)
df.to_csv('data/generated_transactions.csv', index=False)

print(f"✅ Generated {NUM_ROWS} rows in 'data/generated_transactions.csv'")
