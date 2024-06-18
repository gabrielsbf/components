import gspread
from components.Files_Handler.module.file_handler import Files_Handling
 
class Sheets_Manager(Files_Handling):
	"""
    Manages Google Sheets spreadsheets.

    This class handles operations related to Google Sheets spreadsheets.

    Parameters:
        spread_link (str): Link to the spreadsheet.
        service_cred (str): Google Sheets service credential.
        sec_service_cred (str, optional): Second Google Sheets service credential (default: False).
    """

	def __init__(self, spread_link, service_cred, sec_service_cred=False):
		"""
        Initializes the Sheets_Manager.

        Parameters:
            spread_link (str): Link to the spreadsheet.
            service_cred (str): Google Sheets service credential.
            sec_service_cred (str, optional): Second Google Sheets service credential (default: False).
        """
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
		"""
        Creates a new worksheet.

        Parameters:
            worksheet_name (str): Name of the worksheet.
        """
		self.spreadsheet_obj.add_worksheet(worksheet_name, 1000, 10)

	def access_sheet(self, name):
		"""
        Accesses a worksheet.

        Parameters:
            name (str): Name of the worksheet.

        Returns:
            gspread.Worksheet: Worksheet object.
        """
		sheet_obj = self.spreadsheet_obj.worksheet(name)
		return sheet_obj

	def input_data(self, js_obj, sheet, cel_range, js_keys: list):
		"""
        Inputs data into a worksheet.

        Parameters:
            js_obj (list): List of JSON objects.
            sheet (gspread.Worksheet): Worksheet.
            cel_range (str): Range of cells to input the data (e.g., "A1:B5").
            js_keys (list): List of keys of the JSON objects.
        """
		obj_list = []
		for x in js_obj:
			obj_list.append([x[key] for key in js_keys])
		sheet.update(obj_list, cel_range)

	def get_line_response(self, wsheet_name, keyword, column_search:str,column_response:str):
		"""
        """
		column_search_conv = ord(column_search.upper()) - 64
		cfg_sheet = self.spreadsheet_obj.worksheet(wsheet_name)
		filter = cfg_sheet.find(f"{keyword}",in_column=column_search_conv).row
		last_row = cfg_sheet.get_values(column_response + str(filter))
		return last_row[0][0]

	def find_cell_number(self, sheet_name, name_cell, number_column):
		"""
        Finds the cell number.

        Parameters:
            sheet_name (str): Name of the worksheet.
            name_cell (str): Name of the cell.
            number_column (int): Column number.

        Returns:
            int: Cell number.
        """
		sheet = self.spreadsheet_obj.worksheet(sheet_name)
		filter = sheet.find(f"{name_cell}", in_column=number_column).row
		return filter

	def insert_new_data(self, sheet_name, json_obj, first_column_name:str, js_keys,unique_id_col:int,  unique_id='shortUrl', range_cel='optional' ):
		"""
        Inserts new data into the worksheet.

        Parameters:
            sheet_name (str): Name of the worksheet.
            json_obj (list): List of JSON objects.
            first_column_name (str): Name of the first column.
            js_keys (list): List of keys of the JSON objects.
            unique_id_col (int): Column number for unique identification.
            unique_id (str): Key name for unique identification (default: 'shortUrl').
            range_cel (str): Cell range (optional).
        """
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
