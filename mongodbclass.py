from pymongo import MongoClient

class MongoDBLink:
    def __init__(self, link_str=None, db_name='chatbot', collection_name='chathistory'):
        if link_str is None:
            self.db_exists = False
            return
        self.db_exists = True
        self.client = MongoClient(link_str)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_messages(self, key_id):
        results = []
        if not self.db_exists:
            return results
        messages_ = self.collection.find({'key_id': key_id}, {'_id': 0})
        for result in messages_:
            if result is not None:
                results.append(result)
        return results

    def print_all(self):
        if not self.db_exists:
            return
        for i in self.collection.find():
            print(i)

    def check_status(self):
        return self.client.server_info()

    def insert(self, data):
        if not self.db_exists:
            return
        self.collection.insert_one(data)

    def find(self, data):
        return self.collection.find(data)

    def find_one(self, data):
        if not self.db_exists:
            return None
        return self.collection.find_one(data)

    def get_all_id(self):
        key_ids = self.collection.find({}, {'key_id': 1})
        return [key_id['key_id'] for key_id in key_ids]

    def update(self, data, new_data):
        self.collection.update(data, new_data)

    def delete(self, data):
        self.collection.delete(data)

    def delete_one(self, key_id):
        self.collection.delete_one({'key_id': key_id})

    def delete_all(self):
        self.collection.delete_many({})

    def close(self):
        self.client.close()

