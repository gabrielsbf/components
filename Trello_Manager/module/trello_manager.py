import requests
import os
from cfg_manager.module.config_manager import Read_config
from configparser import ConfigParser
from Files_Handler.file_handler import Files_Handling


class Trello_Manager(Files_Handling):
	def __init__(self, boardname, cfg_path, boards_path, new_cards_path, list_allowed:list, section='trello'):
		super().__init__(boards_path)
		self.boards_path = boards_path
		self.cred = Read_config(cfg_path, section).cred
		self.boardname = boardname
		self.board_obj = self.set_board(self.get_boards())
		self.lists = list_allowed
		self.new_cards = new_cards_path
	

	
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


	def get_cards_from_lists(self):
		if self.lists[0] == "all" and len(self.lists) == 1:
			board_id = self.board_obj['id']
			req = self.make_request('/boards/' + board_id + '/cards')
		else :
			arr_resp = []
			for i in self.lists:
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

	def first_exec(self, new_cards, all_cards_new= True):
			print("É a primeira execução do app\ncriando arquivos")
			self.write_file(self.board_obj, self.boardname + '_boards.json')
			self.write_file(self.get_lists(), self.boardname + '_lists.json')
			self.write_file(new_cards, self.boardname + '_cards.json')
			if(all_cards_new == True):
				list(map(lambda x: x.update({'condition' : "new"}) ,new_cards))
				self.write_file(new_cards, 'new_cards.json', self.new_cards)
			else:
				self.write_file([], 'new_cards.json', self.new_cards)
	
	def verify_new_cards(self):
		# print("VERIFICANDO NOVOS CARDS...")
		new_cards = self.get_cards_from_lists()
		try:
			old_cards = self.read_file(self.boardname + '_cards.json')
			self.read_file(self.boardname + '_boards.json')
			self.read_file(self.boardname + '_lists.json')
		except:
			self.first_exec(new_cards)
			return 1
		
		is_equal = new_cards == old_cards
		if is_equal == True:
			# print("Não há cards novos!")
			return 0
		else:
			print("Cards novos ou cards modificados foram identificados!")
			self.write_file(self.get_cards_from_lists(), self.boardname + '_tempCards.json')
			new_cards_json = self.check_elements(old_cards, new_cards)
			new_cards_json = list(filter(lambda x: x['condition'] == 'new', new_cards_json))
			self.write_file(new_cards_json,
							'new_cards.json',
							self.new_cards)
			if len(new_cards_json) <= 0:
				print('cards modificados eram apenas updates, finalizando procedimento sem escrever em planilha')
				self.write_file(self.read_file(self.boardname + '_tempCards.json'), self.boardname + "_cards.json" )
				os.remove(self.boards_path + self.boardname + '_tempCards.json')
				return 0
			else:
				print('Dados foram armazenados em new_cards.json do board específico!')
				return 1 
			

