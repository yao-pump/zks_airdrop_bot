import pymongo
from pymongo import MongoClient

def connect_mongodb(host='localhost', port=27017):
    """
    Connect to the MongoDB server.
    
    :param host: MongoDB server hostname or IP (default: 'localhost')
    :param port: MongoDB server port (default: 27017)
    :return: MongoClient instance
    """
    client = MongoClient(host, port)
    return client

def insert_document(client, database, collection, document):
    """
    Insert a document into a MongoDB collection.
    
    :param database: Name of the database
    :param collection: Name of the collection
    :param document: Dictionary representing the document to be inserted
    :param host: MongoDB server hostname or IP (default: 'localhost')
    :param port: MongoDB server port (default: 27017)
    :return: The inserted document's ObjectID
    """
    db = client[database]
    coll = db[collection]
    
    result = coll.insert_one(document)
    return result.inserted_id

def insert_new_account(account_info):
    document = {'address': account_info['address'],
                'private_key': account_info['private_key'],
                'transactions': {}}
    
    insert_document(client, database='web3', collection='account', document=document)


# Example usage:
if __name__ == '__main__':
    # Connect to the MongoDB server
    client = connect_mongodb()
    
    # Insert a document into the 'test' database and 'example_collection' collection
    database_name = 'test'
    collection_name = 'example_collection'
    document = {
        'name': 'John Doe',
        'age': 30,
        'city': 'New York'
    }
    inserted_id = insert_document(database_name, collection_name, document)
    print(f'Document inserted with ObjectID: {inserted_id}')
