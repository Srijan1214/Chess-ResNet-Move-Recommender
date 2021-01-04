import importlib
import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt

import pickle

positions = []
position_solutions = []
for i in range(1, 20, 1):
	with open(f'{i}_moves', 'rb') as f:
		position_solutions.extend(pickle.load(f))
	print("done loading moves!!!")

for i in range(1, 20, 1):
	with open(f'{i}_positions', 'rb') as f:
		positions.extend(pickle.load(f))
	print('Done loading positions!!!!!!')

print(len(positions))
print(len(position_solutions))

x_train = positions[:int(len(positions) * (697 / 700))]
x_train = np.array(x_train).reshape(-1, 12, 8, 1)

x_test = positions[-int(len(positions) * (3 / 700)):]
x_test = np.array(x_test).reshape(-1, 12, 8, 1)

output = np.unique(np.array(position_solutions))
OUTPUT_SIZE = output.size
print("Output Size is")
print(OUTPUT_SIZE)


def create_output_array(y_test, output):
	final_output = []
	for ele in position_solutions:
		index = np.where(output == ele)[0][0]
		final_output.append(index)
	return np.array(final_output)


final_output = create_output_array(position_solutions, output)
y_train = final_output[:int(len(positions) * (697 / 700))]
y_test = final_output[-int(len(positions) * (3 / 700)):]

print('Number of positions; ', len(positions))
print('Number of moves; ', len(position_solutions))

import model_generator
import config
importlib.reload(model_generator)
importlib.reload(config)
Residual_CNN = model_generator.Residual_CNN

model = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (12, 8, 1),
						OUTPUT_SIZE, config.HIDDEN_CNN_LAYERS)


print(model.model.summary())

for i in range(10000):
	model.model.fit(x_train, y_train, epochs=1)
	if ((i + 1) % 100 == 0):
		print(i)
	print(model.model.evaluate(x_test, y_test))
	model.model.save(f"models/{i}_iteration_deep_neural_net.h5")
