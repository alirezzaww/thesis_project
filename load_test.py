import time
import requests

# Endpoint for submitting transactions
SUBMIT_TRANSACTION_URL = "http://127.0.0.1:5000/submit_transaction"

# Number of transactions per batch and number of batches
TRANSACTIONS_PER_BATCH = 100
NUM_BATCHES = 10

# Function to simulate a batch of transactions
def send_transactions(batch_num, num_transactions):
    start_time = time.time()

    for i in range(num_transactions):
        transaction_data = {"transaction": f"Transaction-{batch_num}-{i}"}
        try:
            response = requests.post(SUBMIT_TRANSACTION_URL, json=transaction_data)
            if response.status_code != 200:
                print(f"[WARNING] Transaction {batch_num}-{i} failed with status {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Exception occurred while sending transaction {batch_num}-{i}: {e}")

    end_time = time.time()
    batch_duration = end_time - start_time
    return batch_duration

# Main load testing logic
if __name__ == "__main__":
    total_transactions = 0
    total_time = 0.0

    print("[STARTING LOAD TEST]")

    for batch_num in range(1, NUM_BATCHES + 1):
        print(f"\n[Sending batch {batch_num}/{NUM_BATCHES}]")
        batch_duration = send_transactions(batch_num, TRANSACTIONS_PER_BATCH)

        # Update metrics
        total_transactions += TRANSACTIONS_PER_BATCH
        total_time += batch_duration

        # Calculate current TPS and latency
        tps = total_transactions / total_time if total_time > 0 else 0
        avg_latency = total_time / total_transactions if total_transactions > 0 else 0

        print(f"Batch {batch_num} completed in {batch_duration:.2f} seconds")
        print(f"[Current TPS: {tps:.2f}, Average Latency: {avg_latency:.4f} seconds]")

    print("\n[LOAD TEST COMPLETE]")
    print(f"Total Transactions: {total_transactions}, Total Time: {total_time:.2f} seconds")
    print(f"Final TPS: {tps:.2f}, Final Average Latency: {avg_latency:.4f} seconds")
