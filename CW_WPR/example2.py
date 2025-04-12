from mpi4py import MPI

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            # numer procesu
    numProcesses = comm.Get_size()  # łączna liczba procesów
    myHostName = MPI.Get_processor_name()  # nazwa maszyny

    REPS = 16

    if ((REPS % numProcesses) == 0 and numProcesses <= REPS):
        # określenie zakresu iteracji dla danego procesu
        chunkSize = int(REPS / numProcesses)
        start = id * chunkSize
        stop = start + chunkSize

        # wykonanie przypisanych iteracji
        for i in range(start, stop):
            print("On {}: Process {} is performing iteration {}"
                  .format(myHostName, id, i))
    else:
        # jeżeli nie da się podzielić iteracji równo
        if id == 0:
            print("Please run with number of processes divisible by "
                  "and less than or equal to {}.".format(REPS))

main()
