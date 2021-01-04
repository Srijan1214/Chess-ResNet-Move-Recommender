import numpy as np
import all_possible_moves
import multiprocessing
import ctypes

moves = []
moves = all_possible_moves.get_all_possible_moves_in_chess()
print("done loading moves!!!")
moves = np.unique(np.array(moves))
OUTPUT_SIZE = moves.size
POSITIONS_PER_BATCH = 50  #Should be an integer as other values depend on this fact.
NO_OF_CHILD_PROCESSES = 1
NO_OF_BATCHES_IN_MEMORY = 10
DIMENSION_OF_NUMPY_ARRAY = (POSITIONS_PER_BATCH * NO_OF_BATCHES_IN_MEMORY, 517,
							8, 1)
TOTAL_NO_OF_ELEMENTS = int(np.prod(np.array(DIMENSION_OF_NUMPY_ARRAY)))
NO_OF_ITEMS_PER_POSITION = DIMENSION_OF_NUMPY_ARRAY[
	1] * DIMENSION_OF_NUMPY_ARRAY[2]

import position_factory2 as position_factory


def load_positions(shared_x_array, shared_y_array, conditions_list,
					sync_lock_list, process_no):
	batch_no = 0
	file_number = int(((process_no + 1) / NO_OF_CHILD_PROCESSES) * 19)
	generator_obj = position_factory.get_n_positions(file_number)
	while (True):
		sync_lock_list[batch_no][process_no].acquire()
		if (conditions_list[batch_no][process_no].value == True):
			print("child waiting")
			sync_lock_list[batch_no][process_no].wait()

		# do stuff
		cur_size = int(POSITIONS_PER_BATCH / NO_OF_CHILD_PROCESSES)
		batch_start = batch_no * POSITIONS_PER_BATCH
		start = batch_start + process_no * cur_size
		end = start + cur_size
		if process_no == (NO_OF_CHILD_PROCESSES - 1):
			end = batch_start + POSITIONS_PER_BATCH
		no_of_positions = end - start
		y_start = start
		start *= NO_OF_ITEMS_PER_POSITION
		end *= NO_OF_ITEMS_PER_POSITION

		i = 0
		shared_array_idx = start
		while (i < no_of_positions):
			buffer_positions, buffer_position_solution = next(generator_obj)
			buffer_position_solution = np.where(
				moves == buffer_position_solution)[0][0]
			for ele1 in buffer_positions:
				for ele2 in ele1:
					shared_x_array[shared_array_idx] = ele2
					shared_array_idx += 1
			shared_y_array[i + y_start] = buffer_position_solution
			i += 1

		conditions_list[batch_no][process_no].value = True
		sync_lock_list[batch_no][process_no].notify_all()
		sync_lock_list[batch_no][process_no].release()
		batch_no += 1
		batch_no %= NO_OF_BATCHES_IN_MEMORY


if __name__ == '__main__':
	import importlib
	import tensorflow as tf
	from tensorflow import keras
	import matplotlib.pyplot as plt
	import model_generator
	import config
	Residual_CNN = model_generator.Residual_CNN
	model = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (517, 8, 1),
							OUTPUT_SIZE, config.HIDDEN_CNN_LAYERS)
	model.model = tf.keras.models.load_model(
		'models/600_iteration_deep_neural_net.h5')
	# print(model.model.summary())

	x_train, x_test, y_train, y_test = ([], [], [], [])

	shared_x_array = multiprocessing.RawArray(ctypes.c_double,
												TOTAL_NO_OF_ELEMENTS)
	shared_y_array = multiprocessing.RawArray(
		ctypes.c_longlong, NO_OF_BATCHES_IN_MEMORY * POSITIONS_PER_BATCH)
	sync_lock_list = [[
		multiprocessing.Condition() for j in range(NO_OF_CHILD_PROCESSES)
	] for i in range(NO_OF_BATCHES_IN_MEMORY)]
	conditions_list = [[
		multiprocessing.Value(ctypes.c_bool, False)
		for j in range(NO_OF_CHILD_PROCESSES)
	] for i in range(NO_OF_BATCHES_IN_MEMORY)]

	processes = []
	for process_no in range(NO_OF_CHILD_PROCESSES):
		p = multiprocessing.Process(target=load_positions,
									args=(shared_x_array, shared_y_array,
											conditions_list, sync_lock_list,
											process_no))
		processes.append(p)
		p.start()

	iteration = 0
	batch_no = 0

	while (True):
		### Wait for all the sub arrays in the batch to be ready
		for idx, ele in enumerate(sync_lock_list[batch_no]):
			print("parent", "ele.acquire()")
			ele.acquire()
			if (conditions_list[batch_no][idx].value == False):
				print("parent", "ele.wait()")
				ele.wait()

		for ele in conditions_list[batch_no]:
			assert (ele.value == True)  ### Assert that the batch is ready

		batch_start = batch_no * POSITIONS_PER_BATCH * NO_OF_ITEMS_PER_POSITION
		batch_end = batch_start + POSITIONS_PER_BATCH * NO_OF_ITEMS_PER_POSITION
		y_start = batch_no * POSITIONS_PER_BATCH
		# print(shared_x_array[int(TOTAL_NO_OF_ELEMENTS * batch_no /
		# 							NO_OF_BATCHES_IN_MEMORY
		# 							):int(TOTAL_NO_OF_ELEMENTS * (batch_no + 1) /
		# 								(NO_OF_BATCHES_IN_MEMORY))])

		x_train = np.frombuffer(buffer=shared_x_array,
								dtype=ctypes.c_double,
								count=POSITIONS_PER_BATCH *
								NO_OF_ITEMS_PER_POSITION,
								offset=batch_start*ctypes.sizeof(ctypes.c_double))
		y_train = np.frombuffer(buffer=shared_y_array,
								dtype=ctypes.c_longlong,
								count=POSITIONS_PER_BATCH,
								offset=y_start * ctypes.sizeof(ctypes.c_longlong))
		x_train.shape = (POSITIONS_PER_BATCH, 517, 8, 1)
		# print(x_train.dtype)
		# print(y_train.dtype)
		# print(np.array(y_train))
		print(x_train.shape)
		print(y_train.shape)

		### Take the array from batch as the batch should be available now.
		### Do the stuff

		model.model.fit(x_train, (y_train), epochs=1)
		# print(f"Iteration {iteration}.    ", end="")
		# print(model.model.evaluate(x_test, y_test))
		if (iteration % 100 == 0):
		 	model.model.save(
		 		f"models/{iteration}_iteration_deep_neural_net.h5")

		#Base batch unusable again.
		for idx, ele in enumerate(conditions_list[batch_no]):
			conditions_list[batch_no][idx].value = False
			sync_lock_list[batch_no][idx].notify_all()
			sync_lock_list[batch_no][idx].release()

		iteration += 1
		batch_no += 1
		batch_no %= NO_OF_BATCHES_IN_MEMORY
