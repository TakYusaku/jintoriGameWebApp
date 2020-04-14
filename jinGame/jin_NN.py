
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

class DQN_epsZero(nn.Module):
    def __init__(self, states, outputs, MAXDROPOUT_PR=.9):
        super(DQN_epsZero, self).__init__()
        self.states = states
        self.outputs = outputs
        self.MAXDROPOUT_PR = MAXDROPOUT_PR
        self.dropout_pr = MAXDROPOUT_PR
        self.step = 0
        self.OBSERVEPERIOD = 0
        self.fc = nn.Sequential(
            nn.Linear(self.states, 64),
            #nn.Dropout(self.dropout_pr),
            nn.LeakyReLU(),
            nn.Linear(64, 32),
            nn.Dropout(self.dropout_pr),
            nn.LeakyReLU(),
            nn.Linear(32, self.outputs)
        )
    def forward(self, x):
        x = self.fc(x.view(-1, self.states))
        #print(x.size())
        return x
"""
    def update_epsilon(self):
        LAMBDA = 0.0000001
        self.dropout_pr =  self.MAXDROPOUT_PR  * math.exp(-LAMBDA * self.step)
        for i in [4]:
            self.fc[i] = nn.Dropout(self.dropout_pr)
        self.step+=1
        #print(self.fc)
"""