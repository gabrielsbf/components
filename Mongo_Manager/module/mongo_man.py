
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils.env_p import URI, PATTERN_FOLDER
import pandas as pd
from src.components.Files_Handler.module.file_handler import Files_Handling


class Mongo_Manager(Files_Handling):
    def __init__(self, db_name):
        self.client = MongoClient(URI, server_api=ServerApi("1"))
        self.inventory = self.client[db_name]

    def insert_into_db(self, operation_type):
        """
        Inserts data into the database from a JSON file.

        This function reads data from a JSON file and inserts items into the database 
        based on the specified operation type.

        Args:
            operation_type (str): The type of operation that determines which set of 
            data will be inserted into the database. This value is used to access 
            the corresponding key in the JSON.

        Returns:
            "teste"
        """
        data = self.read_file("central.json", PATTERN_FOLDER)
        for key, value in data.items():
                docs = self.inventory[key].insert_many(value.get(operation_type))
                # print(f'O item foi adicionado!')
        # print(f'\nNumero de elementos inseridos no Banco de dados: [{len(docs.inserted_ids)}].')

    def edit_in_db(self, filter_db : dict, operation_type):
        """
    Updates documents in the database based on the provided filter.

    This function reads data from a JSON file and updates multiple documents 
    in the database that match the specified filter. The update is based on the 
    operation type specified, which determines the data to be used in the update.

    Args:
        filter_db (dict): A dictionary containing the filter criteria to match the documents 
        in the database that will be updated.
        operation_type (str): The type of operation that defines which set of data 
        will be used to update the documents. This value is used to access the 
        corresponding key in the JSON.

    Returns:
        pymongo.results.UpdateResult: The result of the update operation, including the 
        number of documents matched and modified.
    """
        data = self.read_file("central.json", PATTERN_FOLDER)
        for key, value in data.items():
            result = self.inventory[key].update_many(filter_db, {"$set": value.get(operation_type)[0]})
            # print(f'O elemento foi atualizado!')
        return result
    #verificar função
    def search_in_db(self, collection_name):
        db = self.inventory
        all_docs = []
        collection = db[collection_name]
        docs = collection.find()
        for doc in docs: 
            all_docs.append(doc)
        return all_docs
        
    def get_db_by_collection(self, collection_name, filter_by={}, remove_el={'_id': 0}):
        db = self.inventory
        all_docs = []
        # print("colection name is:", collection_name)
        collection = db[collection_name]
        docs = collection.find(filter_by, remove_el)
        for doc in docs:
            all_docs.append(doc)
        # print(all_docs)
        return all_docs
    
    def close_connection(self):
        try:
            self.client.close()
            # print("MongoDB connection closed successfully.")
        except Exception as e:
            print(f"Error closing the connection: {e}")

    def connection_teste(self):
        try:
            self.client.admin.command("ping")
            # print("Conectado ao MongoDB Atlas com sucesso!")
        except Exception as e:
            print(f"Erro na conexão: {e}")


    def reset_inv(self, collection):
        self.inventory.get_collection(collection).delete_many({})
        resp = {}
        if (collection == "categoria"):
            resp[collection] = {"categoria" : "lorem ipsum"}
        for key, value in resp.items():
                docs = self.inventory[key].insert_many([value])
                print(value)
                print(f'O item foi adicionado!')
    
    def print_db(self, collection):
        db_sample = self.inventory[collection]
        object_db = db_sample.find_one({'Email': 'Alex@mov'}, {"Email" : 1})