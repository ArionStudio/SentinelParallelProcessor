from multiprocessing.managers import BaseManager
import multiprocessing.pool
import time
import multiprocessing

class QueueManager(BaseManager):
    pass

def multiplyVectors(X, Y):
    sum = 0
    for i in range(len(X)):
        sum += float(X[i][0]) * float(Y[i])  
    return sum

def task(X, data):
    results = []
    for Y in data:
        result = multiplyVectors(X, Y)
        results.append(result)
    return results

def run_worker():
    manager = None
    pool = None
    try:
        QueueManager.register('get_data_queue')
        QueueManager.register('get_results_queue')
        
        manager = QueueManager(address=('localhost', 50000), authkey=b'secret')
        
        try:
            manager.connect()
            print("Connected")
        except ConnectionRefusedError:
            print("Cannot connect to the server. Make sure server is running.")
            return
        
        data_queue = manager.get_data_queue()
        results_queue = manager.get_results_queue()
        
        try:
            initial_data = data_queue.get(True, 60)
            if initial_data is None:
                print("Received empty initial data")
                return
                
            taskNumber = initial_data[0]
            X = initial_data[1]
            
            if not X or taskNumber <= 0:
                print("Invalid initial data received")
                results_queue.put("Error")
                return
                
            print(f"Worker has {taskNumber} tasks.")
            print("Worker has entered data loop...")

            pool = multiprocessing.Pool(processes=taskNumber)
            taskIdCounter = 0
            row_count = 0
            
            while True:
                try:
                    if data_queue.empty():
                        time.sleep(0.7)
                        continue
                        
                    data = data_queue.get(True, 60)
                    
                    if data is None:
                        print("Worker work end")
                        break

                    print(f"Worker add process no: {taskIdCounter}")
                    result = pool.apply_async(task, (X, data))
                    
                    try:
                        result_data = result.get(timeout=60)
                        results_queue.put((row_count, result_data))
                        row_count += len(result_data)
                        print(f"Worker has completed process no: {taskIdCounter}")
                        taskIdCounter += 1
                    except multiprocessing.TimeoutError:
                        print("Task computation timed out")
                        results_queue.put("Error")
                        break
                        
                except Exception as e:
                    print(f"Error processing task: {str(e)}")
                    results_queue.put("Error")
                    break
                    
        except Exception as e:
            print(f"Error in main processing loop: {str(e)}")
            try:
                results_queue.put("Error")
            except:
                pass
            return
            
    except Exception as e:
        print(f"Critical error: {str(e)}")
        return
        
    finally:
        if pool:
            pool.close()
            pool.join()
        try:
            results_queue.put(None)
        except:
            pass
        print("End of work")

if __name__ == "__main__":
    run_worker()
