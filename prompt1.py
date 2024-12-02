from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://hao:hao1234@cluster0.15uea.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    # Access database and collection
    db = client['test']  # Replace with your database name
    collection = db['MacandCheese_virtual']  # Replace with your collection name

    # Query for DHT11 - moisture
    pipeline_dht11 = [
        {"$match": {"payload.DHT11 - moisture": {"$exists": True}}},
        {"$addFields": {"numeric-value": {"$toDouble": "$payload.DHT11 - moisture"}}},
        {"$group": {"_id": None, "average": {"$avg": "$numeric-value"}, "count": {"$sum": 1}}}
    ]

    # Query for sensor 3
    pipeline_sensor3 = [
        {"$match": {"payload.sensor 3 637f4c4f-d074-4f27-9bfc-72d7231211ec": {"$exists": True}}},
        {"$addFields": {"numeric-value": {"$toDouble": "$payload.sensor 3 637f4c4f-d074-4f27-9bfc-72d7231211ec"}}},
        {"$group": {"_id": None, "average": {"$avg": "$numeric-value"}, "count": {"$sum": 1}}}
    ]

    # Run the pipelines
    result_dht11 = list(collection.aggregate(pipeline_dht11))
    result_sensor3 = list(collection.aggregate(pipeline_sensor3))

    # Extract averages and counts
    dht11_average = result_dht11[0]['average'] if result_dht11 else 0
    dht11_count = result_dht11[0]['count'] if result_dht11 else 0

    sensor3_average = result_sensor3[0]['average'] if result_sensor3 else 0
    sensor3_count = result_sensor3[0]['count'] if result_sensor3 else 0

    # Calculate overall average
    total_count = dht11_count + sensor3_count
    overall_average = (
        (dht11_average * dht11_count + sensor3_average * sensor3_count) / total_count
        if total_count > 0 else 0
    )

    # Print results
    print(f"Average for DHT11 - moisture: {dht11_average}")
    print(f"Average for sensor 3: {sensor3_average}")
    print(f"Overall average: {overall_average}")

except Exception as e:
    print(f"Error: {e}")
