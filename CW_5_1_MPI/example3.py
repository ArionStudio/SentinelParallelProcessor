from mpi4py import MPI

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            #number of the process running the code
    numProcesses = comm.Get_size()  #total number of processes running
    myHostName = MPI.Get_processor_name()  #machine name running the code

    REPS = 16

    if (numProcesses <= REPS):

        for i in range(id, REPS, numProcesses):
            print("On {}: Process {} is performing iteration {}"\
            .format(myHostName, id, i))

    else:
        # can't have more processes than work; one process reports the error
        if id == 0 :
            print("Please run with number of processes less than \
or equal to {}.".format(REPS))

########## Run the main function
main()
