from dataclasses import dataclass
from flask import Flask, render_template, request
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import text
from datetime import datetime
from urllib.parse import unquote

server = os.environ['UD_HOST_NAME']
database = os.environ['UD_DB_NAME']
username = os.environ['UD_DB_USERNAME']
password = os.environ['UD_DB_PASSWORD']

nightStart = os.environ['NIGHT_START']
nightEnd = os.environ['NIGHT_END']

app = Flask(__name__)

connection_string = "mysql+mysqlconnector://{0}:{1}@{2}/vxs8596_user_directory".format(username,
                                                                                       password,
                                                                                       server)

engine = create_engine(connection_string)

app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

db = SQLAlchemy(app)


@dataclass
class Earthquake(db.Model):
    __tablename__ = 'earthquakes'
    id: str
    time: datetime
    latitude: float
    longitude: float
    depth: float
    mag: float
    magType: str
    nst: int
    gap: float
    dmin: float
    rms: float
    net: str
    updated: datetime
    place: str
    type: str
    horizontalError: float
    depthError: float
    magError: float
    magNst: int
    status: str
    locationSource: str
    magSource: str

    id = db.Column(db.String(200), primary_key=True, nullable=False)
    time = db.Column(db.TIMESTAMP)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    depth = db.Column(db.Float)
    mag = db.Column(db.Float)
    magType = db.Column(db.Text)
    nst = db.Column(db.Integer)
    gap = db.Column(db.Float)
    dmin = db.Column(db.Float)
    rms = db.Column(db.Float)
    net = db.Column(db.Text)
    updated = db.Column(db.TIMESTAMP)
    place = db.Column(db.Text)
    type = db.Column(db.Text)
    horizontalError = db.Column(db.Float)
    depthError = db.Column(db.Float)
    magError = db.Column(db.Float)
    magNst = db.Column(db.Integer)
    status = db.Column(db.Text)
    locationSource = db.Column(db.Text)
    magSource = db.Column(db.Text)


@app.route('/', methods=['GET'])
def home():
    page = getPageParam()
    items = getItemsParam()
    minMag = getMinMagParam()
    maxMag = getMaxMagParam()
    fromDate = getFromDateParam()
    toDate = getToDateParam()
    lat = getLatParam()
    lon = getLonParam()
    dist = getDistParam()
    night = getNightParam()
    return render_template('index.html',
                           data=fetchAllData(page, items, minMag, maxMag, fromDate, toDate, lat, lon, dist, night))


def getToDateParam():
    return datetime.strptime("6/14/2021" if not request.args.get('toDate') else unquote(request.args.get('toDate')),
                             '%m/%d/%Y')


def getFromDateParam():
    return datetime.strptime(
        "6/6/2021" if not request.args.get('fromDate') else unquote(request.args.get('fromDate')), '%m/%d/%Y')


def getMaxMagParam():
    return 6 if not request.args.get('maxMag') else float(request.args.get('maxMag'))


def getMinMagParam():
    return -1 if not request.args.get('minMag') else float(request.args.get('minMag'))


def getItemsParam():
    return 5 if not request.args.get('items') else int(request.args.get('items'))


def getPageParam():
    return 1 if not request.args.get('page') else int(request.args.get('page'))


def getLatParam():
    return None if not request.args.get('lat') else int(request.args.get('lat'))


def getLonParam():
    return None if not request.args.get('lon') else int(request.args.get('lon'))


def getDistParam():
    return None if not request.args.get('dist') else int(request.args.get('dist'))


def getNightParam():
    return False if not request.args.get('night') else request.args.get('night') == 'true'


@app.route('/status')
def hello_world():
    return "Hello World"


def fetchAllData(page: int, items: int, minMag: float, maxMag: float, fromDate: datetime, toDate: datetime, lat: float,
                 lon: float, dist: float, night: bool):
    global data
    distanceFIlterQuery = """
    6373.0 *
    (2 * ATAN2(SQRT(((POW(SIN((latitude - :lat) / 2), 2) +
    (COS(latitude) * COS(:lat) * POW(SIN((longitude - :lon) / 2), 2))))),
    SQRT(1 - ((POW(SIN((latitude - :lat) / 2), 2)) +
    (COS(latitude) * COS(:lat) * POW(SIN((longitude - :lon) / 2), 2)))))) <= :dist
    """
    nightFilterQuery = """
    time(time) between ':nightStart' and ':nightEnd'
    """
    if lat and lon and dist and night:
        distanceFilterQueryString = text(
            distanceFIlterQuery.replace(':lat', str(lat)).replace(':lon', str(lon)).replace(':dist', str(dist)))
        nightFilterQueryString = text(
            nightFilterQuery.replace(':nightStart', nightStart).replace(':nightEnd', nightEnd))

        data = Earthquake.query.filter(Earthquake.mag >= minMag).filter(Earthquake.mag <= maxMag).filter(
            Earthquake.time >= fromDate).filter(Earthquake.time <= toDate).filter(distanceFilterQueryString).filter(
            nightFilterQueryString).paginate(per_page=items,
                                             page=page,
                                             error_out=True)
    elif lat and lon and dist and not night:
        distanceFilterQueryString = text(
            distanceFIlterQuery.replace(':lat', str(lat)).replace(':lon', str(lon)).replace(':dist', str(dist)))
        data = Earthquake.query.filter(Earthquake.mag >= minMag).filter(Earthquake.mag <= maxMag).filter(
            Earthquake.time >= fromDate).filter(Earthquake.time <= toDate).filter(distanceFilterQueryString).paginate(
            per_page=items,
            page=page,
            error_out=True)
    elif (not lat or not lon or not dist) and night:
        data = Earthquake.query.filter(Earthquake.mag >= minMag).filter(Earthquake.mag <= maxMag).filter(
            Earthquake.time >= fromDate).filter(Earthquake.time <= toDate).paginate(per_page=items, page=page,
                                                                                    error_out=True)
        nightFilterQueryString = text(
            nightFilterQuery.replace(':nightStart', nightStart).replace(':nightEnd', nightEnd))

        data = Earthquake.query.filter(Earthquake.mag >= minMag).filter(Earthquake.mag <= maxMag).filter(
            Earthquake.time >= fromDate).filter(Earthquake.time <= toDate).filter(
            nightFilterQueryString).paginate(per_page=items, page=page,
                                             error_out=True)
    else:
        data = Earthquake.query.filter(Earthquake.mag >= minMag).filter(Earthquake.mag <= maxMag).filter(
            Earthquake.time >= fromDate).filter(Earthquake.time <= toDate).paginate(per_page=items, page=page,
                                                                                    error_out=True)
    return data


if __name__ == '__main__':
    app.run()
