import pymongo
from pymongo import MongoClient
import random

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

def insert_new_account(client, account_info):
    document = {'address': account_info['address'],
                'private_key': account_info['private_key'],
                'transactions': {},
                'eth_main_balance': 0,
                'eth_zks_lite_balance': 0,
                'eth_zks_era_balance': 0,
                'syncswap_swap': 0,
                'sync_swap_liquidity': 0,
                'mute_swap': 0,
                'mute_liquidity': 0,
                'ot_swap': 0,
                'ot_liquidity': 0,
                'fund_from': '0x',
                'fund_to': '0x'}
    
    insert_document(client, database='web3', collection='accounts', document=document)


def get_all_accounts(client, database='web3', collection='accounts'):
    """
    Get all documents in a MongoDB collection.
    
    :param database: Name of the database
    :param collection: Name of the collection
    :param host: MongoDB server hostname or IP (default: 'localhost')
    :param port: MongoDB server port (default: 27017)
    :return: A list of documents
    """
    # client = connect_mongodb(host, port)
    db = client[database]
    coll = db[collection]

    documents = list(coll.find())
    return documents

def get_account(client, index=0, database='web3', collection='accounts'):
    accounts = get_all_accounts(client, database, collection)
    return accounts[index]

def get_random_account(client, database='web3', collection='accounts'):
    """
    Get a random document from a MongoDB collection.
    
    :param database: Name of the database
    :param collection: Name of the collection
    :param host: MongoDB server hostname or IP (default: 'localhost')
    :param port: MongoDB server port (default: 27017)
    :return: A single random document
    """

    db = client[database]
    coll = db[collection]

    count = coll.count_documents({})
    if count == 0:
        return None

    random_skip = random.randint(0, count - 1)
    random_document = coll.find().skip(random_skip).next()
    return random_document

def update_account(client, account_address, field_name, field_value, database='web3', collection='accounts'):
    """
    Update a document in a MongoDB collection by adding a new field.
    
    :param database: Name of the database
    :param collection: Name of the collection
    :param filter: Dictionary representing the filter criteria to select the document(s) to update
    :param field_name: Name of the new field to add
    :param field_value: Value of the new field to add
    :param host: MongoDB server hostname or IP (default: 'localhost')
    :param port: MongoDB server port (default: 27017)
    :return: UpdateResult instance
    """

    db = client[database]
    coll = db[collection]
    filter = {'address': account_address}
    update_result = coll.update_one(filter, {'$set': {field_name: field_value}})
    return update_result

# Example usage:
if __name__ == '__main__':
    client = connect_mongodb()
    account = get_random_account(client)
    update_account(client, account['address'], 'eth_main_balance', 0)
