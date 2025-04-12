#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>


int main(int argc, char**argv){
    int procId, procId_nowy, kolor;
    
    MPI_Comm nowycomm;
    float kat, fun, maks;
    char *nazwa[2];
    nazwa[0] = "bialy";
    nazwa[1] = "czarny";

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &procId);

    /*
       utworzenie 2 nowych komunikatorów
       zapamietywanych przez zmienna nowycomm
       czarny - zad z parzystym id
       bialy - zad z nieparzystym id

    */

    kolor = procId % 2;
    MPI_Comm_split(MPI_COMM_WORLD, kolor, procId, &nowycomm);

    /*
       Obliczanie funkcji i zapamietywanie wyniku
    */


    kat = 100. * (procId + 10);
    fun = cos(kat);

    printf("Kolor %6s, Id procesu: %d, argument %5.0f, \
            wartosc funkcji: %8.7f\n", 
            nazwa[kolor], kat, fun);

    /*
       Wyznaczenie maksymalnej wartosci f-ji
       dla każdego komunikatora
     */


    MPI_Reduce(&fun, &maks, 1, MPI_FLOAT, MPI_MAX, 0, nowycomm);
    MPI_Comm_rank(nowycomm, &procId_nowy);

    if(procId_nowy == 0)
        printf("Komunikator (kolor): %6s, maksimum: %8.7f\n",
                nazwa[kolor], maks);
    MPI_Finalize();
    return 0;
}
