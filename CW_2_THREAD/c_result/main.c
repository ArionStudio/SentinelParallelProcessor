#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    double **A, **B, **C;
    size_t ma, na, mb, nb;
    int thread_count;
    size_t *positions;
    double *sum;
    double *frobenius_norm_sum;
    pthread_mutex_t *mutex_sum;
    int id;
} ThreadData;

void *multiply(void *arg) {
    ThreadData *thread_data = (ThreadData *)arg;
    int id = thread_data->id;
    double local_sum = 0.0;
    double local_frobenius_sum = 0.0;

    for (size_t i = (id > 0 ? thread_data->positions[id - 1] : 0); i < thread_data->positions[id]; i++) {
        double cell_value = 0.0;
        size_t row = i / thread_data->nb;
        size_t col = i % thread_data->nb;
        
        for(size_t j = 0; j < thread_data->na; j++){
            cell_value += thread_data->A[row][j] * thread_data->B[j][col];
        }
        
        thread_data->C[row][col] = cell_value;
        local_sum += cell_value;
        local_frobenius_sum += cell_value * cell_value;
    }
    
    pthread_mutex_lock(thread_data->mutex_sum);
    *(thread_data->sum) += local_sum;
    *(thread_data->frobenius_norm_sum) += local_frobenius_sum;
    pthread_mutex_unlock(thread_data->mutex_sum);
    
    pthread_exit(NULL);
}

void print_matrix(double **matrix, size_t rows, size_t cols) {
    printf("[\n");
    for (size_t i = 0; i < rows; i++) {
        for (size_t j = 0; j < cols; j++) {
            printf("%f ", matrix[i][j]);
        }
        printf("\n");
    }
    printf("]\n");
}

double **allocate_matrix(size_t rows, size_t cols) {
    double **matrix = malloc(rows * sizeof(double *));
    if (matrix == NULL) {
        return NULL;
    }
    
    for (size_t i = 0; i < rows; i++) {
        matrix[i] = malloc(cols * sizeof(double));
        if (matrix[i] == NULL) {
            // Free previously allocated memory
            for (size_t j = 0; j < i; j++) {
                free(matrix[j]);
            }
            free(matrix);
            return NULL;
        }
    }
    return matrix;
}

void free_matrix(double **matrix, size_t rows) {
    if (matrix == NULL) return;
    
    for (size_t i = 0; i < rows; i++) {
        free(matrix[i]);
    }
    free(matrix);
}

bool read_matrix(const char *filename, double ***matrix, size_t *rows, size_t *cols) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Error opening file");
        return false;
    }

    int scan_result = fscanf(file, "%zu %zu", rows, cols);
    if (scan_result != 2) {
        fprintf(stderr, "Error reading matrix dimensions\n");
        fclose(file);
        return false;
    }

    *matrix = allocate_matrix(*rows, *cols);
    if (*matrix == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(file);
        return false;
    }

    for (size_t i = 0; i < *rows; i++) {
        for (size_t j = 0; j < *cols; j++) {
            scan_result = fscanf(file, "%lf", &(*matrix)[i][j]);
            if (scan_result != 1) {
                fprintf(stderr, "Error reading matrix element at [%zu][%zu]\n", i, j);
                free_matrix(*matrix, *rows);
                *matrix = NULL;
                fclose(file);
                return false;
            }
        }
    }

    fclose(file);
    return true;
}

void cleanup_resources(double **A, size_t ma, 
                      double **B, size_t mb, 
                      double **C, size_t mc,
                      pthread_t *threads, ThreadData *thread_data, 
                      size_t *positions, pthread_mutex_t *mutex) {
    // Free matrices if allocated
    if (A != NULL) free_matrix(A, ma);
    if (B != NULL) free_matrix(B, mb);
    if (C != NULL) free_matrix(C, mc);
    
    // Free thread resources
    if (threads != NULL) free(threads);
    if (thread_data != NULL) free(thread_data);
    if (positions != NULL) free(positions);
    
    // Destroy mutex if initialized
    if (mutex != NULL) pthread_mutex_destroy(mutex);
}

