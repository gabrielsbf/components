import pathlib
from pathlib import Path
class ProjectConfig:
	"""
	A class to manage project configuration settings.
	"""
	def __init__(self, find_root:str = 'srcs'):
		self.root_path = self.find_root_path(find_root)
	
	def find_root_path(self, find_root) -> Path | None:
		"""
		Finds the root path of the project by searching for a specific folder.
		
		Returns:
			str: The root path of the project.
		"""
		current_path = pathlib.Path(__file__).resolve()
		while current_path.name != find_root:
			current_path = current_path.parent
		return current_path.resolve() if current_path.name == find_root else None

