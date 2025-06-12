import random

def fill_file(x, a, b, filename="data.txt"):
    with open(filename, 'w') as f:
        for _ in range(x):
            num_digits = random.randint(a, b)
            min_value = 10 ** (num_digits - 1)
            max_value = (10 ** num_digits) - 1
            random_number = random.randint(min_value, max_value)
            f.write(str(random_number) + '\n')

if __name__ == "__main__":
    x = 1000
    a = 1
    b = 30
    fill_file(x, a, b)
    print(f"The file data.txt has been filled with {x} random numbers with lengths from {a} to {b} digits.")

