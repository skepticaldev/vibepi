import os
import numpy as np
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
print(config.sections())
