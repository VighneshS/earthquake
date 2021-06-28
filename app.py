import datetime
import json
import os
from dataclasses import dataclass
from time import process_time
from urllib.parse import quote_plus
from urllib.parse import unquote
import random

import dateutil.parser
import pandas as pd
import sqlalchemy
from flask import Flask, render_template, request, url_for, send_from_directory, redirect, flash
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from pymongo import MongoClient
from sqlalchemy import create_engine, desc
from sqlalchemy import text
from flask import jsonify

server = os.environ['UD_HOST_NAME']
database = os.environ['UD_DB_NAME']
username = os.environ['UD_DB_USERNAME']
password = os.environ['UD_DB_PASSWORD']
tableName = os.environ['TABLE_NAME']

nightStart = os.environ['NIGHT_START']
nightEnd = os.environ['NIGHT_END']

secretKey = os.environ['SECRET_KEY']
redisHost = os.environ['REDIS_HOST']
redisPassword = os.environ['REDIS_PASSWORD']
mongoHost = os.environ['MONGO_HOST']

# Upload folder
UPLOAD_FOLDER = 'static'
FILE_NAME = 'all_month.csv'
RECORDS_TO_INSERT_OR_DELETE = 1000

app = Flask(__name__)
app.secret_key = secretKey

# enable debugging mode
app.config["DEBUG"] = True

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection_string = "mysql+pymysql://{0}:{1}@{2}/{3}?charset=utf8mb4".format(username, password, server, database)
connection_string_mongo = "mongodb+srv://{0}:{1}@{2}/{3}?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE".format(
    username, password, mongoHost, database)

app.config["MONGO_URI"] = connection_string_mongo
mongo = PyMongo(app)
client = MongoClient(connection_string_mongo)
mongoDb = client[database]
coll = mongoDb[tableName]
engine = create_engine(connection_string)

app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

db = SQLAlchemy(app)

inserted_ids = []

dataType = {
    "id": sqlalchemy.VARCHAR(200),
    "time": sqlalchemy.TIMESTAMP,
    "latitude": sqlalchemy.Float(),
    "longitude": sqlalchemy.Float(),
    "depth": sqlalchemy.Float(),
    "mag": sqlalchemy.Float(),
    "magType": sqlalchemy.VARCHAR(200),
    "nst": sqlalchemy.Integer(),
    "gap": sqlalchemy.Float(),
    "dmin": sqlalchemy.Float(),
    "rms": sqlalchemy.Float(),
    "net": sqlalchemy.VARCHAR(200),
    "updated": sqlalchemy.TIMESTAMP,
    "place": sqlalchemy.VARCHAR(200),
    "type": sqlalchemy.VARCHAR(200),
    "horizontalError": sqlalchemy.Float(),
    "depthError": sqlalchemy.Float(),
    "magError": sqlalchemy.Float(),
    "magNst": sqlalchemy.Integer(),
    "status": sqlalchemy.VARCHAR(200),
    "locationSource": sqlalchemy.VARCHAR(200),
    "magSource": sqlalchemy.VARCHAR(200)
}


@dataclass
class Earthquake(db.Model):
    __tablename__ = tableName
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
    time = db.Column(sqlalchemy.TIMESTAMP)
    latitude = db.Column(sqlalchemy.Float())
    longitude = db.Column(sqlalchemy.Float())
    depth = db.Column(sqlalchemy.Float())
    mag = db.Column(sqlalchemy.Float())
    magType = db.Column(sqlalchemy.VARCHAR(200))
    nst = db.Column(sqlalchemy.Integer())
    gap = db.Column(sqlalchemy.Float())
    dmin = db.Column(sqlalchemy.Float())
    rms = db.Column(sqlalchemy.Float())
    net = db.Column(sqlalchemy.VARCHAR(200))
    updated = db.Column(sqlalchemy.TIMESTAMP)
    place = db.Column(sqlalchemy.VARCHAR(200))
    type = db.Column(sqlalchemy.VARCHAR(200))
    horizontalError = db.Column(sqlalchemy.Float())
    depthError = db.Column(sqlalchemy.Float())
    magError = db.Column(sqlalchemy.Float())
    magNst = db.Column(sqlalchemy.Integer())
    status = db.Column(sqlalchemy.VARCHAR(200))
    locationSource = db.Column(sqlalchemy.VARCHAR(200))
    magSource = db.Column(sqlalchemy.VARCHAR(200))


@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8') if s else ''
    s = quote_plus(s)
    return Markup(s)


def getToDateParam():
    return datetime.datetime.strptime(
        "6/20/2021" if not request.args.get('toDate') or request.args.get('toDate') == 'None' else unquote(
            request.args.get('toDate')), '%m/%d/%Y')


