# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement_tb = Base.classes.measurement
station_tb = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
conn = engine.connect()

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################


# 1. Define what to do when a user hits the index route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

#2. precipation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # calcualte from recent date minus past year
    last_date = session.query(measurement_tb.date.desc()).order_by(measurement_tb.date.desc()).first()[0]
    last_12 = dt.datetime.strptime(last_date,'%Y-%m-%d') - dt.timedelta(days=365)
    data = session.query(measurement_tb.date, measurement_tb.prcp).\
    filter(measurement_tb.date >= last_12).all()
    session.close()

    # Convert list of tuples into normal list
    all_data = list(np.ravel(data))

    return jsonify(all_data)


#3. stations
@app.route("/api/v1.0/stations")
def  stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

# Design a query to calculate the total number stations in the dataset
    number_stations = session.query(station_tb.station).\
                             group_by(station_tb.station).count()
    
    session.close()
    # Convert list of tuples into normal list
    all_data2 = list(np.ravel(number_stations))

    return jsonify(all_data2)


#3. tobs
@app.route("/api/v1.0/tobs")
def  tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

# Query the dates and temperature observations of 
# the most-active station for the previous year of data
    most_active = session.query(measurement_tb.station,func.count(measurement_tb.station)).\
    filter(station_tb.station == measurement_tb.station).group_by(measurement_tb.station).\
    order_by(func.count(station_tb.station).desc()).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_data3 = list(np.ravel(most_active))

    return jsonify(all_data3)


# Create function to validate input as specific date format YYYY-MM-DD
def validate(date_text):
    try:
        dt.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

#4. start
@app.route("/api/v1.0/<start>")
def start(startDate):
    if isinstance(startDate,str):
        print(f"One date passed - Determine agg funcs over date range")
        validate(startDate)
        # Create our session (link) from Python to the DB
        session = Session(engine)

        results = session.query(func.min(measurement_tb.tobs),\
                                func.avg(measurement_tb.tobs),\
                                func.max(measurement_tb.tobs)).\
                                filter(measurement_tb.date >= startDate).first()
        
        session.close()

        # Convert list of tuples into normal list
        temps_agg = list(np.ravel(results))
        return jsonify(temps_agg)
    return jsonify({"error": "Dates not found."}), 404

#5. start and end
# When given the start and end dates separated by a "/", calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<startDate>/<endDate>")
def temp_date_range(startDate,endDate):
    """Fetch the TMIN, TAVG and TMAX given a  start/end date
       variables supplied by the user, or a 404 if not."""
    
    if isinstance(endDate,str):
        print(f"Both Dates passed - Determine agg funcs over date range")
        validate(startDate)
        validate(endDate)
        # Create our session (link) from Python to the DB
        session = Session(engine)

        results = session.query(func.min(measurement_tb.tobs),\
                                func.avg(measurement_tb.tobs),\
                                func.max(measurement_tb.tobs)).\
                                filter(measurement_tb.date >= startDate).\
                                filter(measurement_tb.date <= endDate).first()
        
        session.close()

        # Convert list of tuples into normal list
        temps_agg = list(np.ravel(results))

        return jsonify(temps_agg)
    return jsonify({"error": "Dates not found."}), 404








if __name__ == '__main__':
    app.run(debug=True)