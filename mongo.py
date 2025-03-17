from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

import os

class MongoInterface:
    def __init__(self):
        load_dotenv()

        self.client = MongoClient(os.getenv('DATABASE_URL'))
        self.db = self.client['raspberrypi']
        self.weather_col = self.db['weather_info']
        
    def insert_weather_data(self, document):
        if self.weather_col:
            self.weather_col.insert_one(document)
            return True
        return False
    
    def get_daily_average_temp(self, timestamp):
        start_of_day = datetime(timestamp.year, timestamp.month, timestamp.day, 0, 0, 0)
        end_of_day = datetime(timestamp.year, timestamp.month, timestamp.day, 23, 59, 59, 999999)
        
        query = {"timestamp": {"$gte": start_of_day, "$lte": end_of_day}}
        documents = self.weather_col.find(query)
        
        total_temp = 0
        count = 0
        
        for doc in documents:
            if 'temperature' in doc:
                total_temp += doc['temperature']
                count += 1
        
        if count == 0:
            return None
        
        average_temp = total_temp / count
        return average_temp
    
    def get_documents_after(self, timestamp):
        return self.weather_col.find({"timestamp": {"$gt": timestamp}})

    def get_documents_before(self, timestamp):
        return self.weather_col.find({"timestamp": {"$lt": timestamp}})

    def get_documents_between(self, start_timestamp, end_timestamp):
        return self.weather_col.find({"timestamp": {"$gte": start_timestamp, "$lte": end_timestamp}})

