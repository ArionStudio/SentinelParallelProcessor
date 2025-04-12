#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>

void calculate_primes(long N, int num_threads) {
    long S = (int)sqrt(N);
    long M = N / 10;

    // Dynamiczna alokacja pamięci dla tablic
    long int* a = (long int*)malloc((S + 1) * sizeof(long int)); /* tablica pomocnicza */
    long int* pierwsze = (long int*)malloc(M * sizeof(long int)); /* liczby pierwsze w przedziale 2..N */
    if (a == NULL || pierwsze == NULL) {
        fprintf(stderr, "Błąd alokacji pamięci.\n");
        exit(1);
    }

    long i, k, liczba, reszta;
    long int lpodz; /* liczba podzielników */
    long int llpier = 0; /* liczba liczb pierwszych w tablicy pierwsze */
    double start_time, end_time; /* zmienne do mierzenia czasu */
    FILE* fp;

    /* Ustawienie liczby wątków */
    omp_set_num_threads(num_threads);

    /* Mierzenie czasu rozpoczęcia */
    start_time = omp_get_wtime();

    /* Wyznaczanie podzielników z przedziału 2..S */
    for (i = 2; i <= S; i++) {
        a[i] = 1; /* inicjowanie */
    }

    for (i = 2; i <= S; i++) {
        if (a[i] == 1) {
            pierwsze[llpier++] = i; /* zapamiętanie podzielnika */
            /* Wykreślanie liczb złożonych będących wielokrotnościami i */
            for (k = i + i; k <= S; k += i) {
                a[k] = 0;
            }
        }
    }

    lpodz = llpier; /* zapamiętanie liczby podzielników */

    /* Wyznaczanie liczb pierwszych w przedziale S+1..N */
    #pragma omp parallel for private(k, reszta) shared(pierwsze, llpier)
    for (liczba = S + 1; liczba <= N; liczba++) {
        int is_prime = 1; /* Flaga oznaczająca, czy liczba jest pierwsza */
        for (k = 0; k < lpodz; k++) {
            reszta = (liczba % pierwsze[k]);
            if (reszta == 0) {
                is_prime = 0; /* Liczba złożona */
                break;
            }
        }
        if (is_prime) {
            #pragma omp critical
            {
                pierwsze[llpier++] = liczba; /* Zapamiętanie liczby pierwszej */
            }
        }
    }

    /* Mierzenie czasu zakończenia */
    end_time = omp_get_wtime();

    /* Zapis wyników do pliku */
    char filename[50];
    sprintf(filename, "primes_%ld_threads_%d.txt", N, num_threads);
    if ((fp = fopen(filename, "w")) == NULL) {
        printf("Nie mogę otworzyć pliku do zapisu\n");
        free(a);
        free(pierwsze);
        exit(1);
    }

    for (i = 0; i < llpier; i++) {
        fprintf(fp, "%ld ", pierwsze[i]);
    }
    fclose(fp);

    /* Wyświetlenie czasu wykonania */
    printf("Rozmiar zadania: %ld, liczba wątków: %d, czas wykonania: %.6f sekund\n",
           N, num_threads, end_time - start_time);

    /* Zwolnienie pamięci */
    free(a);
    free(pierwsze);
}



int main(int argc, char** argv) {
    // Sprawdzenie liczby argumentów
    if (argc != 3) {
        fprintf(stderr, "Użycie: %s <rozmiar_zadania> <liczba_wątków>\n", argv[0]);
        return 1; // Zakończenie programu z kodem błędu
    }

    // Pobranie rozmiaru zadania i liczby wątków z argumentów
    long size = atol(argv[1]);
    int num_threads = atoi(argv[2]);

    // Walidacja argumentów
    if (num_threads <= 0 || num_threads > 8) {
        fprintf(stderr, "Błąd: Liczba wątków musi być liczbą całkowitą w zakresie od 1 do 8.\n");
        return 1;
    }
    if (num_threads <= 0) {
        fprintf(stderr, "Błąd: Liczba wątków musi być dodatnią liczbą całkowitą.\n");
        return 1;
    }

    // Wywołanie funkcji calculate_primes
    printf("Testowanie programu dla rozmiaru zadania %ld i liczby wątków %d:\n", size, num_threads);
    calculate_primes(size, num_threads);

    return 0;
}