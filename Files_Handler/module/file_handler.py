import os
import json

class Files_Handling():
	def __init__(self, pattern_folder):
		self.pattern_folder = pattern_folder
		self.set_folders(self.folder_to_test)

	def set_folders(self, folder_test):
		if folder_test == False:
			return 0
		if not os.path.exists(folder_test):
			print("PROCEDIMENTO DE PRIMEIRA EXECUÇÃO\n>>>Começando a criação de pastas...")
			os.makedirs(folder_test)
			print(">>>Processo Concluído")

	def write_file(self, input, filename, pattern_folder=True):
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
		if not pattern_folder == True:
			folder = pattern_folder
		else:
			folder = self.pattern_folder
		format = filename.split('.')[-1]
		if format == 'json':
			data = self.read_file(filename)
		data = data + input
		self.write_file(data, filename, folder)
		