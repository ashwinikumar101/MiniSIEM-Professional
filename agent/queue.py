# ==========================================
# MiniSIEM Agent
# Queue Manager
# ==========================================

from queue import Queue

from config import MAX_QUEUE_SIZE


event_queue = Queue(MAX_QUEUE_SIZE)


def push(event):

    event_queue.put(event)


def pop():

    if event_queue.empty():

        return None

    return event_queue.get()


def size():

    return event_queue.qsize()