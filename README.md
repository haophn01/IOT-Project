**Assignment 7 : Build an End-to-End IoT System**
<br />
Hao Phan and Reyna Aguirre
<br />
<br />

***Overview of Assignment***

This project is an IoT data query system utilizes a tcp client-server architecture (used in assignment 6)  to process our specific queries related to the smart home devices. Our system fetches data from our MongoDB database (assignment 7) to then provide insights about:

1. The average moisture inside a kitchen fridge in the past three hours.
2. The average water consumption per cycle of a smart dishwasher.
3. The electricity consumption comparison among two refrigerators and a dishwasher.

***Features***

**TCP Client:**

- Accepts specific queries and sends them to the server.
- Validates inputs and provides user-friendly error messages for unsupported queries.
- Displays results received from the server.

**TCP Server:**

- Processes client queries and interacts with a MongoDB database.
- Calculates averages and compares metrics for IoT devices.
- Ensures results are provided in PST and appropriate units (e.g., RH%, gallons, kWh).

***Project Structure***

```client.py```: TCP client code that sends queries and receives responses

```server.py```: TCP server code that processes client queries and fetches data

```prompt1.py```: Handles the query for average moisture in the fridge.

```prompt2.py```: Handles the query for the average water consumption of the dishwasher.

```prompt3.py```: Handles the query for electricity consumption comparison.

***Prerequisites***
- MongoDB 
- Python 3.8 or higher
- ```pymongo``` python package [```pip install pymongo```]
- ```pytz``` python package [```pip install pymongo pytz```]
- ```timezonefinder``` python package [```pip install timezonefinder```]

***Getting Started***

**1. MongoDB Instance:**
- Update the ```uri``` variable in ```prompt1.py```, ```prompt2.py```, ```prompt3.py``` files with your MongoDB database URI.



**2. Running the Server:**
- Navigate to the project directory (ie. ```cd "C:\Users\reynaoaguirre\Documents\Assignment8"```)
- Start the server (ie ```python server.py```)
- Enter server (private) IP and desired port number (ie ```0.0.0.0``` for local testing)
- Now, the server will wait for client connections and handle queries using the database.



**3. Running the Client (New Separate Terminal):**
- Navigate to the project directory (ie. ```cd "C:\Users\reynaoaguirre\Documents\Assignment8"```)
- Start the server (ie ```python client.py```)
- Enter server (public) IP and desired port number (ie ```0.0.0.0``` for local testing)
- Now, select desired query (```1```, ```2```, ```3```, or ```exit```)
- View the server’s response and results to your query.


