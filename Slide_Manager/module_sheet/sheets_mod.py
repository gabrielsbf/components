import requests
import gspread
from gspread import Spreadsheet
import json
from Files_Handler.module.file_handler import Files_Handling

#ESSE ARQUIVO IRÁ DIRETO PARA O REPOSITÓRIO DO FLUXO COMPROBATÓRIO
MONTHS = {
			1:'Janeiro',
			2:'Fevereiro',
			3:'Março',
			4:'Abril',
			5:'Maio',
			6:'Junho',
			7:'Julho',
			8:'Agosto',
			9:'Setembro',
			10:'Outubro',
			11:'Novembro',
			12:'Dezembro'
			}
			
class Sheet_Section(Files_Handling):
	def __init__(self, id_spreadsheet, service, data_folder):
		self.gc = gspread.service_account(service)
		self.id_spreadsheet = id_spreadsheet
		self.month = (0, 0)
		self.data_fd = data_folder
		super().__init__(data_folder)

	def access_url(self):
		return self.gc.open_by_url(self.id_spreadsheet)

	def	month_and_last_month(self, month_index: int):
		if MONTHS.get(month_index-1) == None:
			self.month = (MONTHS.get(12), MONTHS.get(month_index))
			return (MONTHS.get(12), MONTHS.get(month_index))
		else:
			self.month = (MONTHS.get(month_index-1), MONTHS.get(month_index)) 
			return (MONTHS.get(month_index-1), MONTHS.get(month_index))

	def pull_data(self, spreadsheet: Spreadsheet, wsheet_name : str, range: str):
		wsheet = spreadsheet.worksheet(wsheet_name)
		values = wsheet.get(range)
		header = values[0]
		data = values[1:-1]
		json_obj = []
		for i in data:
			row_obj = {}
			list(map(lambda x: row_obj.update({x: i[header.index(x)]}), header))
			json_obj.append(row_obj)
		return json_obj
	
	def delete_voids(self, filename):
		data = self.read_file(filename)
		for i in data:
			i['REDE'] = i[''] if i["REDE"] == '' else i['REDE']
			del i['']
			i[self.month[1]] = int(str(i[self.month[1]]).replace('.', ''))
			i[self.month[0]] = int(str(i[self.month[0]]).replace('.', ''))
		self.write_file(data, filename)
		return data
	
	def adjust_json(self, filename):
		data = self.read_file(filename)
		final_obj = []
		temp_dict = {}
		for key in data:
			cat = key['CATEGORIA']
			rede = key['REDE']
			if temp_dict.get(cat) == None and len(temp_dict) > 0:
				final_obj.append(temp_dict)
			if not temp_dict.get(cat) == None:
				if not temp_dict[cat].get(rede) == None:
					temp_dict[cat][rede].append({'SUBTIPO': key['SUBTIPO'], 'Atual': key[self.month[0]], 'Anterior': key[self.month[1]]})
				else:
					temp_dict[cat].update({rede:[{'SUBTIPO': key['SUBTIPO'], 'Atual': key[self.month[0]], 'Anterior': key[self.month[1]]}]})
			else:
				temp_dict.clear
				temp_dict[cat] = {rede:[{'SUBTIPO': key['SUBTIPO'], 'Atual': key[self.month[0]], 'Anterior': key[self.month[1]]}]}

		if temp_dict.get(cat) == None and len(temp_dict) > 0:
				final_obj.append(temp_dict)

	def menu(self):
		dat = int(input('Insira o index do mês desejado: '))
		self.write_file(self.pull_data(dat), self.month[1] +'.json')
		self.delete_voids(self.month[1] +'.json', dat)
		self.adjust_json(self.month[1] +'.json', dat)
		print("Arquivo Criado!")

