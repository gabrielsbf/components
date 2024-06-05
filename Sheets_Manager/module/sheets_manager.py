import gspread
from Files_Handler.module.file_handler import Files_Handling
 
class Sheets_Manager(Files_Handling):

	def __init__(self, spread_link, service_cred, sec_service_cred=False):
		if sec_service_cred == False:
			self.ct = gspread.service_account(service_cred)
		else:
			try:
				self.ct = gspread.service_account(service_cred)
			except :
				print("Primeira Credencial Rejeitada, Tentando segunda.")
				self.ct = gspread.service_account(sec_service_cred)
		self.spreadsheet_obj = self.ct.open_by_url(spread_link)
		super().__init__()

	def create_sheet(self, worksheet_name):
		self.spreadsheet_obj.add_worksheet(worksheet_name, 1000, 10)

	def access_sheet(self, name):
		sheet_obj = self.spreadsheet_obj.worksheet(name)
		return sheet_obj

	def input_data(self, js_obj, sheet, cel_range, js_keys: list):
		obj_list = []
		for x in js_obj:
			obj_list.append([x[key] for key in js_keys])
		sheet.update(obj_list, cel_range)

	def get_line_response(self, wsheet_name, keyword, column_search:str,column_response:str):
		column_search_conv = ord(column_search.upper()) - 64
		cfg_sheet = self.spreadsheet_obj.worksheet(wsheet_name)
		filter = cfg_sheet.find(f"{keyword}",in_column=column_search_conv).row
		last_row = cfg_sheet.get_values(column_response + str(filter))
		return last_row[0][0]

	def find_cell_number(self, sheet_name, name_cell, number_column):
		sheet = self.spreadsheet_obj.worksheet(sheet_name)
		filter = sheet.find(f"{name_cell}", in_column=number_column).row
		return filter

	def insert_new_data(self, sheet_name, json_obj, first_column_name:str, js_keys,unique_id_col:int,  unique_id='shortUrl', range_cel='optional' ):
		first_cel = str(self.get_line_response('cfg', sheet_name, 'C', 'D')) if range_cel == "optional" else range_cel
		sheet = self.spreadsheet_obj.worksheet(sheet_name)
		new_json_obj = json_obj
		data = []
		for x in new_json_obj:
			if x['condition'] == 'new':
				data.append(x)
			elif x['condition'] == 'update':
				try: self.input_data([x], sheet,
					first_column_name + str(self.find_cell_number(sheet_name, x[unique_id], unique_id_col)),
					js_keys)
				except: print("OCORREU UM ERRO EM UPDATE -> os cards não foram atualizados...")
		if not data == []:
			self.input_data(data, sheet, first_column_name + first_cel, js_keys)
