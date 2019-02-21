import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,inspect,func
import datetime as dt
from flask import Flask, jsonify
from dateutil.parser import parse


engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread':False})
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of the dates and temperature observations from a year from the last data point<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/><br/>"
        f"Examples of start or start-end range.:<br/>"
        f"<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23"
        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results =session\
             .query(Measurement.date, Measurement.prcp)\
              .all()
    
    all_precipitation = []
    for p in results:
        p_dict = {}
        p_dict["date"] = p.date
        p_dict["prcp"] = p.prcp
        all_precipitation.append(p_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def station():
    results = session.query(Station).all()
    all_station = []
    for s in results:
        all_station.append(object_as_dict(s))

    return jsonify(all_station)


@app.route("/api/v1.0/tobs")
def tobs():
    last_date=session.query(func.max(Measurement.date)).first()
    print(f"The last date entry in the data table {last_date[0]}")

    query_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d') - dt.timedelta(days=365)

    results=(session
             .query(Measurement.date, Measurement.tobs)
             .filter(Measurement.date >= query_date)
             .order_by(Measurement.date.desc())
             .all())

        all_result = []
    for r in results:
        r_dict = {}
        r_dict["date"] = r.date
        r_dict["tobs"] = r.tobs
        all_result.append(r_dict)

    return jsonify(all_result)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def tempagg(start,end=None):
    sel = [func.min(Measurement.tobs), 
           func.max(Measurement.tobs), 
           func.avg(Measurement.tobs)]
    
    if start is None or not is_date(start): 
         return jsonify({"error": f"Please specify start date."}), 404
        
    if end is None:
        results=(session
                     .query(*sel)
                     .filter(Measurement.date >= start)
                     .order_by(Measurement.date.desc())
                     .all())
    else:
        if not is_date(end): 
             return jsonify({"error": f"Please specify end date."}), 404
        
        results=(session
                     .query(*sel)
                     .filter(Measurement.date >= start, Measurement.date<=end)
                     .order_by(Measurement.date.desc())
                     .all())
all_result = []
    for r in results:
        r_dict = {}
        r_dict["min"] = r[0]
        r_dict["avg"] = r[1]
        r_dict["max"] = r[2]
        all_result.append(r_dict)

    return jsonify(all_result)

if __name__ == '__main__':
    app.run(debug=True)
