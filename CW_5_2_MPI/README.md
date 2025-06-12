# MPI Integration Program on Raspberry Pi Cluster

This project demonstrates parallel numerical integration using MPI on a Raspberry Pi cluster. The program calculates the definite integral of sin(x) from 0 to π using Simpson's rule.

## Features

- Parallel computation using MPI
- Numerical integration using Simpson's rule
- Distributed workload across multiple Raspberry Pi nodes
- Error checking and validation

## Requirements

- Two or more Raspberry Pi systems
- MPICH
- SSH access between nodes
- Basic C compilation tools

## Setup Instructions

### 1. System Update and Package Installation

Run the following commands on all Raspberry Pi nodes:

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y mpich
```

### 2. SSH Key Setup

On each Raspberry Pi, run:

```bash
# Generate SSH key if not exists
if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
fi

# Copy public key to other nodes
# Replace USERNAME and IP_ADDRESS with actual values
ssh-copy-id -i ~/.ssh/id_ed25519.pub USERNAME@IP_ADDRESS
```

### 3. Network Configuration

Create a hostfile in your project directory:

```
192.168.0.6
192.168.0.17
```

### 4. Compilation

```bash
mpicc integrate.c -o integrate -lm
```

### 5. Running the Program

```bash
mpirun -hostfile hostfile -np 2 integrate 0 3.141592653589793 1000000
```

## Program Parameters

- begin: Starting point of integration (default: 0)
- end: Ending point of integration (default: π)
- num_points: Number of points for integration (must be such that (num_points - 1) is even)

## Expected Output

The program will output the calculated integral value with 12 decimal places of precision.
