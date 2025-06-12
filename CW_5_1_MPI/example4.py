from mpi4py import MPI

# function to return whether a number of a process is odd or even
def odd(number):
    if (number % 2) == 0:
        return False
    else :
        return True

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            #number of the process running the code
    numProcesses = comm.Get_size()  #total number of processes running
    myHostName = MPI.Get_processor_name()  #machine name running the code

    if numProcesses > 1 and not odd(numProcesses):
        #generate a list of 8 numbers, beginning with my id
        sendList = list(range(id, id+8))
        if odd(id):
            #odd processes send to their 'left neighbor', then receive from
            comm.send(sendList, dest=id-1)
            receivedList = comm.recv(source=id-1)
        else :
            #even processes receive from their 'right neighbor', then send
            receivedList = comm.recv(source=id+1)
            comm.send(sendList, dest=id+1)

        print("Process {} of {} on {} computed {} and received {}"\
        .format(id, numProcesses, myHostName, sendList, receivedList))

    else :
        if id == 0:
            print("Please run this program with the number of processes \
positive and even")

########## Run the main function
main()
