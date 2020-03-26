#from jin_consts, jin_init_parameter_optim, jin_parameter, jin_replayMemory import *
import datetime
import math
import sys
import pandas as pd
import pickle
import random
import numpy as np
import mimetypes
import json
import copy
import os
import deque
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F