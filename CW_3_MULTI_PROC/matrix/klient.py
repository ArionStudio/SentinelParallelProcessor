from multiprocessing.managers import BaseManager
import sys


class QueueManager(BaseManager):
    pass

def read_matrix(filename):
    with open(filename, 'r') as f:
        rows = int(f.readline())
        cols = int(f.readline())
        data = []
        for _ in range(rows):
            row = []
            for _ in range(cols):
                val = float(f.readline())
                row.append(val)
            data.append(row)
    return data, rows, cols


def split_tasks(matrix, num_tasks):
    total_rows = len(matrix)
    size_of_task = total_rows // num_tasks
    remainder = total_rows % num_tasks

    tasks = []
    start = 0
    for i in range(num_tasks):
        end = start + size_of_task + (1 if i < remainder else 0)
        task_rows = matrix[start:end]
        tasks.append(task_rows)
        start = end
    return tasks


def run_client(task_number, file_A, file_X):
    manager = None
    try:
        QueueManager.register('get_data_queue')
        QueueManager.register('get_results_queue')

        manager = QueueManager(address=('localhost', 50000), authkey=b'secret')
        try:
            manager.connect()
            print("Connected to server")
        except ConnectionRefusedError:
            print("Error: Could not connect to server. Make sure server is running.")
            return
        
        in_queue = manager.get_data_queue()
        out_queue = manager.get_results_queue()

        try:
            matrix_A, rows_A, cols_A = read_matrix(file_A)
            vector_X, rows_X, cols_X = read_matrix(file_X)
        except FileNotFoundError as e:
            print(f"Error: Input file not found - {str(e)}")
            return
        except ValueError as e:
            print(f"Error: Invalid file format - {str(e)}")
            return

        if cols_A != rows_X:
            print(f"Matrix size mismatch! Matrix A columns ({cols_A}) != Vector X rows ({rows_X})")
            return

        number_of_tasks = min(32, rows_A, task_number)
        tasks = split_tasks(matrix_A, number_of_tasks)

        try:
            in_queue.put((number_of_tasks, vector_X))
            print("Sent vector X")

            for task in tasks:
                in_queue.put(task)
            print(f"Sent {len(tasks)} tasks")

            in_queue.put(None)

            print("Waiting for results...")

            result_map = {}
            tasks_completed = 0
            
            while tasks_completed < len(tasks):
                try:
                    result = out_queue.get(True, 60) 
                    if result is None:
                        print("Worker signaled completion")
                        break
                    if result == "Error":
                        print("Worker signaled error")
                        return

                    row_start_id, result_list = result
                    tasks_completed += 1
                    print(f"Received result {tasks_completed}/{len(tasks)}")

                    for i, val in enumerate(result_list):
                        result_map[row_start_id + i] = val
                        
                except TimeoutError:
                    print("Timeout waiting for results. Worker might be stuck.")
                    return

            if len(result_map) != rows_A:
                print(f"Error: Missing results. Expected {rows_A} results, got {len(result_map)}")
                return

            try:
                result_vector = [result_map[i] for i in range(rows_A)]
                output_filename = "result_vector.txt"
                with open(output_filename, 'w') as f:
                    f.write(f"{len(result_vector)}\n")
                    f.write("1\n")
                    for val in result_vector:
                        f.write(f"{val}\n")
                print(f"\nResult vector has been saved to {output_filename}")
            except IOError as e:
                print(f"Error saving results to file: {str(e)}")
                return

        except Exception as e:
            print(f"Unexpected error during processing: {str(e)}")
            try:
                in_queue.put(None)
            except:
                pass
            return

    except Exception as e:
        print(f"Critical error: {str(e)}")
        return


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <task_number> <file_A> <file_X>")
        sys.exit(1)
    task_number = int(sys.argv[1])
    file_A = sys.argv[2]
    file_X = sys.argv[3]

    run_client(task_number, file_A, file_X)
