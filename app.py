from dataclasses import dataclass
from flask import Flask, render_template, request
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
from urllib.parse import unquote
from urllib.parse import urlparse

server = os.environ['UD_HOST_NAME']
database = os.environ['UD_DB_NAME']
username = os.environ['UD_DB_USERNAME']
password = os.environ['UD_DB_PASSWORD']

app = Flask(__name__)

connection_string = "mysql+mysqlconnector://{0}:{1}@{2}/vxs8596_user_directory".format(username,
                                                                                       password,
                                                                                       server)

app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

db = SQLAlchemy(app)


@dataclass
class Earthquake(db.Model):
    __tablename__ = 'earthquakes2'
    time: datetime
    time2: int
    latitude: float
    longitude: float
    depth: float
    mag: float
    magType: str
    net: str
    place: str

    time2 = db.Column(db.Integer, primary_key=True, nullable=False)
    time = db.Column(db.TIMESTAMP)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    depth = db.Column(db.Float)
    mag = db.Column(db.Float)
    magType = db.Column(db.Text)
    net = db.Column(db.String)
    place = db.Column(db.Text)


@app.route('/', methods=['GET'])
def home():
    page = getPageParam()
    items = getItemsParam()
    minTime2 = getMinTime2Param()
    maxTime2 = getMaxTime2Param()
    fromDate = getFromDateParam()
    toDate = getToDateParam()
    return render_template('index.html', data=fetchAllData(page, items, minTime2, maxTime2, fromDate, toDate))


def getToDateParam():
    return datetime.strptime("6/16/2021" if not request.args.get('toDate') else unquote(request.args.get('toDate')),
                             '%m/%d/%Y')


def getFromDateParam():
    return datetime.strptime(
        "6/9/2021" if not request.args.get('fromDate') else unquote(request.args.get('fromDate')), '%m/%d/%Y')


def getMaxTime2Param():
    return 8000 if not request.args.get('maxTime2') else int(request.args.get('maxTime2'))


def getMinTime2Param():
    return 5000 if not request.args.get('minTime2') else int(request.args.get('minTime2'))


def getItemsParam():
    return 5 if not request.args.get('items') else int(request.args.get('items'))


def getPageParam():
    return 1 if not request.args.get('page') else int(request.args.get('page'))


@app.route('/status')
def hello_world():
    return "Hello World"


def fetchAllData(page: int, items: int, minTime2: float, maxTime2: float, fromDate: datetime, toDate: datetime):
    return Earthquake.query.filter(Earthquake.time2 >= minTime2).filter(Earthquake.time2 <= maxTime2).filter(
        Earthquake.time >= fromDate).filter(
        Earthquake.time <= toDate).order_by(desc(Earthquake.mag)).paginate(per_page=items, page=page,
                                                                           error_out=True)


if __name__ == '__main__':
    app.run()
