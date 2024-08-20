import pymongo

class mongo_db:

    def __init__(self, connection_string, database) -> None:
        self.connection_string = connection_string
        self.database = database
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client[self.database]


    def insert_one(self, collection_name, document):
        """Insert a single document into the collection."""
        result = self.db[collection_name].insert_one(document)
        return result.inserted_id

    def insert_many(self, collection_name, documents):
        """Insert multiple documents into the collection."""
        result = self.db[collection_name].insert_many(documents)
        return result.inserted_ids

    def find_one(self, collection_name, query):
        """Find a single document in the collection."""
        result = self.db[collection_name].find_one(query)
        return result

    def find_many(self, collection_name, query, limit=0):
        """Find multiple documents in the collection."""
        results = self.db[collection_name].find(query).limit(limit)
        return list(results)

    def find_with_projection(self, collection_name, query, projection, limit=0):
        """Find documents in the collection with a specific projection."""
        results = self.db[collection_name].find(query, projection).limit(limit)
        return list(results)

    def update_one(self,collection_name,  query, update_values):
        """Update a single document in the collection."""
        result = self.db[collection_name].update_one(query, {'$set': update_values})
        return result.modified_count

    def update_many(self,collection_name,  query, update_values):
        """Update multiple documents in the collection."""
        result = self.db[collection_name].update_many(query, {'$set': update_values})
        return result.modified_count

    def delete_one(self,collection_name,  query):
        """Delete a single document from the collection."""
        result = self.db[collection_name].delete_one(query)
        return result.deleted_count

    def delete_many(self, collection_name, query):
        """Delete multiple documents from the collection."""
        result = self.db[collection_name].delete_many(query)
        return result.deleted_count

    def count_documents(self,collection_name,  query):
        """Count the number of documents matching the query."""
        count = self.db[collection_name].count_documents(query)
        return count

    def aggregate(self,collection_name,  pipeline):
        """Perform an aggregation on the collection."""
        result = self.db[collection_name].aggregate(pipeline)
        return list(result)

    def close(self,collection_name, ):
        """Close the connection to the MongoDB database."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.db[collection_name] = None
