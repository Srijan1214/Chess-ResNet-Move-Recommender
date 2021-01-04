import getting_a_position

def get_n_positions(n):
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
				print('loading factory')

				# if(i%10000==0): print(len(positions))
				i+=1
				if(n<=len(positions)):
					yield (positions,position_solutions)
					# f = open(file_name, encoding="utf-8")
					positions=[]
					position_solutions=[]
				
				try:
					new_positions,new_moves=getting_a_position.get_positions_and_moves_from_pgn(pgn)
					positions.extend(new_positions)
					position_solutions.extend(new_moves)
				except Exception as e:
					print(e)

				pgn=""
			line=f.readline()
		f.close()
		file_number+=1
		if file_number >19: file_number = 1

	return (positions,position_solutions)

# generator_obj=get_n_positions(1000)

# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))

# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))

# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))

# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))

# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))

# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))

# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))
# print(len(generator_obj.__next__()[0]))
