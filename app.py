# import dependencies and Flask
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all routes that are available.."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#design a Flask API based on the queries that you have just developed.

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #the query is for the last 12 months of the dataset.
    #Return the JSON representation of your dictionary.
    session = Session(engine)
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > '2016-08-23')\
      .order_by(Measurement.date).all()
 
    session.close()

    # Convert to Dictionary.
    date_precip = []
    for date, prcp  in precip:
        date_precip_dict = {}
        date_precip_dict["date"] = date
        date_precip_dict["prcp"] = prcp
        date_precip.append(date_precip_dict)

    return jsonify(date_precip)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of Stations.
    session = Session(engine)   
    stations = session.query(Station.station).all()
    
    session.close()  

    list_stations = list(stations)

    return jsonify(list_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    session = Session(engine)

    #query to find the most active station for last year of data.
    most_active_station_12_months = session.query(Measurement.station, func.count(Measurement.station))\
      .filter(Measurement.date > '2016-08-23')\
      .group_by(Measurement.station)\
      .order_by(func.count(Measurement.station).desc()).first()

    #query to find data of most active station for last year of data.
    data_most_active_station = session.query(Measurement.date, Measurement.tobs)\
      .filter(Measurement.date >= '2016-08-23')\
      .filter(Measurement.station == most_active_station_12_months[0]).all()

    session.close() 
    
    # Convert to Dictionary.
    date_tobs = []
    for date, tobs in data_most_active_station:
        date_tobs_dict = {}
        date_tobs_dict["date"] = date
        date_tobs_dict["tobs"] = tobs
        date_tobs.append(date_tobs_dict)

    return jsonify(date_tobs)

@app.route("/api/v1.0/start")
def start():
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature
    #for a given start.
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal
    #to the start date.
    session = Session(engine)
    
    #for this example query is used as start date 2016-01-01.
    stats_tobs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
      .filter(Measurement.date >= '2016-01-01').all()

    session.close() 

    #Create the dictionary.
    start_tobs = []
    for min, avg, max in stats_tobs:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min_temp"] = min
        start_date_tobs_dict["avg_temp"] = avg
        start_date_tobs_dict["max_temp"] = max
        start_tobs.append(start_date_tobs_dict)

    return jsonify(start_tobs)
    
@app.route("/api/v1.0/start/end")
def start_end():
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the
    #start and end date inclusive..
    session = Session(engine)

    #for this example query is used as start date 2016-01-01 (same as the above endpoint to check for the same results)
    # and end date 2017-08-24.
    stats_tobs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
      .filter(Measurement.date >= '2016-01-01')\
      .filter(Measurement.date <= '2017-08-23').all()

    session.close() 

    # Create a dictionary from the row data and append to a list of start_date_tobs
    start_end_tobs = []
    for min, avg, max in stats_tobs:
        start_end_date_tobs_dict = {}
        start_end_date_tobs_dict["min_temp"] = min
        start_end_date_tobs_dict["avg_temp"] = avg
        start_end_date_tobs_dict["max_temp"] = max
        start_end_tobs.append(start_end_date_tobs_dict)

    return jsonify(start_end_tobs)
    
if __name__ == "__main__":
    app.run(debug=True)

