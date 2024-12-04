from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import pytz
from timezonefinder import TimezoneFinder

def prompt1():
    # Connect to MongoDB
    uri = "mongodb+srv://hao:hao1234@cluster0.15uea.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        # Access database and collection
        db = client['test']  # Replace with your database name
        metadata_collection = db['MacandCheese_metadata'] 
        data_collection = db['MacandCheese_virtual'] 

        metadata = metadata_collection.find_one({
            "customAttributes.name": {"$in": ["Fridge", "Fridge2"]}
        })
        if not metadata:
            print("Warning: No metadata found for any fridge. Using defaults.")
            return "No metadata found for any fridge (Fridge or Fridge2)."
        

        # Debugging to identify field structure
        # print("Metadata Debugging:")
        # print(metadata)

        # Extract latitude and longitude
        latitude_field = metadata.get("latitude")
        longitude_field = metadata.get("longitude")

        # Handle cases where latitude/longitude is an integer or a nested dictionary
        try:
            latitude = float(latitude_field["$numberInt"]) if isinstance(latitude_field, dict) else float(latitude_field)
            longitude = float(longitude_field["$numberInt"]) if isinstance(longitude_field, dict) else float(longitude_field)
        except (TypeError, KeyError, ValueError) as e:
            print(f"Error parsing latitude/longitude: {e}")
            latitude = None
            longitude = None

        # Use TimezoneFinder to determine the time zone
        if latitude is not None and longitude is not None:
            tf = TimezoneFinder()
            device_time_zone = tf.timezone_at(lat=latitude, lng=longitude) or "America/Los_Angeles"
        else:
            device_time_zone = "America/Los_Angeles"


        pst = pytz.timezone("America/Los_Angeles")

        # Calculate the time three hours ago in PST
        utc_now = datetime.utcnow()
        pst_now = utc_now.astimezone(pst)
        three_hours_ago_pst = pst_now - timedelta(hours=3)
        three_hours_ago_utc = three_hours_ago_pst.astimezone(pytz.utc)

        # Query for DHT11 - moisture
        pipeline_dht11 = [
            {"$match": {
                "payload.DHT11 - moisture": {"$exists": True},
                "time": {"$gte": three_hours_ago_utc}
            }},
            {"$addFields": {
                "numeric-value": {"$toDouble": "$payload.DHT11 - moisture"},
                "timestamp_pst": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$time", "timezone": "America/Los_Angeles"}}
            }},
            {"$group": {
                "_id": None,
                "average": {"$avg": "$numeric-value"},
                "count": {"$sum": 1}
            }}
        ]

        # Query for sensor 3
        pipeline_sensor3 = [
            {"$match": {
                "payload.sensor 3 637f4c4f-d074-4f27-9bfc-72d7231211ec": {"$exists": True},
                "time": {"$gte": three_hours_ago_utc}
            }},
            {"$addFields": {
                "numeric-value": {"$toDouble": "$payload.sensor 3 637f4c4f-d074-4f27-9bfc-72d7231211ec"},
                "timestamp_pst": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$time", "timezone": "America/Los_Angeles"}}
            }},
            {"$group": {
                "_id": None,
                "average": {"$avg": "$numeric-value"},
                "count": {"$sum": 1}
            }}
        ]

        # Run the pipelines
        result_dht11 = list(data_collection.aggregate(pipeline_dht11))
        result_sensor3 = list(data_collection.aggregate(pipeline_sensor3))

        # Extract averages and counts for DHT11 - moisture
        dht11_average = result_dht11[0]['average'] if result_dht11 else 0
        dht11_count = result_dht11[0]['count'] if result_dht11 else 0

        # Extract averages and counts for sensor 3
        sensor3_average = result_sensor3[0]['average'] if result_sensor3 else 0
        sensor3_count = result_sensor3[0]['count'] if result_sensor3 else 0

        # Calculate overall averages
        total_count = dht11_count + sensor3_count
        overall_average = (
            (dht11_average * dht11_count + sensor3_average * sensor3_count) / total_count
            if total_count > 0 else 0
        )

        # Format the results as a string
        output = (
            f"\nResults in PST (Pacific Standard Time): {pst_now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Average moisture for DHT11 - moisture (RH%): {dht11_average:.10f}\n"
            f"Average moisture for sensor 3 (RH%): {sensor3_average:.10f}\n"
            f"Overall average moisture (RH%): {overall_average:.10f}\n"
            f"Total Records: {dht11_count + sensor3_count}\n"
        )
        return output
    
    except KeyError as e:
        return f"KeyError: Missing field in metadata: {e}"
    except Exception as e:
        print(f"Error: {e}")