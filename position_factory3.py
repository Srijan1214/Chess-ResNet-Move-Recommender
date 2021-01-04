import numpy as np
import getting_a_position
import all_possible_moves

moves = all_possible_moves.get_all_possible_moves_in_chess()
moves = np.unique(np.array(moves))
OUTPUT_SIZE = moves.size

def get_n_positions():
	file_number =1
	positions=[]
	position_solutions=[]
	i=0
	while (file_number<=19):
		file_name= f"{file_number}.pgn"
		f = open(file_name, encoding="utf-8")
		pgn=""
		line=f.readline()
		moves_played = []
		while line:
			pgn=pgn +line
			if "result" in line.lower():
				pgn=pgn + f.readline()
				pgn=pgn + f.readline()
				pgn=pgn + f.readline()

				i+=1
				try:
					new_positions,new_moves=getting_a_position.get_positions_and_moves_from_pgn(pgn)
					for ret_x, ret_y in zip(new_positions,new_moves):
						ret_y = np.where(moves == ret_y)[0][0]
						#print(ret_y)
						ret_x = np.array(ret_x)
						#print(ret_x.shape)
						ret_x = np.array(ret_x).reshape(-1,8,1,1)
						temp = np.zeros(OUTPUT_SIZE)
						temp[ret_y] = 1
						#print(temp)
						yield (ret_x, ret_y)
				except Exception as e:
					print(e)

				pgn=""
			line=f.readline()
		f.close()
		file_number+=1
		if file_number >19: file_number = 1

	return (positions,position_solutions)

