import dotenv
import dotenv.variables  

class Read_env:
	def __init__(self, env_path):
		self.env_path = env_path
		self.env_info = dotenv.load_dotenv(self.env_path)
		
	def return_dict(self):
		return dotenv.dotenv_values(self.env_path)
		