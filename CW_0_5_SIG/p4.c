#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>

pid_t child_pid = 0;

/* Global variable for parent's PID, so child can send back signal */
pid_t parent_pid = 0;

/* Child's handler for SIGTERM */
void child_term_handler(int sig) {
    printf("[Child] Received SIGTERM. Sending SIGUSR1 to parent (PID=%d)\n", parent_pid);
    kill(parent_pid, SIGUSR1);
    /* After sending farewell, child can exit or continue. Let's exit. */
    exit(0);
}

/* Parent's handler for SIGUSR1 (receives farewell message from child) */
void parent_usr1_handler(int sig) {
    printf("[Parent] Received SIGUSR1 from child (PID=%d). Farewell message!\n", child_pid);
}

int main(void) {
    struct sigaction sa_child;
    struct sigaction sa_parent;
    sigset_t block_mask;

    parent_pid = getpid();

    switch (child_pid = fork()) {
        case -1:
            perror("fork");
            exit(EXIT_FAILURE);

        case 0:
            /* Child code */
            printf("[Child] Child PID=%d started.\n", getpid());
            /* Setup handler for SIGTERM */
            sigemptyset(&block_mask);
            sa_child.sa_mask = block_mask;
            sa_child.sa_flags = 0;
            sa_child.sa_handler = child_term_handler;
            sigaction(SIGTERM, &sa_child, NULL);

            /* Wait indefinitely for signals */
            while(1) {
                pause();
            }
            exit(EXIT_SUCCESS);

        default:
            /* Parent code */
            printf("[Parent] Parent PID=%d, Child PID=%d.\n", parent_pid, child_pid);

            /* Setup parent's handler for SIGUSR1 */
            sigemptyset(&block_mask);
            sa_parent.sa_mask = block_mask;
            sa_parent.sa_flags = 0;
            sa_parent.sa_handler = parent_usr1_handler;
            sigaction(SIGUSR1, &sa_parent, NULL);

            /* Sleep to ensure child is ready */
            sleep(2);

            /* Send SIGTERM to child */
            printf("[Parent] Sending SIGTERM to child...\n");
            kill(child_pid, SIGTERM);

            /* Wait for child's farewell (SIGUSR1) */
            sleep(2);

            printf("[Parent] Parent is exiting.\n");
            if(wait(0) == -1){
                perror("wait for childe");
                exit(EXIT_FAILURE);
            }
            exit(EXIT_SUCCESS);
    }
}