def getFromDateParam():
    return datetime.datetime.strptime(
        "5/1/2021" if not request.args.get('fromDate') or request.args.get('fromDate') == 'None' else unquote(
            request.args.get('fromDate')), '%m/%d/%Y')


def getMaxMagParam():
    return 6 if not request.args.get('maxMag') or request.args.get('maxMag') == 'None' else float(
        request.args.get('maxMag'))


def getMinMagParam():
    return -1 if not request.args.get('minMag') or request.args.get('minMag') == 'None' else float(
        request.args.get('minMag'))


def getItemsParam():
    return 5 if not request.args.get('items') or request.args.get('items') == 'None' else int(
        request.args.get('items'))


def getPageParam():
    return 1 if not request.args.get('page') or request.args.get('page') == 'None' else int(request.args.get('page'))


def getLatParam():
    return None if not request.args.get('lat') or request.args.get('lat') == 'None' else float(request.args.get('lat'))


def getLonParam():
    return None if not request.args.get('lon') or request.args.get('lon') == 'None' else float(request.args.get('lon'))


def getDistParam():
    return None if not request.args.get('dist') or request.args.get('dist') == 'None' else float(
        request.args.get('dist'))


def getNightParam():
    return False if not request.args.get('night') or request.args.get('night') == 'None' else request.args.get(
        'night') == 'true'


def getNetParam():
    return None if not request.args.get('net') or request.args.get('net') == 'None' else request.args.get('net')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/analyse', methods=['GET'])
def analyse():
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
    net = getNetParam()
    return render_template('analyse.html',
                           data=fetchAllData(page, items, minMag, maxMag, fromDate, toDate, lat, lon, dist, night, net))


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/crud', methods=['GET'])
def crud():
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
    net = getNetParam()
    return render_template('crud.html',
                           data=fetchAllData(page, items, minMag, maxMag, fromDate, toDate, lat, lon, dist, night, net))


@app.route('/graphs/<questionNumber>', methods=['GET', 'POST'])
def graphs(questionNumber: int):
    if int(questionNumber) == 1:
        if request.method == 'POST':
            return fetchAllDataForGraph(request.get_json())
        else:
            return render_template('graphs.html')
    else:
        if request.method == 'POST':
            return fetchAllDataForMagDepthGraph(request.get_json()['numberOfItems'])
        else:
            return render_template('graphs2.html')


@app.route('/crudMongo', methods=['GET'])
def crudMongo():
    minMag = getMinMagParam()
    maxMag = getMaxMagParam()
    fromDate = getFromDateParam()
    toDate = getToDateParam()
    net = getNetParam()
    return render_template('crudMongo.html',
                           data=fetchAllDataMongo(minMag, maxMag, fromDate, toDate, net))


@app.route('/status')
def hello_world():
    return "Hello World"


def fetchAllData(page: int, items: int, minMag: float, maxMag: float, fromDate: datetime, toDate: datetime, lat: float,
                 lon: float, dist: float, night: bool, net: str):
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
    distanceFilterQueryString = text(
        distanceFIlterQuery.replace(':lat', str(lat)).replace(':lon', str(lon)).replace(':dist', str(dist)))
    nightFilterQueryString = text(
        nightFilterQuery.replace(':nightStart', nightStart).replace(':nightEnd', nightEnd))
    try:
        q = Earthquake.query.filter(Earthquake.mag >= minMag).filter(Earthquake.mag <= maxMag).filter(
            Earthquake.time >= fromDate).filter(Earthquake.time <= toDate)
        if net:
            q = q.filter(Earthquake.net == net)
        if night:
            q = q.filter(nightFilterQueryString)
        if lat and lon and dist:
            q = q.filter(distanceFilterQueryString)
        data = q.paginate(per_page=items,
                          page=page,
                          error_out=True)
    except sqlalchemy.exc.ProgrammingError:
        data = []
    return data


def fetchAllDataForGraph(range: list):
    try:
        global data
        data = []
        q = '''select case '''
        qTail = ''' else 'OTHERS'
            end  as `magRange`,
            count(1) as `Count`
            from earthquakes
            group by magRange'''
        for r in range:
            q += " when mag between {f} and {t} then '{f}-{t}' ".replace('{f}', str(r['from'])).replace('{t}',
                                                                                                        str(r['to']))
        q += qTail
        with engine.connect() as con:
            rs = con.execute(q)
            for row in rs:
                value = {'magRange': row[0], 'value': row[1]}
                data.append(value)
    except sqlalchemy.exc.ProgrammingError:
        data = []
    return jsonify(data)


def fetchAllDataForMagDepthGraph(numberOfItems: int):
    try:
        global data
        data = []
        results = Earthquake.query.with_entities(Earthquake.mag, Earthquake.depth).order_by(
            desc(Earthquake.time)).limit(numberOfItems).all()
        for row in results:
            data.append([row[0], row[1]])
    except sqlalchemy.exc.ProgrammingError:
        data = []
    return jsonify(data)


