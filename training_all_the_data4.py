import numpy as np
import all_possible_moves
import multiprocessing


moves = []
moves = all_possible_moves.get_all_possible_moves_in_chess()
print("done loading moves!!!")
moves = np.unique(np.array(moves))
OUTPUT_SIZE = moves.size

NUM_OF_POSITIONS_TO_LOAD = 1000
NO_OF_WORKERS = 3

import position_factory2 as position_factory

def load_next_positions(conn,fileNumber):
	x_train, x_test, y_train, y_test = ([], [], [], [])
	buffer_positions = []
	buffer_position_solutions = []

	generator_obj = position_factory.get_n_positions(fileNumber)
	print('entered')


	while(True):
		postions = []
		postion_solutions = []
		for i in range(int(NUM_OF_POSITIONS_TO_LOAD/NO_OF_WORKERS)):
			buffer_positions, buffer_position_solutions = next(generator_obj)
			buffer_position_solutions = np.where(moves==buffer_position_solutions)[0][0]
			postions.append(buffer_positions)
			postion_solutions.append(buffer_position_solutions)
			if(i%int(NUM_OF_POSITIONS_TO_LOAD/(NO_OF_WORKERS*3))==0): print("loading ",i)
		conn.send([postions, postion_solutions])

def collect_positions(conn):
	parent_connections = []
	child_connections = []
	for i in range(NO_OF_WORKERS):
		parent_conn, child_conn = multiprocessing.Pipe()
		child_process= multiprocessing.Process(target=load_next_positions, args=(child_conn,i+1))
		parent_connections.append(parent_conn)
		child_connections.append(child_conn)
		child_process.start()

	while(True):
		position_solutions = np.empty((NUM_OF_POSITIONS_TO_LOAD), dtype = 'int64')
		positions = np.empty((NUM_OF_POSITIONS_TO_LOAD,517,8), dtype = 'float64')
		start_pos = 0
		end_pos = 0
		for parent_conn in parent_connections:
			p, move = parent_conn.recv()
			start_pos = end_pos
			end_pos = len(p) + start_pos
			positions[start_pos:end_pos] = p
			position_solutions[start_pos:end_pos] = move
			print("RECEIVING")
		print("SENDING")
		conn.send([positions,position_solutions])
		print("SENT")


if __name__=='__main__':
	import importlib
	import tensorflow as tf
	from tensorflow import keras
	import matplotlib.pyplot as plt


	import model_generator
	import config
	Residual_CNN = model_generator.Residual_CNN
	model = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (517, 8, 1),
							OUTPUT_SIZE, config.HIDDEN_CNN_LAYERS)
	model.model = tf.keras.models.load_model('models/600_iteration_deep_neural_net.h5')
	print(model.model.summary())

	x_train, x_test, y_train, y_test = ([], [], [], [])

	i = 1
	
	parent_conn, child_conn = multiprocessing.Pipe()
	child_process= multiprocessing.Process(target=collect_positions, args=(child_conn,)) 
	child_process.start()

	while (True):

		positions, position_solutions = parent_conn.recv()

		print("loaded elements")
		positions = positions.reshape(-1, 517, 8, 1)
		position_solutions = np.array(position_solutions)
		(x_train) = positions[:int(0.99*len(positions))]
		(x_test) = positions[:int(0.1*len(positions))]
		(y_train) = (position_solutions[:int(0.99*len(positions))])
		(y_test) = (position_solutions[:int(0.1*len(positions))])
		print("x_train",x_train.shape)
		print("y_train",y_train.shape)
		print("x_test",x_test.shape)
		print("y_test",y_test.shape)
		print("x_train_dtype",x_train.dtype)
		print("y_train_dtype",y_train.dtype)
		# model.model.fit(x_train, (y_train), epochs=1)
		# print(f"Iteration {i}.    ", end="")
		# print(model.model.evaluate(x_test, y_test))
		# if(i%100==0):
			# model.model.save(f"models/{i+600}_iteration_deep_neural_net.h5")
		i += 1
