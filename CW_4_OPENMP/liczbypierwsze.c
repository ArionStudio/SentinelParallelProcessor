#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

void calculate_primes(long N) {
    long S = (long)sqrt(N); // Pierwiastek z N
    long M = N / 10;        // Szacowana maksymalna liczba liczb pierwszych

    // Dynamiczne alokowanie tablic
    long int* a = (long int*)malloc((S + 1) * sizeof(long int)); // Tablica pomocnicza
    long int* pierwsze = (long int*)malloc(M * sizeof(long int)); // Tablica liczb pierwszych

    if (a == NULL || pierwsze == NULL) {
        printf("Nie udało się zaalokować pamięci dla N = %ld.\n", N);
        return;
    }

    long i, k, liczba, reszta;
    long int lpodz; /* Liczba podzielników */
    long int llpier = 0; /* Liczba liczb pierwszych w tablicy pierwsze */

    // Mierzenie czasu rozpoczęcia
    clock_t start = clock();

    /* Wyznaczanie podzielników z przedziału 2..S */
    for (i = 2; i <= S; i++) {
        a[i] = 1; /* Inicjowanie */
    }

    for (i = 2; i <= S; i++) {
        if (a[i] == 1) {
            pierwsze[llpier++] = i; /* Zapamiętanie podzielnika */
            /* Wykreślanie liczb złożonych będących wielokrotnościami i */
            for (k = i + i; k <= S; k += i) {
                a[k] = 0;
            }
        }
    }

    lpodz = llpier; /* Zapamiętanie liczby podzielników */

    /* Wyznaczanie liczb pierwszych w przedziale S+1..N */
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
            pierwsze[llpier++] = liczba; /* Zapamiętanie liczby pierwszej */
        }
    }

    // Mierzenie czasu zakończenia
    clock_t end = clock();
    float seconds = (float)(end - start) / CLOCKS_PER_SEC;
    printf("%ld %f\n", N, seconds);

    /* Zapis wyników do pliku */
    FILE* fp;
    char filename[50];
    sprintf(filename, "primes_%ld.txt", N);
    if ((fp = fopen(filename, "w")) == NULL) {
        printf("Nie mogę otworzyć pliku do zapisu dla N = %ld.\n", N);
        free(a);
        free(pierwsze);
        return;
    }

    for (i = 0; i < llpier; i++) {
        fprintf(fp, "%ld ", pierwsze[i]);
    }
    fclose(fp);

    // Zwolnienie pamięci
    free(a);
    free(pierwsze);
}

int main() {
    // Zakresy do przetworzenia
    long zakresy[] = {100000, 1000000, 10000000};
    int liczba_zakresow = sizeof(zakresy) / sizeof(zakresy[0]);

    printf("Rozpoczynam obliczenia dla zakresów: 10^5, 10^6, 10^7\n");

    for (int i = 0; i < liczba_zakresow; i++) {
        calculate_primes(zakresy[i]);
    }

    printf("Obliczenia zakończone. Wyniki zapisano w plikach.\n");

    return 0;
}
