# Import dependencies
from flask import Flask, request, redirect, jsonify
import numpy as np 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import datetime as dt


# SET UP FLASK APP
app = Flask(__name__)


# SET UP DATABASE & DB REFERENCES
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


# CREATE FLASK ROUTES
################################################################
@app.route("/")
# Home page.
# Lists all routes that are available...
def home():
    homepageHTML = (
        f"<h1>Welcome to the Hawaii Climate Analysis API!</h1>"
        f"<h2>Available API Endpoints:</h2><br/>"

        f"<h3>🌧 PRECIPITATION:</h3>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/><br/><br/><br/>"

        f"<h3>📡 STATIONS:</h3>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/><br/><br/><br/>"
        
        f"<h3>🌡 TEMPERATURE OBSERVATIONS:</h3>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/><br/><br/><br/>"

        f"<h3>📆 SPECIFIED START DATE:</h3>"
        f"<a href='/api/v1.0/yyyy-mm-dd'>/api/v1.0/yyyy-mm-dd</a><br/><br/><br/><br/>"

        f"<h3>📆 SPECIFIED START DATE & END DATE:</h3>"
        # f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
        f"<a href='/api/v1.0/yyyy-mm-dd/yyyy-mm-dd'>/api/v1.0/yyyy-mm-dd/yyyy-mm-dd</a><br/><br/><br/><br/>"
    )
    return homepageHTML


################################################################
@app.route("/api/v1.0/precipitation") 
# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
def precipitation():
    #Calculate data for last 12 months
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #create our session (link) from Python to the DB
    session = Session(engine)
    #Query Percipatation and date
    results = session.query(Measurement.date, Measurement.prcp).\
            filter (Measurement.date >= prev_year).all()
    
    #close out the session
    session.close()
    
    #Create a dictionary from the row data and append to a list of dates and precipitations
    data_prec = []

    for date, prcp in results:
        prcp_dict= {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp

        data_prec.append(prcp_dict)
    
    return jsonify(data_prec)



################################################################
@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset.
def stations():

#create our session (link) from Python to the DB
    session = Session(engine)
    #Query Percipatation and date
    results = session.query(Station.station, Station.name).all()
    
    #close out the session
    session.close()

    station_list = []

    for station, name in results:
        stat_name={}
        stat_name["station"] = station
        stat_name["name"] = name

        station_list.append(stat_name)
    
    return jsonify(station_list)


################################################################
@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
def temp():
    #create our session (link) from Python to the DB
    session = Session(engine)
    #create variable to focus on last 12 months
    lastyear = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lastyear, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)

    sel = [Measurement.date, Measurement.tobs]
    
    results = session.query(*sel).filter(Measurement.date >= querydate).all()
    
        #close out the session
    session.close()
    temps = list(np.ravel(results))
    return jsonify(stations=temps)



################################################################
@app.route("/api/v1.0/<start_date>")

def start_temp(start_date):
    #create our session (link) from Python to the DB
    session = Session(engine)
    
    
    #return min, max, average temp for a specific date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= 2017-8-23).all()

    #close out the session
    session.close()
    
    #create a dictionary with values

    start_values = []

    for min, avg, max in results:
        startdate_value = {}
        startdate_value["min_temp"] = min
        startdate_value["avg_temp"] = avg
        startdate_value["max_temp"] = max

        start_values.append(startdate_value)
    
    return jsonify(start_values)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_temp(start_date, end_date):

    session = Session(engine)
    
    
    #return min, max, average temp for a specific date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= 2016-8-18).filter(Measurement.date <= 2017-8-18).all()

    #close out the session
    session.close()
    
    #create a dictionary with values for state to end date
    range_values = []

    for min, avg, max in results:
        start_end_values ={}
        start_end_values["min_temp"] = min
        start_end_values["avg_temp"] = avg
        start_end_values["max_temp"] = max
        range_values.append(start_end_values)
    
    return jsonify(range_values)


# Run the Flask app that was created at the top of this file --> app = Flask(__name__)
################################################################
if __name__ == '__main__':
    app.run(debug=True) # set to false if deploying to a live website server (such as Google Cloud, Heroku, or AWS Elastic Beanstaulk)