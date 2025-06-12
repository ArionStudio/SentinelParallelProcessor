#include <stdio.h>

int main() {
    // Zmienne wejściowe
    int liczba_watkow;
    double czas_sekwencyjny, czas_rownolegly;
    long rozmiar_zadania;

    // Pobranie danych od użytkownika
    printf("Podaj rozmiar zadania (n): ");
    scanf("%ld", &rozmiar_zadania);

    printf("Podaj czas wykonania programu sekwencyjnego (T(1, n)): ");
    scanf("%lf", &czas_sekwencyjny);

    printf("Podaj liczbę wątków (p): ");
    scanf("%d", &liczba_watkow);

    printf("Podaj czas wykonania programu równoległego (T(p, n)): ");
    scanf("%lf", &czas_rownolegly);

    // Obliczenie przyspieszenia i efektywności
    double przyspieszenie = czas_sekwencyjny / czas_rownolegly;
    double efektywnosc = przyspieszenie / liczba_watkow;

    // Wyświetlenie wyników
    printf("\nWyniki dla rozmiaru zadania n = %ld, liczby wątków p = %d:\n", rozmiar_zadania, liczba_watkow);
    printf("Przyspieszenie (S(p, n)): %.6f\n", przyspieszenie);
    printf("Efektywność (E(p, n)): %.6f\n", efektywnosc);

    return 0;
}
