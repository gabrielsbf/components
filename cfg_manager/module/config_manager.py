from configparser import ConfigParser


class Read_config:
	def __init__(self, filepath, section = False):
		self.file = filepath
		self.section = section
		self.cred = self.get_cred()
	
	def get_cred(self):
		"""
        Get credentials from the configuration file.

        Returns:
            dict: Dictionary containing credentials.
        """
		parser = ConfigParser()
		parser.read(self.file)
		tuple_items = parser.items(self.section) if not self.section == False else parser.items()
		obj_items = {i[0] : i[1] for i in tuple_items}
		return obj_items


cfg = Read_config('config.ini')
print(cfg.cred['section_n'])