def fetchAllDataMongo(minMag: float, maxMag: float, fromDate: datetime, toDate: datetime, net: str):
    global data
    data = []
    query = [{"mag": {
        "$gte": minMag,
        "$lte": maxMag
    }}, {
        "time": {
            "$gte": str(fromDate.strftime("%Y-%m-%d %H:%M:%S")),
            "$lte": str(toDate.strftime("%Y-%m-%d %H:%M:%S"))
        }}]
    if net:
        query.append({"net": net})
    data = mongo.db[tableName].find({'$and': query})
    return data


def deleteAllData(minMag: float, maxMag: float, fromDate: datetime, toDate: datetime, lat: float,
                  lon: float, dist: float, night: bool, net: str):
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
    distanceFilterQueryString = text(
        distanceFIlterQuery.replace(':lat', str(lat)).replace(':lon', str(lon)).replace(':dist', str(dist)))
    nightFilterQueryString = text(
        nightFilterQuery.replace(':nightStart', nightStart).replace(':nightEnd', nightEnd))
    try:
        q = Earthquake.query.filter(Earthquake.mag >= minMag).filter(Earthquake.mag <= maxMag).filter(
            Earthquake.time >= fromDate).filter(Earthquake.time <= toDate)
        if net:
            q = q.filter(Earthquake.net == net)
        if night:
            q = q.filter(nightFilterQueryString)
        if lat and lon and dist:
            q = q.filter(distanceFilterQueryString)
        ids_to_delete = []
        for value in q.all():
            ids_to_delete.append(value.id)
        delete_q = Earthquake.__table__.delete().where(Earthquake.id.in_(ids_to_delete))
        db.session.execute(delete_q)
        db.session.commit()
    except sqlalchemy.exc.ProgrammingError:
        flash('Table not found', 'danger')


def deleteAllDataMongo(minMag: float, maxMag: float, fromDate: datetime, toDate: datetime, net: str):
    query = [{"mag": {
        "$gte": minMag,
        "$lte": maxMag
    }}, {
        "time": {
            "$gte": str(fromDate.strftime("%Y-%m-%d %H:%M:%S")),
            "$lte": str(toDate.strftime("%Y-%m-%d %H:%M:%S"))
        }}]
    if net:
        query.append({"net": net})
    coll.remove({'$and': query})


def getAllIdsFromDB():
    global inserted_ids
    inserted_ids = []
    for value in Earthquake.query.all():
        inserted_ids.append(value.id)


def getAllIdsFromMongoDB():
    global inserted_ids
    inserted_ids = []
    for value in mongo.db.earthquakes.find():
        inserted_ids.append(value['id'])


# Get the uploaded files
@app.route("/create", methods=['POST'])
def createRecords():
    start = end = 0
    # get the uploaded file
    getAllIdsFromDB()
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], FILE_NAME)
    start = process_time()
    parseCSVToInsert(file_path)
    end = process_time()
    flash("Data inserted successfully in {0} (HH:MM:SS)".format(str(datetime.timedelta(seconds=end - start))),
          'success')
    return redirect(url_for('crud'))


# Get the uploaded files
@app.route("/createMongo", methods=['POST'])
def createMongoRecords():
    start = end = 0
    # get the uploaded file
    getAllIdsFromDB()
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], FILE_NAME)
    start = process_time()
    parseCSVToInsertMongo(file_path)
    end = process_time()
    flash("Data inserted successfully in {0} (HH:MM:SS)".format(str(datetime.timedelta(seconds=end - start))),
          'success')
    return redirect(url_for('crudMongo'))


# Get the uploaded files
@app.route("/delete", methods=['POST'])
def deleteFiles():
    start = end = 0
    if request.args.get('type') == 'random' and request.args.get('server') == 'sql':
        getAllIdsFromDB()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], FILE_NAME)
        start = process_time()
        parseCSVToDelete(file_path)
        end = process_time()
        flash("Data deleted successfully in {0} (HH:MM:SS)".format(str(datetime.timedelta(seconds=end - start))),
              'success')
    elif request.args.get('type') == 'filter' and request.args.get('server') == 'sql':
        minMag = getMinMagParam()
        maxMag = getMaxMagParam()
        fromDate = getFromDateParam()
        toDate = getToDateParam()
        lat = getLatParam()
        lon = getLonParam()
        dist = getDistParam()
        night = getNightParam()
        net = getNetParam()
        start = process_time()
        deleteAllData(minMag, maxMag, fromDate, toDate, lat, lon, dist, night, net)
        end = process_time()
        flash("Data deleted based on filter successfully in {0} (HH:MM:SS)".format(
            str(datetime.timedelta(seconds=end - start))),
            'success')
    return redirect(url_for('crud'))


