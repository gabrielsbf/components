import os
import json

class Files_Handling():
	"""
    Handles file operations.

    This class provides methods to handle file operations such as writing, reading, and appending data to files.
    """
	def __init__(self, pattern_folder='./data/'):
		"""
        Initializes the Files_Handling object.

        Parameters:
            pattern_folder (str): Pattern folder path.
        """
		self.pattern_folder = pattern_folder
		self.set_folders(self.pattern_folder)

	def set_folders(self, folder_test):
		"""
        Sets up folders.

        Parameters:
            folder_test (bool): Flag to determine if folder setup is needed.
        """
		if folder_test == False:
			return 0
		if not os.path.exists(folder_test):
			print("PROCEDIMENTO DE PRIMEIRA EXECUÇÃO\n>>>Começando a criação de pastas...")
			os.makedirs(folder_test)
			print(">>>Processo Concluído")

	def write_file(self, input, filename, pattern_folder=True):
		"""
        Writes data to a file.

        Parameters:
            input (str or dict): Data to write.
            filename (str): Name of the file.
            pattern_folder (bool, optional): Flag to indicate if the pattern folder is used (default: True).
        """
		if not pattern_folder == True:
			folder = pattern_folder
		else:
			folder = self.pattern_folder
		format = filename.split('.')[-1]
		if format == 'json':
			file = open(folder + filename, "w", encoding="UTF-8")
			json.dump(input, file)
			file.close()
		else: 
			with open(self, folder + filename, "w", encoding="UTF-8") as file:
				file.write(input)
				file.close()

	def read_file(self, filename, pattern_folder=True):
		"""
        Reads data from a file.

        Parameters:
            filename (str): Name of the file.
            pattern_folder (bool, optional): Flag to indicate if the pattern folder is used (default: True).

        Returns:
            str or dict: Data read from the file.
        """
		if not pattern_folder == True:
			folder = pattern_folder
		else:
			folder = self.pattern_folder
		format = filename.split('.')[-1]
		with open(folder + filename, 'r', encoding='UTF-8') as file:
			data = file.read()
		if format == 'json':
			return json.loads(data)
		return data

	def append_file(self, input, filename, pattern_folder=True):
		"""
        Appends data to a file.

        Parameters:
            input (str or dict): Data to append.
            filename (str): Name of the file.
            pattern_folder (bool, optional): Flag to indicate if the pattern folder is used (default: True).
        """
		if not pattern_folder == True:
			folder = pattern_folder
		else:
			folder = self.pattern_folder
		try:
			data = self.read_file(filename, folder)
		except:
			data = []
		data = data + input
		self.write_file(data, filename, folder)
		