import java.io.File;
import java.io.FileNotFoundException;
import java.util.Locale;
import java.util.Scanner;

public class Matrix {
    private final int rows;
    private final int cols;
    private final double[][] data;

    public Matrix(int rows, int cols) {
        if (rows <= 0 || cols <= 0) {
            throw new IllegalArgumentException("Matrix dimensions must be positive");
        }
        this.rows = rows;
        this.cols = cols;
        this.data = new double[rows][cols];
    }

    public int getRows() {
        return rows;
    }

    public int getCols() {
        return cols;
    }

    public double[][] getData() {
        double[][] copy = new double[rows][cols];
        for (int i = 0; i < rows; i++) {
            System.arraycopy(data[i], 0, copy[i], 0, cols);
        }
        return copy;
    }

    public double getValue(int row, int col) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw new IndexOutOfBoundsException("Index out of bounds: [" + row + "][" + col + "]");
        }
        return data[row][col];
    }
    

    public void setValue(int row, int col, double value) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw new IndexOutOfBoundsException("Index out of bounds: [" + row + "][" + col + "]");
        }
        data[row][col] = value;
    }


    public static Matrix readMatrixFromFile(String filename) {
        try {
            File file = new File(filename);
            System.out.println("Reading matrix from: " + file.getAbsolutePath());
            
            try (Scanner scanner = new Scanner(file)) {
                scanner.useLocale(Locale.US);
                
                if (!scanner.hasNextInt()) {
                    System.err.println("Error: Expected number of rows at the beginning of the file.");
                    return null;
                }
                int rows = scanner.nextInt();
                
                if (!scanner.hasNextInt()) {
                    System.err.println("Error: Expected number of columns after rows.");
                    return null;
                }
                int cols = scanner.nextInt();
                
                if (rows <= 0 || cols <= 0) {
                    System.err.println("Error: Matrix dimensions must be positive.");
                    return null;
                }
                
                System.out.println("Matrix dimensions: " + rows + "x" + cols);
                
                Matrix matrix;
                try {
                    matrix = new Matrix(rows, cols);
                } catch (IllegalArgumentException e) {
                    System.err.println("Error: " + e.getMessage());
                    return null;
                }

                for (int i = 0; i < rows; i++) {
                    for (int j = 0; j < cols; j++) {
                        if (!scanner.hasNextDouble()) {
                            System.err.println("Error: Expected a number at position [" + i + "][" + j + "]");
                            if (scanner.hasNext()) {
                                System.err.println("Current scanner position: " + scanner.next());
                            } else {
                                System.err.println("End of file reached unexpectedly");
                            }
                            return null;
                        }
                        matrix.data[i][j] = scanner.nextDouble();
                    }
                }
                return matrix;
            }
        } catch (FileNotFoundException e) {
            System.err.println("Error: File not found - " + filename);
            return null;
        } catch (Exception e) {
            System.err.println("Error reading matrix file: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("[\n");
        for (double[] row : data) {
            for (double value : row) {
                sb.append(value).append(" ");
            }
            sb.append("\n");
        }
        sb.append("]\n");
        return sb.toString();
    }
}
