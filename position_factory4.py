import getting_a_position2 as getting_a_position

def get_n_positions(file_number):
	positions=[]
	position_solutions=[]
	i=0
	while (file_number<=19):
		file_name= f"{file_number}.pgn"
		f = open(file_name, encoding="utf-8")
		pgn=""

		line=f.readline()
		while line:
			pgn=pgn +line
			if "result" in line.lower():
				pgn=pgn + f.readline()
				pgn=pgn + f.readline()
				pgn=pgn + f.readline()
				i+=1
				try:
					generator_obj = getting_a_position.get_positions_and_moves_from_pgn(pgn)
					yield next(generator_obj)
					new_positions,new_moves=getting_a_position.get_positions_and_moves_from_pgn(pgn)
					for ret_x, ret_y in zip(new_positions,new_moves):
						yield ret_x, ret_y
				except Exception as e:
					print(e)

				pgn=""
			line=f.readline()
		f.close()
		print(file_number)
		file_number+=1
		if(file_number>19):
			file_number=1

	return (positions,position_solutions)

