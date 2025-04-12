from mpi4py import MPI
import numpy as np

def generate_table(size,rank,name):
    data = [list(np.random.randint(1, 10, size=5)) for _ in range(size)]
    print(f"Master (rank {rank}) on {name} generated data: {data}")
    return data

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = MPI.Get_processor_name()

    if size <= 1:
        if rank == 0:
            print("Please run with more than 1 process.")
        return

    if rank == 0:
        data = generate_table(size,rank,hostname)

        for dest in range(1, size):
            comm.send(data[dest], dest=dest, tag=100 + dest)

        my_data = data[0]

    else:
        my_data = comm.recv(source=0, tag=100 + rank)

    local_sum = sum(my_data)
    print(f"Process {rank} on {hostname} received {my_data}, sum = {local_sum}")

main()
