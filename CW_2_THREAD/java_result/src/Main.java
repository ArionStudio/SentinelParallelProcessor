import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        if (args.length != 3) {
            System.out.println("Usage: java Main A.txt B.txt num_threads");
            return;
        }

        String fileA = args[0];
        String fileB = args[1];
        
        int numThreads;
        try {
            numThreads = Integer.parseInt(args[2]);
        } catch (NumberFormatException e) {
            System.out.println("Error: Number of threads must be an integer.");
            return;
        }

        if (numThreads <= 0) {
            System.out.println("Error: Number of threads must be greater than 0.");
            return;
        }

        Matrix A = Matrix.readMatrixFromFile(fileA);
        Matrix B = Matrix.readMatrixFromFile(fileB);

        if (A == null || B == null) {
            System.out.println("Error: Failed to load matrices.");
            return;
        }

        if (A.getCols() != B.getRows()) {
            System.out.println("Error: Invalid matrix dimensions! Cannot multiply.");
            return;
        }
        MatrixMultiplier.resetCounters();

        int totalOperations = A.getRows() * B.getCols();
        if (numThreads > totalOperations) {
            numThreads = totalOperations;
            System.out.println("Number of operations (" + totalOperations + ") is less than number of threads! Setting " + numThreads + " threads.");
        }

        Matrix C = new Matrix(A.getRows(), B.getCols());
        List<Thread> threads = new ArrayList<>();

        int chunkSize = totalOperations / numThreads;
        int remainder = totalOperations % numThreads;
        int start = 0;

        for (int i = 0; i < numThreads; i++) {
            int end = start + chunkSize + (i < remainder ? 1 : 0);
            threads.add(new Thread(new MatrixMultiplier(A, B, C, start, end)));
            start = end;
        }

        for (Thread thread : threads) {
            thread.start();
        }

        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                System.err.println("Thread was interrupted: " + e.getMessage());
                Thread.currentThread().interrupt(); 
            }
        }

        System.out.println("Result matrix:");
        System.out.println(C);
        System.out.printf("Sum of elements in result matrix: %.2f%n", MatrixMultiplier.getGlobalSum());
        System.out.printf("Frobenius norm of result matrix: %.6f%n", MatrixMultiplier.getFrobeniusNorm());
    }
}
