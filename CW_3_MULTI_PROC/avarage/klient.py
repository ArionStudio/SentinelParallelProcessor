from multiprocessing.managers import BaseManager
import time

class QueueManager(BaseManager):
    pass

def get_data(filename):
    data = ""
    try:
        with open(filename, 'r') as file:
            data = file.read()
    except Exception as e:
        print("Error while reading file", e)
        exit(1)
    return data

def get_num_of_lines(filename):
    num = 0
    try:
        with open(filename, 'r') as file:
            for i in file:
                num += 1
    except Exception as e:
        print("Error while reading file")
        exit(1)
    return num

def split_chunks(array, num):
    if not array:
        print("Data is not an array")
    
    if num <= 0:
        print("Chunks number > 0")
    
    if(num > len(array)):
        print("We lower number of chunks to array size")
    num_chunks = min(num, len(array))
    chunk_size = len(array) // num
    remainder = len(array) % num

    chunks = []
    start = 0

    for i in range(num_chunks):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunks.append(array[start:end])
        start=end
    return chunks

def digit_count(data):
    return sum(1 for char in data if char.isdigit())

def run_client():
    num_worker = 4
    QueueManager.register('get_data_queue')
    QueueManager.register('get_results_queue')
    
    manager = QueueManager(address=('localhost', 50000), authkey=b'secret')
    
    try:
        manager.connect()
        print("Conected")
    except ConnectionRefusedError:
        print("Error when connecting to a server")
        return
    
    data_queue = manager.get_data_queue()
    results_queue = manager.get_results_queue()

    print("Reading data from file")
    data = get_data('data.txt')
    print((digit_count(data)))
    num_of_lines = get_num_of_lines('data.txt')
    print("Spliting data into chunks")
    chunks = split_chunks(data, num_worker)
    
    print(f"Client will send {num_worker} to queue...")
    
    for i in range(num_worker):
        data_queue.put(chunks[i])
    data_queue.put(None)
    
    print('Client complete sending data.')
    
    print("Client is waiting for results...")
    digit_sum = 0
    try:
        for i in range(num_worker):
            if(results_queue.empty()):
                print('Queue is empty, waiting for more data')
                time.sleep(0.5)
            result = results_queue.get(True, 60)
            digit_sum += result
            print(f"Client recived result: {result}")
    except Exception as e:
        print(f"Exception occured {e}")
        exit(1)

    print(f"Avg digit in line {digit_sum / num_of_lines}, in {num_of_lines} lines")    
    
    print("Client end it's work")

if __name__ == "__main__":
    run_client()
