import java.util.concurrent.locks.ReentrantLock;

public class MatrixMultiplier implements Runnable {
    private final Matrix A, B, C;
    private final int startIdx, endIdx;

    private static double globalSum = 0;
    private static double frobeniusNormSum = 0;
    private static final ReentrantLock lock = new ReentrantLock();

    public MatrixMultiplier(Matrix A, Matrix B, Matrix C, int startIdx, int endIdx) {
        this.A = A;
        this.B = B;
        this.C = C;
        this.startIdx = startIdx;
        this.endIdx = endIdx;
    }


    public static void resetCounters() {
        lock.lock();
        try {
            globalSum = 0;
            frobeniusNormSum = 0;
        } finally {
            lock.unlock();
        }
    }

    @Override
    public void run() {
        try {
            int rows = C.getRows();
            int cols = C.getCols();
            int na = A.getCols();

            double localSum = 0;
            double localFrobenius = 0;

            for (int i = startIdx; i < endIdx; i++) {
                int row = i / cols;
                int col = i % cols;
                
                if (row >= rows || col >= cols) {
                    System.err.println("Warning: Index out of bounds: [" + row + "][" + col + "]");
                    continue;
                }
                
                double sum = 0;

                for (int j = 0; j < na; j++) {
                    sum += A.getValue(row, j) * B.getValue(j, col);
                }

                C.setValue(row, col, sum);

                localSum += sum;
                localFrobenius += sum * sum;
            }

            lock.lock();
            try {
                globalSum += localSum;
                frobeniusNormSum += localFrobenius;
            } finally {
                lock.unlock();
            }
        } catch (Exception e) {
            System.err.println("Error in thread execution: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static double getGlobalSum() {
        return globalSum;
    }

    public static double getFrobeniusNorm() {
        return Math.sqrt(frobeniusNormSum);
    }
}
