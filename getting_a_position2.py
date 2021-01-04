import chess.pgn
import io
import all_possible_moves

all_moves = all_possible_moves.get_all_possible_moves_in_chess()

def hash_position(data):
	data = data.encode("ascii")
	hash_ = 0xcbf29ce484222325
	for b in data:
		hash_ *= 0x100000001b3
		hash_ &= 0xffffffffffffffff
		hash_ ^= b
	return hash_


piece_dict = {
	"p": 11,
	"k": 14,
	"q": 19,
	"r": 15,
	"n": 13,
	"b": 13.5,
	"P": 1,
	"K": 4,
	"Q": 9,
	"R": 5,
	"N": 3,
	"B": 3.5,
	".": 0
}


def get_positions_and_moves_from_pgn(a):
	game_file = io.StringIO(a)
	first_game = chess.pgn.read_game(game_file)
	first_game.headers["Event"]

	board = first_game.board()
	position_count_dict = {}

	for i, move in enumerate(first_game.mainline_moves()):
		position_string = str(board)
		position_array_str = ([(x).split()
								for x in position_string.splitlines()])
		position = [[15, 13, 13.5, 19, 14, 13.5, 13, 15],
					[11, 11, 11, 11, 11, 11, 11, 11], [0, 0, 0, 0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1],
					[5, 3, 3.5, 9, 4, 3.5, 3, 5]]
		for r in range(8):
			for c in range(8):
				position[r][c] = piece_dict[position_array_str[r][c]]

		player_turn = [(i + 1) % 2 for x in range(8)]
		white_castling_rights = board.has_castling_rights(chess.WHITE)
		black_castling_rights = board.has_castling_rights(chess.BLACK)
		white_castling_rights = [int(white_castling_rights) for x in range(8)]
		black_castling_rights = [int(black_castling_rights) for x in range(8)]

		repetition = 0
		hashed_string = hash_position(position_string)
		if (hashed_string not in position_count_dict):
			position_count_dict[hashed_string] = 0
			repetition = [0 for x in range(8)]
		else:
			position_count_dict[hashed_string] += 1
			repetition = [position_count_dict[hashed_string] for x in range(8)]

		position.append(player_turn)
		position.append(white_castling_rights)
		position.append(black_castling_rights)
		position.append(repetition)

		yield_move = ""
		if (board.is_kingside_castling(move)):
			yield_move = "0-0"
		elif (board.is_queenside_castling(move)):
			yield_move = "0-0-0"
		else:
			yield_move = (str(move)[0:4])
		board.push(move)
		position.extend(
			get_possible_move_list(board, board.is_kingside_castling(move),
									board.is_queenside_castling(move)))
		yield(position,yield_move)


def get_possible_move_list(board, is_kingside_castling, is_queenside_castling):
	global all_moves
	legal_moves = []
	legal_moves_no_duplicates = []
	for item in board.legal_moves:
		legal_moves.append(str(item)[0:4])

	if (board.is_kingside_castling): legal_moves.append('0-0')
	if (board.is_queenside_castling): legal_moves.append('0-0-0')

	one_hot_encoded_list = [0 for x in range(len(all_moves))]

	count = 0
	for i, item in enumerate(all_moves):
		if (item in legal_moves):
			one_hot_encoded_list[i] = 1
			legal_moves_no_duplicates.append(item)
			count += 1
	legal_moves = legal_moves_no_duplicates
	if (count != len(legal_moves)):
		print("Error. Something is wrong.")
		print(legal_moves)
		print(count, "count")
		print(len(legal_moves), "legal_moves")
		for item in legal_moves:
			if (item not in all_moves):
				print(item)
		print("---------------------------------------------------------------")

	# length of last all moves is 4034 with is not divisible by 8. Take last two elements out ot make it divisible.
	var1 = one_hot_encoded_list[-2]
	var2 = one_hot_encoded_list[-1]
	return_list = []
	temp_list = []
	for i in range(len(one_hot_encoded_list) - 2):
		if (i != 0 and i % 8 == 0):
			return_list.append(temp_list.copy())
			temp_list = []
		temp_list.append(one_hot_encoded_list[i])
	return_list.append([var1 for x in range(8)])
	return_list.append([var2 for x in range(8)])

	return return_list
