from mpi4py import MPI

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            #number of the process running the code
    numProcesses = comm.Get_size()  #total number of processes running
    myHostName = MPI.Get_processor_name()  #machine name running the code

    if numProcesses > 1 :

        if id == 0:        # master
            #master: generate a dictionary with arbitrary data in it
            data = list(range(numProcesses))
            print("Master Process {} of {} on {} broadcasts {}"\
            .format(id, numProcesses, myHostName, data))

        else :
            # worker: start with empty data
            data = []
            print("Worker Process {} of {} on {} starts with {}"\
            .format(id, numProcesses, myHostName, data))

        #initiate and complete the broadcast
        data = comm.bcast(data, root=0)

        #check the result
        print("Process {} of {} on {} has {} after the broadcast"\
        .format(id, numProcesses, myHostName, data))

    else :
        print("Please run this program with the number of processes greater than 1")

########## Run the main function
main()
