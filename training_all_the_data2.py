import numpy as np
import all_possible_moves

moves = []
moves = all_possible_moves.get_all_possible_moves_in_chess()
print("done loading moves!!!")
moves = np.unique(np.array(moves))
OUTPUT_SIZE = moves.size

NUM_OF_POSITIONS_TO_LOAD = 7000

def load_next_positions(q, fileNumber):
	x_train, x_test, y_train, y_test = ([], [], [], [])
	buffer_positions = []
	buffer_position_solutions = []
	import position_factory2 as position_factory

	generator_obj = position_factory.get_n_positions(fileNumber)
	print('entered')

	temp_arr = []
	while(True):
		buffer_positions, buffer_position_solutions = generator_obj.__next__()

		final_output = np.where(moves == buffer_position_solutions)[0][0]
		temp_arr.append([buffer_positions,final_output])
		if(len(temp_arr) >= NUM_OF_POSITIONS_TO_LOAD):
			q.put(temp_arr)
			temp_arr = []


if __name__=='__main__':
	import importlib
	import tensorflow as tf
	from tensorflow import keras
	import matplotlib.pyplot as plt
	import multiprocessing
	from multiprocessing import Queue


	import model_generator
	import config
	Residual_CNN = model_generator.Residual_CNN
	model = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (517, 8, 1),
							OUTPUT_SIZE, config.HIDDEN_CNN_LAYERS)
	print(model.model.summary())

	x_train, x_test, y_train, y_test = ([], [], [], [])

	i = 1
	
	q= Queue()
	processess = []
	for i in range(1,7):
		p = multiprocessing.Process(target=load_next_positions, args=(q,i))
		p.start()
		processess.append(p)

	while (True):
		positions = []
		position_solutions = []
		#for counter in range(10):
		while(len(positions)<(30000*517*8)):
			(a, b) = zip(*(q.get()))
			positions = np.append(positions,a)
			position_solutions = np.append(position_solutions,b)
			print(positions.shape)

		print("loaded elements")
		#positions = np.array(positions)
		positions = positions.reshape(-1, 517, 8, 1)
		position_solutions = np.array(position_solutions)
		(x_train) = positions[:int(0.99*len(positions))]
		(x_test) = positions[:int(0.1*len(positions))]
		(y_train) = (position_solutions[:int(0.99*len(positions))])
		(y_test) = (position_solutions[:int(0.1*len(positions))])
		print(x_train.shape)
		model.model.fit(x_train, (y_train), epochs=1)
		print(f"Iteration {i}.    ", end="")
		print(model.model.evaluate(x_test, y_test))
		if(i%100==0):
			model.model.save(f"models/{i}_iteration_deep_neural_net.h5")
		i += 1
