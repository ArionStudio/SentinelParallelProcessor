%%writefile example0.py

from mpi4py import MPI

def main():
  comm = MPI.COMM_WORLD # komunikator zawierający wszystkie procesy
  id = comm.Get_rank() # id aktualnego procesu
  numProc = comm.Get_size() # liczba procesów w komunikatorze
  hostName = MPI.Get_processor_name() # nazwa maszyny na której uruchamiany jest program

  print(f"Jestem procesem nr {id} z {numProc} uruchamianym na maszynie {hostName}")

main()
