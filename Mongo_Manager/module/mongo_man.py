from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database, Collection
from pymongo.collection import InsertManyResult

class Mongo_Manager:
	def __init__(self, uri):
		self.client = MongoClient(uri, server_api=ServerApi('1'))

	def test_connection(self):
	
		try:
			self.client.admin.command('ping')
			print("Pinged your deployment. You successfully connected to MongoDB!")
		except Exception as e:
			print(e)

	def get_database(self, db_name: str)->Database | None:
		try:
			return self.client.get_database(db_name)
		except:
			return None

	def catch_collection(self, db: Database, collection_name: str) -> Collection:
		if db == None:
			return None
		return db.get_collection(collection_name)

	def validate_insert(self, valid_keys: list, values:list[dict]):
		if "_id" in valid_keys: valid_keys.remove("_id")
		for v in values:
			if len(valid_keys) > 0 and v in valid_keys:
				valid_keys.remove(v)
			else: 
				return IndexError(f"Valor {v} não é base na coleçaõ | Value {v} is not present in collection")
		if len(valid_keys) > 0:
			return IndexError(f"Existem chaves que precisam entrar na base de dados | There are values that needed to be filled", valid_keys)
		return True

	def data_insert(self, collection: Collection, values: list[dict]) -> InsertManyResult | None:
		if collection.estimated_document_count() == 0:
			print("first insert of database - inserting data")
			return collection.insert_many(values)
		else: 
			self.validate_insert([i for i in collection.find_one()], values)
			collection.insert_many(values)
			
	def reset_collection(self, collection: Collection):
		return collection.delete_many({})
	