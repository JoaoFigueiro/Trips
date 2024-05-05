# Trips
This project implements an automated process to ingest and store vehicle trip data, grouping it by similar origin, destination, and time. Additionally, it allows for filtering the data by specific region or area.

# Dependencies
  * python 3.9 or more
  * Install dependencies:   
    `pip install duckdb`  
    `pip install flask`

# Launching
To start the project, navigate to the project directory and run: 

`python app.py` 

Then, access the following URL in your browser: [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

# Basic Usage
1- **Filtering by Region**:
  * Enter the desired region in the first search box and click the Submit button.
    
2- **Filtering by Bounding Box**:
  * Enter the coordinates of the desired bounding box in the second search box in the format: latitude1 longitude1 latitude2 longitude2.
  * Example: 9.8470 53.4693 10.1499 53.6165 for Hamburg, Germany.
  * Click the `Submit` button.

To remove the filters, click in the `Clear filter` button. 

# Expected format of filtered data: 
  * Result after type "Prague" in the first search box.
![image](https://github.com/JoaoFigueiro/Trips/assets/93953665/353bc637-b48a-4be4-9517-13facefc3ae1)
