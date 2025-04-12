from multiprocessing.managers import BaseManager
import Queue
import sys


class QueueManager(BaseManager):
    pass


def main(ip, port):
    in_queue = Queue.Queue()
    out_queue = Queue.Queue()
    QueueManager.register('in_queue', callable=lambda:in_queue)
    QueueManager.register('out_queue', callable=lambda:out_queue)
    manager = QueueManager(address=(ip, int(port)), authkey='blah')
    server = manager.get_server()
    server.serve_forever()


if __name__ == '__main__':
    main(*sys.argv[1:])
