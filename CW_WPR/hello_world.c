#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "mpi.h"

int main(int argc, char** argv)
{
    int  rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    printf("Liczba zadan: %d, jestem zadaniem: %d.\n", size, rank);

    MPI_Finalize(); 
    
    return 0;
}
