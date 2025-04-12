Data queue
-> taskNumber, vector X
-> task 1
-> task 2
....
-> task N
-> None


TASK [
matrix row_xi, - stringi
matrix row_xi +1,
...
]

NUMBER_OF_TASKS = min(32, vector size)
SIZE_OF_TASK = MATRIX_ROWS // NUMBER_OF_TASKS
REMAINDER = MATRIX_ROWS % NUMBER_OF_TASKS

Result queue

-> id, [
RESULT
RESULT
RESULT
]
-> id, [
RESULT
RESULT
RESULT
]
-> NONE
