#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "mpi.h"

int main(int argc, char** argv)
{
    char msg[20];
    int i, rank, size;
    int tag = 99;

    MPI_Status status;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if(rank == 0)
    {
        strcpy(msg, "Hello, world");
        for(i=1; i < size; i++)
           MPI_Send(msg, 13, MPI_CHAR, i, tag, MPI_COMM_WORLD);
    } 
    else
    {

       MPI_Recv(msg, 20, MPI_CHAR, 0, tag, MPI_COMM_WORLD, &status);
       printf("Tu proces %d: %s\n", rank, msg);

    }


    MPI_Finalize(); 
    
    return 0;
}
