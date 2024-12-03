from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import pytz

# Connect to MongoDB

def prompt3():
    uri = "mongodb+srv://hao:hao1234@cluster0.15uea.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        # Access database and collection
        db = client['test']  # Replace with your database name
        collection = db['MacandCheese_virtual']  # Replace with your collection name

        # # Calculate the time three hours ago in PST
        utc_now = datetime.utcnow()
        pst = pytz.timezone('America/Los_Angeles')
        pst_now = utc_now.astimezone(pst)
        three_hours_ago_pst = pst_now - timedelta(hours=3)

        # # Convert PST time to UTC for MongoDB query
        three_hours_ago_utc = three_hours_ago_pst.astimezone(pytz.utc)

        # Query for fridge1 - anmeter
        fridge1_query = [
            {"$match": {
                "payload.ACS712 - Anmeter": {"$exists": True},
                "time": {"$gte": three_hours_ago_utc}
            }},
            {"$addFields": {
                "numeric-value": {"$toDouble": "$payload.ACS712 - Anmeter"},
                "timestamp_pst": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$time", "timezone": "America/Los_Angeles"}}
            }},
            {"$group": {
                "_id": None,
                "average": {"$avg": "$numeric-value"},
                "count": {"$sum": 1}
            }}
        ]

        # Query for fridge1 - anmeter
        fridge2_query = [
            {"$match": {
                "payload.sensor 2 637f4c4f-d074-4f27-9bfc-72d7231211ec": {"$exists": True},
                "time": {"$gte": three_hours_ago_utc}
            }},
            {"$addFields": {
                "numeric-value": {"$toDouble": "$payload.sensor 2 637f4c4f-d074-4f27-9bfc-72d7231211ec"},
                "timestamp_pst": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$time", "timezone": "America/Los_Angeles"}}
            }},
            {"$group": {
                "_id": None,
                "average": {"$avg": "$numeric-value"},
                "count": {"$sum": 1}
            }}
        ]

        # Query for dishwasher - anmeter
        dishwasher_query = [
            {"$match": {
                "payload.sensor 2 956b7932-b559-4cfc-8ba6-153d69083a9f": {"$exists": True},
                "time": {"$gte": three_hours_ago_utc}
            }},
            {"$addFields": {
                "numeric-value": {"$toDouble": "$payload.sensor 2 956b7932-b559-4cfc-8ba6-153d69083a9f"},
                "timestamp_pst": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$time", "timezone": "America/Los_Angeles"}}
            }},
            {"$group": {
                "_id": None,
                "average": {"$avg": "$numeric-value"},
                "count": {"$sum": 1}
            }}
        ]

        # Run the pipelines
        result_fridge1 = list(collection.aggregate(fridge1_query))
        result_fridge2 = list(collection.aggregate(fridge2_query))
        result_dishwasher = list(collection.aggregate(dishwasher_query))

        # Extract averages and counts for fridge1
        fridge1_average = result_fridge1[0]['average'] if result_fridge1 else 0
        fridge1_count = result_fridge1[0]['count'] if result_fridge1 else 0

        # Extract averages and counts for fridge2
        fridge2_average = result_fridge2[0]['average'] if result_fridge2 else 0
        fridge2_count = result_fridge2[0]['count'] if result_fridge2 else 0

        # Extract averages and counts for dishwasher
        dishwasher_average = result_dishwasher[0]['average'] if result_dishwasher else 0
        dishwasher_count = result_dishwasher[0]['count'] if result_dishwasher else 0

        # Calculate overall averages
        total_count = fridge1_count + fridge2_count + dishwasher_count
        overall_average = (
            (fridge1_average * fridge1_count +  fridge2_average * fridge2_count + dishwasher_average * dishwasher_count) / total_count
            if total_count > 0 else 0
        )

        # Print results
        output = (
            f"\n\nResults in PST (Pacific Standard Time): {pst_now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Average antmeter for fridge 1: {fridge1_average:.10f}\n"
            f"Average antmeter for fridge 2: {fridge2_average:.10f}\n"
            f"Average antmeter for fridge 3: {dishwasher_average:.10f}\n"
            f"Overall average anmeter: {overall_average:.10f}\n"
        )
        return output
    except Exception as e:
        print(f"Error: {e}")
