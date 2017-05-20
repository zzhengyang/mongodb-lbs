import hashlib
import datetime
import re

import flask
import pymongo
import bson.binary
import bson.objectid
import bson.errors
from cStringIO import StringIO
from PIL import Image
from flask import render_template, request, redirect
from flask.ext.bootstrap import Bootstrap
# import importDb

app = flask.Flask(__name__)
bootstrap = Bootstrap(app)
app.debug = True
db = pymongo.MongoClient('localhost', 27017).gisdb
# db = pymongo.MongoClient('106.14.177.41', 27017).gisdb
allow_formats = ['jpeg', 'png', 'gif']

def save_file(f):


    content = StringIO(f.read())
    try:
        mime = Image.open(content).format.lower()
        if mime not in allow_formats:
            raise IOError()
    except IOError:
        flask.abort(400)

    sha1 = hashlib.sha1(content.getvalue()).hexdigest()
    c = dict(
        content=bson.binary.Binary(content.getvalue()),
        mime=mime,
        time=datetime.datetime.utcnow(),
        sha1=sha1,
    )
    try:
        db.files.save(c)
    except pymongo.errors.DuplicateKeyError:
        pass
    # return sha1

@app.route('/f')
def serve_file():
    try:
        f = db.xqpoint.find_one({'x': int(request.args.get('x')),'y': int(request.args.get('y')),'zoom': int(request.args.get('z'))})
        if f is None:
            raise bson.errors.InvalidId()
        if flask.request.headers.get('If-Modified-Since') == f['time'].ctime():
            return flask.Response(status=304)
        resp = flask.Response(f['content'], mimetype='image/' + f['mime'])
        resp.headers['Last-Modified'] = f['time'].ctime()
        # return f['content']
        return  '''
    <!doctype html>
    <html>
    <body>
    <h1></h1>
    '''
    except bson.errors.InvalidId:
        flask.abort(404)

@app.route('/<int:city_id>/edit', methods=['GET','POST'])
def edit(city_id):
    if request.method == 'GET':
        return render_template('edit.html', xqpoint=db.xqpoint.find({'CNTYPT_': city_id}))
    else:
        db.xqpoint.update({'CNTYPT_': city_id}, {'$set':{'NAME': request.form['name']}})
        return redirect('/'+city_id+'/edit')
@app.route('/<int:city_id>/delete')
def delete(city_id):
    db.xqpoint.remove({'CNTYPT_': city_id})
    return redirect('/get/page/1')

@app.route('/get/page/<int:page>', methods=['GET'])
def get_all(page):

  return render_template('list.html', xqpoint=db.xqpoint.find().limit(15).skip((page-1)*15),page=page)


@app.route('/search/exact', methods=['POST'])
def get_one_by_coordinates():
    return render_template('detail.html', xqpoint=db.xqpoint.find({'geom.coordinates':
                                                                     [float(request.form['lng']),float(request.form['lat'])]}))

@app.route('/search/near', methods=['POST'])
def get_near_by_coordinates():
    return render_template('detail.html', xqpoint=db.xqpoint.find({'geom.coordinates':
                                                                     {'$near':[float(request.form['lng']),float(request.form['lat'])]
                                                                 }}).limit(int(request.form['number'])))

@app.route('/search/within', methods=['POST'])
def get_within_by_coordinates():
    return render_template('detail.html',xqpoint=db.xqpoint.find({'geom.coordinates':{
                                                                    '$within':{
                                                                        '$center':[[float(request.form['lng']),float(request.form['lat'])],int(request.form['radius'])]
                                                                        }
                                                                    }
                                                                }))

@app.route('/search/name', methods=['POST'])
def get_one_by_name():
    return render_template('detail.html', xqpoint=db.xqpoint.find({'NAME': re.compile(request.form['country'])}))

@app.route('/exat', methods=['GET'])
def exat():
    return render_template('searchExat.html')

@app.route('/near', methods=['GET'])
def near():
    return render_template('searchNear.html')

@app.route('/within', methods=['GET'])
def within():
    return render_template('searchWithin.html')

@app.route('/map/point', methods=['GET'])
def get_map_points():
    list = ''
    a = db.xqpoint.find({'geom':{'type':'Point'}})
    for i in a:
        list += "{name: '" + i['NAME'] + "', coordinates: " + str(i['geom']['coordinates']) + "},"
    return render_template('map.html', data1 = "["+list+"]")

@app.route('/map/polygon', methods=['GET'])
def get_map_polygon():
    list = ''
    a = db.xqpoint.find({'geom':{'type':'Polygen'}})
    for i in a:
        list += "{name: '" + i['NAME'] + "', coordinates: " + str(i['geom']['coordinates']) + "},"
    return render_template('map_polygon.html', data1 = "["+list+"]")


@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(port=7777)