def get_all_possible_moves_in_chess():
	file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
	rank = ['1', '2', '3', '4', '5', '6', '7', '8']
	all_squares = []
	all_moves = []
	for item_1 in file:
		for item_2 in rank:
			all_squares.append(item_1 + item_2)

	for item_1 in all_squares:
		for item_2 in all_squares:
			if (item_1!=item_2): all_moves.append(item_1 + item_2)

	all_moves.append('0-0')
	all_moves.append('0-0-0')

	return all_moves


