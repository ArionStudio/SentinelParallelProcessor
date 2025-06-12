from multiprocessing.managers import BaseManager
import time

class QueueManager(BaseManager):
    pass


def digit_count(data):
    return sum(1 for char in data if char.isdigit())

def run_worker():
    QueueManager.register('get_data_queue')
    QueueManager.register('get_results_queue')
    
    manager = QueueManager(address=('localhost', 50000), authkey=b'secret')
    
    try:
        manager.connect()
        print("Connected")
    except ConnectionRefusedError:
        print("Cannot connect to the server.")
        return
    
    data_queue = manager.get_data_queue()
    results_queue = manager.get_results_queue()
    
    print("Worker has enter data loop...")

    i = 1
    
    while True:
        try:
            if data_queue.empty():
                time.sleep(0.7)
                continue
            
            data = data_queue.get(True, 60)  
            
            if data == None:
                print("Worker work end")
                break
                
            print(f"Worker in process")
            results_queue.put(digit_count(data))
            print(f"Worker end it's work no: {i}, result: {digit_count(data)}")
            i += 1
            
        except Exception as e:
            print(f"Error in worker: {e}")
            time.sleep(1)
    
    print("End of work")

if __name__ == "__main__":
    run_worker()
