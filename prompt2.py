from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import pytz
from timezonefinder import TimezoneFinder

# Connect to MongoDB
def prompt2():
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

        # Calculate the time three hours ago in PST
        utc_now = datetime.utcnow()
        pst = pytz.timezone('America/Los_Angeles')
        pst_now = utc_now.astimezone(pst)
        three_hours_ago_pst = pst_now - timedelta(hours=3)

        # # Convert PST time to UTC for MongoDB query
        three_hours_ago_utc = three_hours_ago_pst.astimezone(pytz.utc)

        # Query for DHT11 - moisture
        pipeline_watersensor = [
            {"$match": {
                "payload.YF-S201 - watersensor": {"$exists": True},
                "time": {"$gte": three_hours_ago_utc}
            }},
            {"$addFields": {
                "numeric-value-metric": {"$toDouble": "$payload.YF-S201 - watersensor"},
                "numeric-value-imperial": {"$multiply": [{"$toDouble": "$payload.YF-S201 - watersensor"}, 0.264172]},  # Conversion from liters to gallons
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
        result_watersensor = list(data_collection.aggregate(pipeline_watersensor))
    
        average_metric = result_watersensor[0]['average-metric'] if result_watersensor else 0
        average_imperial = result_watersensor[0]['average-imperial'] if result_watersensor else 0
        count = result_watersensor[0]['count'] if result_watersensor else 0


        # Calculate overall averages
        total_count = count 
        overall_average = (
            (average_imperial * count ) / total_count
            if total_count > 0 else 0
        )

        # Print results
        output = (
            f"\n\n---------------------------------------------------------------\n"
            f"Results in PST (Pacific Standard Time): {pst_now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Average water consumption (Metric - Liters): {average_metric:.4f} L\n"
            f"Average water consumption (Imperial - Gallons): {average_imperial:.4f} gal\n"
            f"Total Records: {count}\n"
            f"---------------------------------------------------------------\n"
        )
        return output

    except Exception as e:
        print(f"Error: {e}")
