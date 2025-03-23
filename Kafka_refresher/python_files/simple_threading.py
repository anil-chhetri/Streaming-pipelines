import threading
import time

def print_numbers(name):
    """Function that prints numbers 1-5 with the thread name"""
    for i in range(1, 6):
        print(f"Thread {name}: number {i}")
        time.sleep(1)  # Pause for 1 second

# Create three threads
thread1 = threading.Thread(target=print_numbers, args=("A",))
thread2 = threading.Thread(target=print_numbers, args=("B",))
thread3 = threading.Thread(target=print_numbers, args=("C",))

# Start all threads
thread1.start()
thread2.start()
thread3.start()

print("All threads started!")

# Wait for all threads to complete
thread1.join()
thread2.join()
thread3.join()

print("All threads finished!")