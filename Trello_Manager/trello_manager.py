import requests
import os
from srcs.classes.file_handler import Files_Handling
from utils.get_credentials import *
from utils.env_p import *

class Trello_Manager(Files_Handling):
	def __init__(self, boardname):
		super().__init__(TEST_ALL_FOLDERS)
		self.boardname = boardname
		self.cred = get_cred('trello_api')
		self.board_obj = self.set_board(self.get_boards())

	def make_request(self, endpoint):
		api_token = self.cred['token']
		api_key = self.cred['key']
		domain = self.cred["domain"]
		url = domain + endpoint + '?key=' + api_key + '&token=' + api_token
		req = requests.get(url)
		return req.json()

	def get_boards(self):
		trello_user =  self.cred['username']
		req = self.make_request('/members/' + trello_user + '/boards')
		return req

	def set_board(self, json_obj):
		for x in json_obj:
			if x['name'] == self.boardname:
				return x
		return "Board não localizado"

	def get_lists(self):
		id = self.board_obj['id']
		req = self.make_request('/boards/' + id + '/lists')
		return req

	def get_listName_byId(self, list_id):
		lists_obj = self.get_lists()
		resp = list(filter(lambda x: x["id"] == list_id, lists_obj))
		return resp[0]['name']

	def get_listId_byName(self, list_name):
		lists_obj = self.get_lists()

		resp = list(filter(lambda x: x["name"] == list_name, lists_obj))
		return resp[0]['id']


	def get_cards_from_lists(self, lists=LISTS_ALLOWED):
		if lists[0] == "all" and len(lists) == 1:
			board_id = self.board_obj['id']
			req = self.make_request('/boards/' + board_id + '/cards')
		else :
			arr_resp = []
			for i in lists:
				list_id = self.get_listId_byName(i)
				arr_resp.append(self.make_request('/lists/' + list_id + '/cards'))
			req = arr_resp[0]
		return req

	def check_cards(self, check, old_cards):
		has_old_id = list(filter(lambda x : x['id'] == check['id'], old_cards))
		return True if has_old_id == [] else False

	def check_elements(self, old, new):
		diference = []
		for check in new:
			if check not in old:
				check["condition"] = 'new' if self.check_cards(check, old) == True else 'update'
				diference.append(check)
		return diference

	def first_exec(self, new_cards, all_cards_new=BEGIN_NEW_CARDS):
			print("É a primeira execução do app\ncriando arquivos")
			self.write_file(self.board_obj, BOARD_NAME + '_boards.json')
			self.write_file(self.get_lists(), BOARD_NAME + '_lists.json')
			self.write_file(new_cards, BOARD_NAME + '_cards.json')
			if(all_cards_new == True):
				list(map(lambda x: x.update({'condition' : "new"}) ,new_cards))
				self.write_file(new_cards, 'new_cards.json', NEW_CARDS_PATH)
			else:
				self.write_file([], 'new_cards.json', NEW_CARDS_PATH)
	
	def verify_new_cards(self):
		# print("VERIFICANDO NOVOS CARDS...")
		new_cards = self.get_cards_from_lists()
		try:
			old_cards = self.read_file(BOARD_NAME + '_cards.json')
			self.read_file(BOARD_NAME + '_boards.json')
			self.read_file(BOARD_NAME + '_lists.json')
		except:
			self.first_exec(new_cards)
			return 1
		
		is_equal = new_cards == old_cards
		if is_equal == True:
			# print("Não há cards novos!")
			return 0
		else:
			print("Cards novos ou cards modificados foram identificados!")
			self.write_file(self.get_cards_from_lists(), BOARD_NAME + '_tempCards.json')
			new_cards_json = self.check_elements(old_cards, new_cards)
			new_cards_json = list(filter(lambda x: x['condition'] == 'new', new_cards_json))
			self.write_file(new_cards_json,
							'new_cards.json',
							NEW_CARDS_PATH)
			if len(new_cards_json) <= 0:
				print('cards modificados eram apenas updates, finalizando procedimento sem escrever em planilha')
				self.write_file(self.read_file(BOARD_NAME + '_tempCards.json'), BOARD_NAME + "_cards.json" )
				os.remove(BOARD_DATA_PATH + BOARD_NAME + '_tempCards.json')
				return 0
			else:
				print('Dados foram armazenados em new_cards.json do board específico!')
				return 1 
			