int main(int argc, char *argv[]) {    
    double **A = NULL, **B = NULL, **C = NULL;
    size_t ma, na, mb, nb;
    int num_threads;
    double global_sum = 0.0;
    double frobenius_norm_sum = 0.0;
    pthread_mutex_t mutex_sum;
    int result;
    pthread_t *threads = NULL;
    ThreadData *thread_data = NULL;
    size_t *positions = NULL;
    bool mutex_initialized = false;
    
    if (argc != 4) {
        printf("Usage: %s matrixA.txt matrixB.txt num_threads\n", argv[0]);
        return EXIT_FAILURE;
    }

    num_threads = atoi(argv[3]);
    if (num_threads <= 0) {
        printf("Number of threads must be greater than 0\n");
        return EXIT_FAILURE;
    }

    if (num_threads > 32) {
        printf("Number of threads cannot exceed 32\n");
        return EXIT_FAILURE;
    }

    if (!read_matrix(argv[1], &A, &ma, &na)) {
        return EXIT_FAILURE;
    }
    
    if (!read_matrix(argv[2], &B, &mb, &nb)) {
        cleanup_resources(A, ma, NULL, 0, NULL, 0, NULL, NULL, NULL, NULL);
        return EXIT_FAILURE;
    }

    if (na != mb) {
        printf("Invalid matrix dimensions for multiplication!\n");
        cleanup_resources(A, ma, B, mb, NULL, 0, NULL, NULL, NULL, NULL);
        return EXIT_FAILURE;
    }

    size_t total_operations = ma * nb;

    if ((size_t)num_threads > total_operations) {
        num_threads = (int)total_operations;
        printf("Number of operations (%zu) is less than number of threads! Setting to %d threads.\n", 
               total_operations, num_threads);
    }

    C = allocate_matrix(ma, nb);
    if (C == NULL) {
        printf("Memory allocation failed for result matrix\n");
        cleanup_resources(A, ma, B, mb, NULL, 0, NULL, NULL, NULL, NULL);
        return EXIT_FAILURE;
    }
    
    threads = malloc(num_threads * sizeof(pthread_t));
    if (threads == NULL) {
        printf("Memory allocation failed for threads\n");
        cleanup_resources(A, ma, B, mb, C, ma, NULL, NULL, NULL, NULL);
        return EXIT_FAILURE;
    }
    
    thread_data = malloc(num_threads * sizeof(ThreadData));
    if (thread_data == NULL) {
        printf("Memory allocation failed for thread data\n");
        cleanup_resources(A, ma, B, mb, C, ma, threads, NULL, NULL, NULL);
        return EXIT_FAILURE;
    }

    if (pthread_mutex_init(&mutex_sum, NULL) != 0) {
        printf("Mutex initialization failed\n");
        cleanup_resources(A, ma, B, mb, C, ma, threads, thread_data, NULL, NULL);
        return EXIT_FAILURE;
    }
    mutex_initialized = true;

    positions = malloc(num_threads * sizeof(size_t));
    if (positions == NULL) {
        printf("Memory allocation failed for positions array\n");
        cleanup_resources(A, ma, B, mb, C, ma, threads, thread_data, NULL, 
                         mutex_initialized ? &mutex_sum : NULL);
        return EXIT_FAILURE;
    }
    
    size_t rows_per_thread = total_operations / num_threads;
    size_t extra_rows = total_operations % num_threads;
    size_t sum = 0;

    for (int i = 0; i < num_threads; i++) {
        size_t extra = (i < (int)extra_rows) ? 1 : 0;
        sum += rows_per_thread + extra;
        positions[i] = sum;
    }
    
    for (int i = 0; i < num_threads; i++) {
        thread_data[i].A = A;
        thread_data[i].B = B;
        thread_data[i].C = C;
        thread_data[i].ma = ma;
        thread_data[i].na = na;
        thread_data[i].mb = mb;
        thread_data[i].nb = nb;
        thread_data[i].sum = &global_sum;
        thread_data[i].frobenius_norm_sum = &frobenius_norm_sum;
        thread_data[i].mutex_sum = &mutex_sum;
        thread_data[i].thread_count = num_threads;
        thread_data[i].id = i;
        thread_data[i].positions = positions;
        
        result = pthread_create(&threads[i], NULL, multiply, (void *)&thread_data[i]);
        if (result != 0) {
            printf("Thread creation failed with error code: %d\n", result);
            for (int j = 0; j < i; j++) {
                pthread_cancel(threads[j]);
                pthread_join(threads[j], NULL);
            }
            cleanup_resources(A, ma, B, mb, C, ma, threads, thread_data, positions, 
                             mutex_initialized ? &mutex_sum : NULL);
            return EXIT_FAILURE;
        }
    }

    for (int i = 0; i < num_threads; i++) {
        result = pthread_join(threads[i], NULL);
        if (result != 0) {
            printf("Failed to join thread %d with error code: %d\n", i, result);
        }
    }

    double frobenius_norm = sqrt(frobenius_norm_sum);

    printf("Result matrix:\n");
    print_matrix(C, ma, nb);
    printf("Sum of elements in result matrix: %.2f\n", global_sum);
    printf("Frobenius norm of result matrix: %.6f\n", frobenius_norm);

    cleanup_resources(A, ma, B, mb, C, ma, threads, thread_data, positions, 
                     mutex_initialized ? &mutex_sum : NULL);

    return EXIT_SUCCESS;
}
