import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all API routes"""
    return(
        f"Available Routes:<br/><br/>"

        f"/api/v1.0/precipitation<br/>"
        f"- Returns a list of precipiation for each day from 2016-08-23 to 2017-08-23.<br/><br/>"

        f"/api/v1.0/stations<br/>"
        f"- Returns a list of weather stations from the dataset. <br/><br/>"

        f"/api/v1.0/tobs<br/>"
        f"- Returns a list of temperature observations (tobs) from 2016-08-23 to 2017-08-23. <br/><br/>"

        f"(Note for the following routes: The earliest date is 2010-01-01 and the latest date is 2017-08-23.)<br/><br/>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"- When a date is entered as part of the route, returns the minimum, maximum and average temperature for a given date.<br/><br/>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"- When start and ends dates are entered as part of the route, returns the minimum, maximum and average temperature for a given period.<br/><br/>"
    )
# variable used in queries
begin_date = dt.date(2017, 8, 23) - dt.timedelta(days=366)

# ----------------------------
@app.route("/api/v1.0/precipitation")

def prcp():
    """Return dates and precipitation from 2016-08-23 to 2017-08-23."""
    # Query prcp and date for a given range
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > begin_date).\
    all()
    # Create a list for results
    prcp_list = [results]
    return jsonify(prcp_list)

# ----------------------------
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all stations
    results = session.query(Station).all()
    # Create a dictionary from the row data and append a list of all_stations
    all_stations = []
    for station in results:
        station_dict = {}
        station_dict["Station ID"] = station.station
        station_dict["Name"] = station.name
        station_dict["Station elevation"] = station.elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)
# ----------------------------
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of tobs for the latest 12 months of data."""
    # Query station name, date and tobs from tables
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
    filter(Measurement.date > begin_date).\
    all()
    # Create a dictionary from the row data and append a list of tobs_list
    tobs_list = []
    for tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = tobs.date
        tobs_dict["Station"] = tobs.name
        tobs_dict["Temperature"] = tobs.tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)
# ----------------------------
@app.route("/api/v1.0/<date>/")
def specific_date(date):
    """Return the average temp, max temp, and min temp for a given date"""
    # Query a specific date; return min and max temp and calc avg for a given date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date == date).\
    all()
    # Create a dictionary from the row data and append a list of temp_stats
    temp_stats = []
    for Tmin, Tmax, Tavg in results:
        temp_stats_dict = {}
        temp_stats_dict["Date"] = date
        temp_stats_dict["_Minimum Temperature"] = Tmin
        temp_stats_dict["_Maximum Temperature"] = Tmax
        temp_stats_dict["_Average Temperature"] = Tavg
        temp_stats.append(temp_stats_dict)
    return jsonify(temp_stats)
# ----------------------------
@app.route('/api/v1.0/<start_date>/<end_date>/')
def start_end_dates(start_date, end_date):
    """Return the avg, max, min, temp over a specific time period"""
    # Query a period of time; return min and max temp and calc avg for all dates within the time period
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date, Measurement.date <= end_date).\
    all()
    # Create a dictionary from the row data and append a list of begin_end_stats
    begin_end_stats = []
    for Tmin, Tmax, Tavg in results:
        begin_end_stats_dict = {}
        begin_end_stats_dict["01 Start Date"] = start_date
        begin_end_stats_dict["02 End Date"] = end_date
        begin_end_stats_dict["_Minimum Temperature"] = Tmin
        begin_end_stats_dict["_Maximum Temperature"] = Tmax
        begin_end_stats_dict["_Average Temperature"] = Tavg
        begin_end_stats.append(begin_end_stats_dict)
    return jsonify(begin_end_stats)

# ----------------------------

if __name__ == '__main__':
    app.run(debug=True)