#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

/* Funkcja uruchamiana, gdy napotkamy sygnał HUP */
void on_hup(int signal) {
    printf("HUP..Czekam..\n");
    sleep(10); /* Czekamy najwyżej 10s na sygnał */
    printf("..Skończyłem czekać..\n");
    pause(); /* Czekamy na kolejny sygnał */
    printf("..Koniec HUP\n");
}

void ignore_signal(int sig) {
    printf(" Odebrano sygnał %d, ale został zignorowany.\n", sig);
}

/* Funkcja uruchamiana, gdy napotkamy sygnał USR1 */
/* Czy kiedykolwiek się uruchomi? */
void on_usr1(int signal) { printf("Otrzymałem USR1\n"); }

/* Funkcja uruchamiana, gdy napotkamy sygnał USR2 */
void on_usr2(int signal) { printf("Otrzymałem USR2\n"); }

int main(int argc, char** argv) {
    /* Pobierz swój PID */
    pid_t my_pid = getpid();
    sigset_t mask; /* Maska sygnałów */

    /* Konfiguracja obsługi sygnału USR1 */
    struct sigaction usr1;
    sigemptyset(&mask); /* Wyczyść maskę */
    usr1.sa_handler = (&on_usr1);
    usr1.sa_mask = mask;
    usr1.sa_flags = SA_SIGINFO;
    sigaction(SIGUSR1, &usr1, NULL);

    /* Konfiguracja obsługi sygnału USR2 */
    struct sigaction usr2;
    sigemptyset(&mask); /* Wyczyść maskę */
    usr2.sa_handler = (&on_usr2);
    usr2.sa_mask = mask;
    usr2.sa_flags = SA_SIGINFO;
    sigaction(SIGUSR2, &usr2, NULL);

    // /* Konfiguracja obslugi sugnalu CTRL+Z - SIGTSTP */
    struct sigaction signal_stop;
    sigemptyset(&mask);
    signal_stop.sa_handler = SIG_IGN;
    signal_stop.sa_mask = mask;
    signal_stop.sa_flags = SA_SIGINFO;
    sigaction(SIGTSTP, &signal_stop, NULL);

    /* Konfiguracja obsługi sygnału
     * HUP */
    struct sigaction hup;
    sigemptyset(&mask);        /* Wyczyść maskę */
    sigaddset(&mask, SIGUSR1); /* Dodaj do niej SIGUSR1 */
    hup.sa_handler = (&on_hup);
    hup.sa_mask = mask;
    hup.sa_flags = SA_SIGINFO;
    sigaction(SIGHUP, &hup, NULL);

    sigemptyset(&mask);                  /* Wyczyść maskę */
    sigprocmask(SIG_BLOCK, &mask, NULL); /* Ustaw maskę dla całego procesu */

    printf("PID: %d\n", my_pid);
    while (1) pause(); /* Czekaj na sygnały */

    return 0;
}
