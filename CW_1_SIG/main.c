#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/wait.h>
#include <signal.h>
#include <unistd.h>
#include <semaphore.h>
#include <time.h>
#include <fcntl.h>

#define VECTOR_SIZE 10000
#define SHM_KEY_RANGE 1234
#define SHM_KEY_RESULT 5678

void signal_handler(int signum) {
    if (signum == SIGUSR1) {
        return;
    }
}

void child_process(int id, int shm_id_range, int shm_id_result, double *vector) {
    signal(SIGUSR1, signal_handler);
    pause(); 

    int *range = (int *) shmat(shm_id_range, NULL, 0);
    if (range == (void *) -1) {
        perror("Błąd shmat dla range w procesie potomnym");
        exit(1);
    }

    double *result = (double *) shmat(shm_id_result, NULL, 0);
    if (result == (void *) -1) {
        perror("Błąd shmat dla result w procesie potomnym");
        exit(1);
    }

    int start = (id != 0) ? range[id - 1] : 0;
    int end = range[id];

    double local_sum = 0;
    for (int i = start; i < end; i++) {
        local_sum += vector[i];
    }

    result[id] = local_sum;

    if(shmdt(range) == -1) {
        perror("Błąd shmdt dla range w procesie potomnym");
    }
    if(shmdt(result) == -1) {
        perror("Błąd shmdt dla result w procesie potomnym");
    }

    exit(0);
}


int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Użycie: %s <plik_wektora> <liczba_procesów>\n", argv[0]);
        return 1;
    }

    char *endptr;
    long num_processes_test = strtol(argv[2], &endptr, 10);
    if (*endptr != '\0' || num_processes_test <= 0 || num_processes_test > VECTOR_SIZE) {
        fprintf(stderr, "Liczba procesów musi być liczbą większą od 0 i mniejszą od %d\n", VECTOR_SIZE);
        return 1;
    }
    int num_processes = (int) num_processes_test;

    int shm_id_range = shmget(SHM_KEY_RANGE, num_processes * sizeof(int), IPC_CREAT | 0666);
    if (shm_id_range == -1) {
        perror("Błąd shmget dla range");
        return 1;
    }
    int shm_id_result = shmget(SHM_KEY_RESULT, num_processes * sizeof(double), IPC_CREAT | 0666);
    if (shm_id_result == -1) {
        perror("Błąd shmget dla result");
        return 1;
    }

    int *range = (int *) shmat(shm_id_range, NULL, 0);
    if (range == (void *) -1) {
        perror("Błąd shmat dla range w procesie macierzystym");
        return 1;
    }
    double *result = (double *) shmat(shm_id_result, NULL, 0);
    if (result == (void *) -1) {
        perror("Błąd shmat dla result w procesie macierzystym");
        return 1;
    }

    double *vector = (double *) malloc(VECTOR_SIZE * sizeof(double));
    if (vector == NULL) {
        perror("Błąd alokacji pamięci dla vector");
        return 1;
    }

    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror("Błąd otwierania pliku");
        free(vector);
        return 1;
    }
    for (int i = 0; i < VECTOR_SIZE; i++) {
        if (fscanf(file, "%lf", &vector[i]) != 1) {
            fprintf(stderr, "Błąd odczytu elementu %d z pliku\n", i);
            fclose(file);
            free(vector);
            return 1;
        }
    }
    fclose(file);

    printf("Il. procesów: %d\n", num_processes);

    pid_t children[num_processes];
    for (int i = 0; i < num_processes; i++) {
        pid_t pid = fork();
        if (pid == -1) {
            perror("Błąd fork");
            exit(1);
        } else if (pid == 0) {
            printf("Proces potomny %d: PID = %d\n", i, getpid());
            child_process(i, shm_id_range, shm_id_result, vector);
        } else {
            children[i] = pid;
        }
    }

    int chunk_size = VECTOR_SIZE / num_processes;
    int remainder = VECTOR_SIZE % num_processes;
    int sum = 0;
    for (int i = 0; i < num_processes; i++) {
        int extra = (i < remainder) ? 1 : 0;
        sum += chunk_size + extra;
        range[i] = sum;
    }

    usleep(1000);
    for (int i = 0; i < num_processes; i++) {
        if (kill(children[i], SIGUSR1) == -1) {
            perror("Błąd wysyłania sygnału do procesu potomnego");
        }
    }

    for (int i = 0; i < num_processes; i++) {
        if (wait(NULL) == -1) {
            perror("Błąd wait");
            return 1;
        }
    }

    double total_sum = 0;
    for (int i = 0; i < num_processes; i++) {
        printf("Proces %d: suma lokalna = %lf\n", i, result[i]);
        total_sum += result[i];
    }

    printf("Suma wektora: %lf\n", total_sum);

    double test_sum = 0;
    for (int i = 0; i < VECTOR_SIZE; i++) {
        test_sum += vector[i];
    }
    printf("Suma wektora (test): %lf\n", test_sum);

    if (shmdt(range) == -1) {
        perror("Błąd shmdt dla range w procesie macierzystym");
    }
    if (shmdt(result) == -1) {
        perror("Błąd shmdt dla result w procesie macierzystym");
    }
    if (shmctl(shm_id_range, IPC_RMID, NULL) == -1) {
        perror("Błąd shmctl dla range");
    }
    if (shmctl(shm_id_result, IPC_RMID, NULL) == -1) {
        perror("Błąd shmctl dla result");
    }
    free(vector);

    return 0;
}
