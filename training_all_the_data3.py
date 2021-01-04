import numpy as np
import all_possible_moves
import position_factory3 as position_factory
import importlib
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt

moves = all_possible_moves.get_all_possible_moves_in_chess()
moves = np.unique(np.array(moves))
OUTPUT_SIZE = moves.size

import model_generator
import config
Residual_CNN = model_generator.Residual_CNN
model = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (8, 517, 1),
						OUTPUT_SIZE, config.HIDDEN_CNN_LAYERS)
print(model.model.summary())

x_train, x_test, y_train, y_test = ([], [], [], [])

i = 1

generator_obj = position_factory.get_n_positions()

model.model.fit(x = generator_obj, steps_per_epoch = 1000, max_queue_size = 10, verbose = 1, epochs=3, use_multiprocessing = True, workers = 10)

if(i%100==0):
	model.model.save(f"models/{i}_iteration_deep_neural_net.h5")
i += 1
