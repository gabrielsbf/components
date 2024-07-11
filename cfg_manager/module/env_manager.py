import dotenv
import dotenv.variables  
from pathlib import Path
import os

class Read_env:
	def __init__(self, env_path:str, env_var=None):
		self.env_path = [env_path]
		self.env_values = {}
		self.set_envs(env_var)
		self.return_dict(self.env_values)

	def return_dict(self, index=1)->None:
		if len(self.env_path) == 1:
			values = dotenv.dotenv_values(self.env_path[0])
			self.env_values.update({**values})
		else:
			values = dotenv.dotenv_values(self.env_path[index])
			self.env_values.update({**values})

	def add_new_env(self, new_env_path:str, env_var=None)->None:
		self.env_path.append(new_env_path)
		self.set_envs(env_var)
		self.return_dict(-1)

	def set_envs(self, env_var: dict | None):
		if env_var == None:
			return 0
		else:
			for key, value in env_var.items():
				os.environ[key] = value
			self.env_values.update(env_var)