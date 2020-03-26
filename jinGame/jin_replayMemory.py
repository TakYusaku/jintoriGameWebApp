import random
from collections import namedtuple

# define transition
Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward', 'userID'))

class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        # Saves a transition.
        overWriteFlag = True
        deleteItemID = -1
        if len(self.memory) < self.capacity:
            self.memory.append(None)
            overWriteFlag = False
        if overWriteFlag:
            deleteItemID = self.memory[self.position].itemID

        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity
        return overWriteFlag,deleteItemID

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
