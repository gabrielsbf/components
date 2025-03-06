import requests
import os
from components.cfg_manager.module.config_manager import Read_config
from components.Files_Handler.module.file_handler import Files_Handling
from time import sleep

class Trello_Manager(Files_Handling):
	def __init__(self, boardname, credentials, boards_path, new_cards_path, list_allowed=["all"], section='trello'):
		"""
    Manages Trello operations.

    This class handles operations related to Trello boards, lists, and cards.

    Parameters:
        boardname (str): Name of the Trello board.
        credentials (str): Path to the configuration file.
        boards_path (str): Path to store Trello boards information.
        new_cards_path (str): Path to store new cards information.
        list_allowed (list): List of allowed lists.
        section (str, optional): Section in the configuration file (default: 'trello').
    """
		super().__init__(boards_path)
		self.boards_path = boards_path
		self.cred = Read_config(credentials, section).cred if type(credentials) == str else credentials
		self.boardname = boardname
		self.board_obj = self.set_board(self.get_boards())
		self.board_labels = self.make_request("/boards/" + self.board_obj["id"] + "/labels")
		self.lists = list_allowed
		self.new_cards = new_cards_path
	

	
	def make_request(self, endpoint):
		"""
        Make a request to the Trello API.

        Parameters:
            endpoint (str): API endpoint.

        Returns:
            dict: JSON response from the API.
        """
		api_token = self.cred['token']
		api_key = self.cred['key']
		domain = self.cred["domain"]
		url = domain + endpoint + '?key=' + api_key + '&token=' + api_token
		req = None
		for i in range(0, 11):
			try: 
				req = requests.get(url)
				break
			except: 
				print("error on request - Try nb: ", i)
				sleep(5)

		return req.json() if req != None else req

	def get_boards(self):
		"""
        Get Trello boards.

        Returns:
            dict: JSON response containing Trello boards.
        """
		trello_user =  self.cred['username']
		req = self.make_request('/members/' + trello_user + '/boards')
		return req

	def set_board(self, json_obj):
		"""
        Set the current Trello board.

        Parameters:
            json_obj (dict): JSON response containing Trello boards.

        Returns:
            str: Name of the Trello board if found, otherwise returns "Board não localizado".
        """
		for x in json_obj:
			if x['name'] == self.boardname:
				return x
		return "Board não localizado"

	def get_lists(self):
		"""
        Get lists of the current Trello board.

        Returns:
            dict: JSON response containing lists of the Trello board.
        """
		id = self.board_obj['id']
		req = self.make_request('/boards/' + id + '/lists')
		return req

	def get_listName_byId(self, list_id):
		"""
        Get the name of a list by its ID.

        Parameters:
            list_id (str): ID of the list.

        Returns:
            str: Name of the list.
        """
		lists_obj = self.get_lists()
		resp = list(filter(lambda x: x["id"] == list_id, lists_obj))
		return resp[0]['name']

	def get_listId_byName(self, list_name):
		"""
        Get the ID of a list by its name.

        Parameters:
            list_name (str): Name of the list.

        Returns:
            str: ID of the list.
        """
		lists_obj = self.get_lists()
		resp = list(filter(lambda x: x["name"] == list_name, lists_obj))
		return resp[0]['id']


	def get_cards_from_lists(self):
		"""
        Get cards from the allowed lists.

        Returns:
            dict: JSON response containing cards from the allowed lists.
        """
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
		"""
        Check if a card exists in the old cards.

        Parameters:
            check (dict): Card to check.
            old_cards (list): List of old cards.

        Returns:
            bool: True if the card exists in the old cards, False otherwise.
        """
		has_old_id = list(filter(lambda x : x['id'] == check['id'], old_cards))
		print("has old id" , has_old_id)
		return True if has_old_id == [] else False

	def check_elements(self, old, new):
		"""
    Check new or modified elements.

    This method compares new elements with old ones to identify which are new or have been modified.
    New or modified elements are marked with the condition 'new' or 'update', respectively.

    Parameters:
        old (list): List of old elements.
        new (list): List of new elements.

    Returns:
        list: List of new or modified elements, marked with the corresponding condition.
    """
		diference = []
		for check in new:
			if check not in old:
				check["condition"] = 'new' if self.check_cards(check, old) == True else 'update'
				print("value to check is:", check["name"],check["shortUrl"], "result is:", check["condition"])
				diference.append(check)
		return diference

	def first_exec(self, new_cards, all_cards_new= True):
			"""
    Executes the first run of the application.

    This method is called when the application is run for the first time. It creates necessary files
    to store information about the Trello board, including boards, lists, and cards. If `all_cards_new`
    is True, sets the state of new cards to 'new' and stores them in 'new_cards.json'.

    Parameters:
        new_cards (list): List of new cards.
        all_cards_new (bool, optional): Indicates if all cards are new (default: True).
    """
			print("FIRST EXEC")	
			if not os.path.exists(self.boardname + '_tempCards.json'):
				self.write_file([], self.boardname + '_tempCards.json')
			if not os.path.exists(self.new_cards):
				os.makedirs(self.new_cards)
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
		"""
    Verify new cards on the Trello board.

    This method compares the current state of the Trello board with the previously saved state to identify any new cards
    or modifications to existing cards. If new cards are found, they are stored in 'new_cards.json'.

    Returns:
        int: 0 if no new cards are found, 1 if new cards are identified.
    """
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
			self.write_file(new_cards, self.boardname + '_tempCards.json')
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
			