# Get the uploaded files
@app.route("/deleteMongo", methods=['POST'])
def deleteMongoFiles():
    start = end = 0
    if request.args.get('type') == 'random' and request.args.get('server') == 'sql':
        getAllIdsFromMongoDB()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], FILE_NAME)
        start = process_time()
        parseCSVToDeleteMongo(file_path)
        end = process_time()
        flash("Data deleted successfully in {0} (HH:MM:SS)".format(str(datetime.timedelta(seconds=end - start))),
              'success')
    elif request.args.get('type') == 'filter' and request.args.get('server') == 'sql':
        minMag = getMinMagParam()
        maxMag = getMaxMagParam()
        fromDate = getFromDateParam()
        toDate = getToDateParam()
        net = getNetParam()
        start = process_time()
        deleteAllDataMongo(minMag, maxMag, fromDate, toDate, net)
        end = process_time()
        flash("Data deleted based on filter successfully in {0} (HH:MM:SS)".format(
            str(datetime.timedelta(seconds=end - start))),
            'success')
    return redirect(url_for('crudMongo'))


# Get the uploaded files
@app.route("/init", methods=['POST'])
def initializeDatabase():
    start = end = 0
    if request.args.get('type') == 'random' and request.args.get('server') == 'sql':
        start = process_time()
        if sqlalchemy.inspect(engine).has_table(Earthquake.__table__):
            Earthquake.__table__.drop(engine)
        db.create_all()
        end = process_time()
        flash(
            "Database initialized successfully in {0} (HH:MM:SS)".format(str(datetime.timedelta(seconds=end - start))),
            'success')
    return redirect(url_for('crud'))


# Get the uploaded files
@app.route("/initMongo", methods=['POST'])
def initializeMongoDatabase():
    global coll
    start = end = 0
    if request.args.get('type') == 'random' and request.args.get('server') == 'sql':
        start = process_time()
        mongoDb.drop_collection(coll)
        mongoDb.create_collection(tableName)
        coll = mongoDb[tableName]
        end = process_time()
        flash(
            "Database initialized successfully in {0} (HH:MM:SS)".format(str(datetime.timedelta(seconds=end - start))),
            'success')
    return redirect(url_for('crudMongo'))


def parseCSVToInsert(filePath):
    # Use Pandas to parse the CSV file
    allData = pd.read_csv(filePath)
    csvData = allData[~allData['id'].isin(inserted_ids)].sample(
        n=RECORDS_TO_INSERT_OR_DELETE) if inserted_ids else allData.sample(n=RECORDS_TO_INSERT_OR_DELETE)
    # Loop through the Rows
    csvData['time'] = csvData['time'].apply(
        lambda x: dateutil.parser.parse(x).strftime('%Y-%m-%d %H:%M%:%S'))
    csvData['updated'] = csvData['updated'].apply(
        lambda x: dateutil.parser.parse(x).strftime('%Y-%m-%d %H:%M%:%S'))
    csvData.to_sql(con=engine, index=False, name=Earthquake.__tablename__, if_exists='append', dtype=dataType)


def parseCSVToInsertMongo(filePath):
    # Use Pandas to parse the CSV file
    allData = pd.read_csv(filePath)
    csvData = allData[~allData['id'].isin(inserted_ids)].sample(
        n=RECORDS_TO_INSERT_OR_DELETE) if inserted_ids else allData.sample(n=RECORDS_TO_INSERT_OR_DELETE)

    payload = json.loads(csvData.to_json(orient='records'))
    coll.insert(payload)


def parseCSVToDelete(filePath):
    # Use Pandas to parse the CSV file
    allData = pd.read_csv(filePath)
    numberOfItems = RECORDS_TO_INSERT_OR_DELETE if len(inserted_ids) >= RECORDS_TO_INSERT_OR_DELETE else len(
        inserted_ids)
    csvData = allData[allData['id'].isin(inserted_ids)].sample(
        n=numberOfItems) if inserted_ids else allData.sample(n=numberOfItems)
    try:
        delete_q = Earthquake.__table__.delete().where(Earthquake.id.in_(csvData['id'].values))
        db.session.execute(delete_q)
        db.session.commit()
    except sqlalchemy.exc.ProgrammingError:
        flash('Table not found', 'danger')


def parseCSVToDeleteMongo(filePath):
    numberOfItems = RECORDS_TO_INSERT_OR_DELETE if len(inserted_ids) >= RECORDS_TO_INSERT_OR_DELETE else len(
        inserted_ids)
    idsToDelete = random.sample(inserted_ids, numberOfItems)
    mongo.db.earthquakes.remove({'id': {'$in': idsToDelete}})


if __name__ == '__main__':
    app.run()
