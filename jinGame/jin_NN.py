
# coding: utf-8

import torch.nn as nn
import torch.nn.functional as F

class DQN(nn.Module):
    """
    states: features number,
    output: actions number
    """
    def __init__(self, states, outputs):
        super(DQN, self).__init__()
        self.states = states
        self.outputs = outputs
        self.fc = nn.Sequential(
            nn.Linear(self.states, 64),
#             nn.BatchNorm1d(32)
            nn.LeakyReLU(),
            nn.Linear(64, 64),
#             nn.BatchNorm1d(64)
            nn.LeakyReLU(),
#             nn.BatchNorm1d(9)
            nn.Linear(64, self.outputs)
        )

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, x):
        x = self.fc(x.view(-1, self.states))
        return x
