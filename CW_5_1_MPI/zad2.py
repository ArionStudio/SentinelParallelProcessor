from mpi4py import MPI
import numpy as np

def generate_table(size, rank, name):
    data = [list(np.random.randint(1, 10, size=5)) for _ in range(size)]
    print(f"Master (rank {rank}) on {name} generated data: {data}")
    return data

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    name = MPI.Get_processor_name()

    if size <= 1:
        if rank == 0:
            print("Please run this program with more than one process.")
        return

    if rank == 0:
        data = generate_table(size, rank, name)
    else:
        data = None

    my_data = comm.scatter(data, root=0)

    local_sum = sum(my_data)
    print(f"Process {rank} on {name} received {my_data}, sum = {local_sum}")

main()
