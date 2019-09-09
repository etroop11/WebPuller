import urllib.request as url
import csv
import numpy as np
import pandas as pd

def retrieve_player_ids(web_page, testing_alphabet):
	player_ids = []
	for l in testing_alphabet:

		directory_url = "http://www.chessgames.com/directory/" + l + '.html'
		print(directory_url)
		directory_page = url.urlopen(directory_url)
		directory_html = directory_page.read()

		limited_html = str(directory_html)
		#print(limited_html)
		while '/perl/chessplayer' in limited_html:
			#print("Locating next link...")
			try:
				try:
					index = limited_html.index('/perl/chessplayer')
				except:
					print('this is where the error is')
					index = -1
					break

				if(index != -1):
					#print(limited_html[index + 22:].index('"'))
					current_player_ID = limited_html[(index + 22):index + 22 + limited_html[index + 22:].index('"')]
					#print('currentplayerid' + current_player_ID + ".")
					player_ids.append(current_player_ID)
					limited_html = limited_html[(index + 22):]
					#print(index)
					#print(len(limited_html))
					#print(limited_html)
					#print('\n\n\n\n')

			except:
				print("Link not found, moving on.")
		print(len(player_ids))
		print("DONE with " + l)
	print("ALL IDS RETRIEVED")
	directory_page.close()
	return player_ids


def retreive_game_links(player_ids):
	game_links = []
	for player_id in player_ids:
		#print("ID is " + str(player_id))
		
		directory_url = "http://www.chessgames.com/perl/chessplayer?pid=" + player_id

		directory_page = url.urlopen(directory_url)
		directory_html = str(directory_page.read())

		string_to_search = 'Number of games in database: <B>'
		index = directory_html.index(string_to_search)
		
		#print("INDEX is " + str(index))

		num_string = directory_html[index + 32 : index + 32 + directory_html[index + 32:].index('</B>')]
		#print("NUM_STRING = " + num_string + ".")
		while ',' in num_string:
			ind = num_string.index(',')
			num_string = num_string[:ind] + num_string[ind + 1:]
		
		number = int(num_string)

		num_pages = int(number / 25)
		#print('NUM _PAGES = ' + str(num_pages) + ".")
		for page_num in range(num_pages):
			print("Player ID: " + str(player_id) + "| Page number : " + str(page_num + 1) + "/" + str(num_pages))
			#http://www.chessgames.com/perl/chess.pl?page=3&pid=67200
			second_directory_url = "http://www.chessgames.com/perl/chess.pl?page=" + str(page_num + 1) + "&pid=" + str(player_id)
			second_directory_page = url.urlopen(second_directory_url)
			second_directory_html = str(second_directory_page.read())
			second_limited_html = second_directory_html
			#print(second_directory_url)
			#print(second_limited_html)

			#print(('perl/chessgame?gid=') in second_limited_html)
			while 'perl/chessgame?gid=' in second_limited_html:
				#print("IN WHILE LOOP")
				start_index = second_limited_html.index("/perl/chessgame?")
				game_id = second_limited_html[start_index + 20: start_index + 20 + second_limited_html[start_index + 20:].index('"')]
				#print("Game id : " + str(game_id))
				second_limited_html = second_limited_html[start_index + 20 + second_limited_html[start_index + 20:].index('"'):]
				game_links.append(game_id)

		print('.....')

	return game_links



def retreive_game_data(game_ids):
	games = []
	for game_id in game_ids:
		print("Game id : " + str(game_id))
		game_url = "http://www.chessgames.com/perl/chessgame?gid=" + str(game_id)
		game_page = url.urlopen(game_url)
		game_html = str(game_page.read())
		limited_html = game_html

		first_cut_index = limited_html.index('[PlyCount "')
		#print(first_cut_index)
		limited_html = limited_html[first_cut_index + 11:]
		
		second_cut_index = limited_html.index(']')
		limited_html = limited_html[second_cut_index + 5:]

		end_index = limited_html.index("'") 

		game = limited_html[:end_index]
		#print(game)
		games.append(game)
	return games




def format_game_data(games):
	formatted_games = []
	for game in games:
		formatted_game = make_row_column(game)
		#print(formatted_game)

		game_arr = []
		ind = 1
		while (str(ind + 1) + ".") in formatted_game:
			current_index = formatted_game.index(str(ind) + ".")
			next_index = ''
			if (str(ind + 1) + ".") in formatted_game:
				next_index = formatted_game.index(str(ind + 1) + ".")
			elif str(" 0") in formatted_game:
				next_index = formatted_game.index(" 0")
			elif str(" 1") in formatted_game:
				next_index = formatted_game.index(" 1")
			else:
				print("Game formatting error")
				break
			current_string = formatted_game[current_index:next_index]
			current_string = current_string[len(str(ind) + '.'):]
			current_string = current_string.strip()
			game_arr.append(current_string)
			ind += 1

		formatted_games.append(game_arr)

	return formatted_games




def make_row_column(game):
	alphabet= "abcdefgh"
	index = 0
	for l in alphabet:
		while l in game:
			ind = game.index(l)
			game = game[:ind] + str(index) + game[ind + 1:]
		index += 1
	return game





#HERE IS WHERE ALL CALLS ARE MADE
#prolly should put this in a method
#then call individually by letter and make a seperate file for each


web_page = url.urlopen('http://www.chessgames.com/directory/')
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
testing_alphabet = alphabet


saved_player_ids = retrieve_player_ids(web_page, testing_alphabet)

print('...')
print()
print()	

testing_player_ids = saved_player_ids[:5]

game_ids = retreive_game_links(saved_player_ids)
#Testing
#game_ids = retreive_game_links(testing_player_ids)

print('...')
print()
print()	

testing_game_ids = game_ids[:5]

games = retreive_game_data(game_ids)
#Testing
#games = retreive_game_data(testing_game_ids)

formatted_games = format_game_data(games)

game_storage_array = np.array(formatted_games)
data_frame = pd.DataFrame(game_storage_array)
print(data_frame)
data_frame.to_csv("GameDatabase.csv")





