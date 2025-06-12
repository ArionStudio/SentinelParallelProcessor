import multiprocessing as mp
from multiprocessing.managers import BaseManager

class QueueManager(BaseManager):
    pass

def run_server():
    data_queue = mp.Queue()
    results_queue = mp.Queue()
    
    QueueManager.register('get_data_queue', callable=lambda: data_queue)
    QueueManager.register('get_results_queue', callable=lambda: results_queue)
    
    manager = QueueManager(address=('localhost', 50000), authkey=b'secret')
    server = manager.get_server()
    
    print("Serwer uruchomiony. Oczekiwanie na połączenia...")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
