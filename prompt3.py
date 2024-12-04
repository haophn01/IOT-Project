from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import pytz
from timezonefinder import TimezoneFinder

# Connect to MongoDB

def prompt3():
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
               "numeric-value-metric": {"$toDouble": "$payload.ACS712 - Anmeter"},
               "numeric-value-imperial": {"$multiply": [{"$toDouble": "$payload.ACS712 - Anmeter"}, 3412.14]},  # Convert kWh to BTU
               "timestamp_pst": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$time", "timezone": "America/Los_Angeles"}}
            }},
            {"$group": {
                "_id": None,
                "average-metric": {"$avg": "$numeric-value-metric"},
                "average-imperial": {"$avg": "$numeric-value-imperial"},
                "count": {"$sum": 1}
            }}
        ]

        # Query for fridge2 - anmeter
        fridge2_query = [
            {"$match": {
                "payload.sensor 2 637f4c4f-d074-4f27-9bfc-72d7231211ec": {"$exists": True},
                "time": {"$gte": three_hours_ago_utc}
            }},
            {"$addFields": {
                "numeric-value-metric": {"$toDouble": "$payload.sensor 2 637f4c4f-d074-4f27-9bfc-72d7231211ec"},
                "numeric-value-imperial": {"$multiply": [{"$toDouble": "$payload.sensor 2 637f4c4f-d074-4f27-9bfc-72d7231211ec"}, 3412.14]},  # Convert kWh to BTU
                "timestamp_pst": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$time", "timezone": "America/Los_Angeles"}}
            }},
            {"$group": {
                "_id": None,
                "average-metric": {"$avg": "$numeric-value-metric"},
                "average-imperial": {"$avg": "$numeric-value-imperial"},
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
                "numeric-value-metric": {"$toDouble": "$payload.sensor 2 956b7932-b559-4cfc-8ba6-153d69083a9f"},
                "numeric-value-imperial": {"$multiply": [{"$toDouble": "$payload.sensor 2 956b7932-b559-4cfc-8ba6-153d69083a9f"}, 3412.14]},  # Convert kWh to BTU
                "timestamp_pst": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$time", "timezone": "America/Los_Angeles"}}
            }},
            {"$group": {
                "_id": None,
                "average-metric": {"$avg": "$numeric-value-metric"},
                "average-imperial": {"$avg": "$numeric-value-imperial"},
                "count": {"$sum": 1}
            }}
        ]

        # Run the pipelines
        result_fridge1 = list(data_collection.aggregate(fridge1_query))
        result_fridge2 = list(data_collection.aggregate(fridge2_query))
        result_dishwasher = list(data_collection.aggregate(dishwasher_query))

        # Extract averages and counts for fridge1
        fridge1_metric_average = result_fridge1[0]['average-metric'] if result_fridge1 else 0
        fridge1_imperial_average = result_fridge1[0]['average-imperial'] if result_fridge1 else 0
        fridge1_count = result_fridge1[0]['count'] if result_fridge1 else 0

        # Extract averages and counts for fridge2
        fridge2_metric_average = result_fridge2[0]['average-metric'] if result_fridge2 else 0
        fridge2_imperial_average = result_fridge2[0]['average-imperial'] if result_fridge2 else 0
        fridge2_count = result_fridge2[0]['count'] if result_fridge2 else 0

        # Extract averages and counts for dishwasher
        dishwasher_metric_average = result_dishwasher[0]['average-metric'] if result_dishwasher else 0
        dishwasher_imperial_average = result_dishwasher[0]['average-imperial'] if result_dishwasher else 0
        dishwasher_count = result_dishwasher[0]['count'] if result_dishwasher else 0

        # Calculate overall averages
        total_count = fridge1_count + fridge2_count + dishwasher_count

        overall_metric_average = (
            (fridge1_metric_average * fridge1_count +
            fridge2_metric_average * fridge2_count +
            dishwasher_metric_average * dishwasher_count) / total_count
            if total_count > 0 else 0
        )

        overall_imperial_average = (
            (fridge1_imperial_average * fridge1_count +
            fridge2_imperial_average * fridge2_count +
            dishwasher_imperial_average * dishwasher_count) / total_count
            if total_count > 0 else 0
        )

        # Print results
        output = (
            f"\n\n---------------------------------------------------------------\n"
            f"Results in PST (Pacific Standard Time): {pst_now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Average antmeter for fridge 1 (Metric): {fridge1_metric_average:.10f} kWh\n"
            f"Average antmeter for fridge 1 (Imperial): {fridge1_imperial_average:.10f} BTU\n"
            f"Average antmeter for fridge 2 (Metric): {fridge2_metric_average:.10f} kWh\n"
            f"Average antmeter for fridge 2 (Imperial): {fridge2_imperial_average:.10f} BTU\n"
            f"Average antmeter for dishwasher (Metric): {dishwasher_metric_average:.10f} kWh\n"
            f"Average antmeter for dishwasher (Imperial): {dishwasher_imperial_average:.10f} BTU\n"
            f"Overall average antmeter (Metric): {overall_metric_average:.10f} kWh\n"
            f"Overall average antmeter (Imperial): {overall_imperial_average:.10f} BTU\n"
            f"Total Records: {total_count}\n"
            f"---------------------------------------------------------------\n"
        )

        return output
    except Exception as e:
        print(f"Error: {e}")
