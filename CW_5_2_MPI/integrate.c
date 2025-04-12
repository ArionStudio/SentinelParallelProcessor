#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>

double f(double x) {
  return sin(x);
}

double integrate(double (*func)(double), double begin, double h,
                     int global_start, int global_end, int global_N) {
  double local_sum = 0.0;
  for (int i = global_start; i <= global_end; i++) {
    double x = begin + i * h;
    double coeff;
    if (i == 0 || i == global_N - 1) {
      coeff = 1.0;
    } else if (i % 2 == 1) {
      coeff = 4.0;
    } else {
      coeff = 2.0;
    }
    local_sum += coeff * func(x);
  }
  
  return local_sum;
}

int main(int argc, char *argv[]) {
  int rank, size;

  MPI_Init(&argc, &argv); 
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  double begin, end;
  int num_points;
  
  if (rank == 0) {
    if (argc != 4) {
      fprintf(stderr, "Użycie: %s begin end num_points\n", argv[0]);
      MPI_Abort(MPI_COMM_WORLD, 1);
    }
    begin = atof(argv[1]);
    end = atof(argv[2]);
    num_points = atoi(argv[3]);

    if ((num_points - 1) % 2 != 0) {
      fprintf(stderr,
              "Liczba punktów musi być taka, że (num_points - 1) jest parzysta!\n");
      MPI_Abort(MPI_COMM_WORLD, 1);
    }
  }
  
  MPI_Bcast(&begin, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
  MPI_Bcast(&end, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
  MPI_Bcast(&num_points, 1, MPI_INT, 0, MPI_COMM_WORLD);
  
  double h = (end - begin) / (num_points - 1);
  
  int points_per_proc = num_points / size;
  int remainder = num_points % size;
  int local_count, local_start, local_end;
  if (rank < remainder) {
    local_count = points_per_proc + 1;
    local_start = rank * local_count;
  } else {
    local_count = points_per_proc;
    local_start = remainder * (points_per_proc + 1) +
                  (rank - remainder) * points_per_proc;
  }
  local_end = local_start + local_count - 1;
  
  double local_result = integrate(f, begin, h, local_start, local_end, num_points);
  
  double global_result = 0.0;
  MPI_Reduce(&local_result, &global_result, 1, MPI_DOUBLE, MPI_SUM, 0,
             MPI_COMM_WORLD);
  
  if (rank == 0) {
    double integral = h / 3.0 * global_result;
    printf("Całka oznaczona = %.12f\n", integral);
  }
  
  MPI_Finalize();
  return 0;
}