#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <signal.h>
#include <math.h>

#define N 3 

pid_t children[N];

int is_prime(long num) {
    if (num < 2) return 0;
    for (long i = 2; i <= sqrt(num); i++) {
        if (num % i == 0) return 0;
    }
    return 1;
}

volatile sig_atomic_t reset_flag = 0;

void on_hup_child(int signal) {
    printf("Potomek PID: %d otrzymał SIGHUP – resetuję licznik!\n", getpid());
    reset_flag = 1; 
}

void find_primes() {
    pid_t my_pid = getpid();
    long num = 2;

    struct sigaction hup;
    hup.sa_handler = on_hup_child;
    sigemptyset(&hup.sa_mask);
    hup.sa_flags = 0;
    sigaction(SIGHUP, &hup, NULL);

    printf("Potomek PID: %d zaczyna szukać liczb pierwszych...\n", my_pid);
    
    while (1) {
        if (reset_flag) { 
            num = 2;
            reset_flag = 0;
            printf("Potomek PID: %d restartuje pracę!\n", my_pid);
        }

        if (is_prime(num)) {
            printf("PID %d: %ld jest liczbą pierwszą\n", my_pid, num);
        }
        num++;

        usleep(100000);
    }
}

void on_hup_parent(int signal) {
    printf("Macierzysty PID: %d otrzymał SIGHUP – przekazuję do potomków...\n", getpid());
    
    for (int i = 0; i < N; i++) {
        if (children[i] > 0) {
            kill(children[i], SIGHUP); 
        }
    }
}

int main() {
    pid_t pid;
    sigset_t mask;
    
    printf("Macierzysty PID: %d\n", getpid());

    struct sigaction hup;
    hup.sa_handler = on_hup_parent;
    sigemptyset(&hup.sa_mask);
    hup.sa_flags = 0;
    sigaction(SIGHUP, &hup, NULL);

    for (int i = 0; i < N; i++) {
        pid = fork();
        if (pid < 0) {
            perror("Błąd fork()");
            return EXIT_FAILURE;
        }
        if (pid == 0) {
            find_primes();
            return EXIT_SUCCESS;
        } else { 
            children[i] = pid; 
            printf("Macierzysty utworzył potomka PID: %d\n", pid);
        }
    }

    while (1) {
        pause(); 
    }

    return 0;
}
