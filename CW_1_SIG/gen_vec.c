#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define VECTOR_SIZE 10000
#define MAX_VALUE 100   

int main() {
    FILE *file = fopen("vector.txt", "w");
    if (!file) {
        perror("Błąd otwierania pliku");
        return 1;
    }

    srand(time(NULL));

    for (int i = 0; i < VECTOR_SIZE; i++) {
        fprintf(file, "%d ", rand() % MAX_VALUE + 1);
    }

    fclose(file);
    printf("Plik 'vector.txt' wygenerowany poprawnie!\n");

    return 0;
}
