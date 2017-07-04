from flask import Flask, send_from_directory, jsonify, request, current_app
import pymongo
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import BadRequest, NotFound
import flask.json
import decimal
from bson.decimal128 import Decimal128
from bson.objectid import ObjectId


from pymongo import MongoClient
from functools import wraps


app = Flask(__name__)
app.jinja_env.globals['scripts'] = ()

client = MongoClient()


class MyJSONEncoder(flask.json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (decimal.Decimal, ObjectId, Decimal128)):
            return str(obj)
        return super(MyJSONEncoder, self).default(obj)


app.json_encoder = MyJSONEncoder


def decorate(decorator):
	@wraps(decorator)
	def wrapper(f):
		@wraps(f)
		def wrapper(*args, **kwargs):
			return decorator(f, *args, **kwargs)
		return wrapper
	return wrapper


def identifier(n):
	if not n.isidentifier():
		raise BadRequest('Not a valid database name: %r' % n)
	return n


def must_find_one(db, collection_name, *args, **kwargs):
	found = db[identifier(collection_name)].find_one(*args, **kwargs)
	if not found:
		raise NotFound({'db': db, 'collection_name': collection_name, 'filter': (args, kwargs)})
	return found


def from_json(cls):
	def decorator(f):
		@wraps(f)
		def wrapper(*args, **kwargs):
			return f(None if request.json is None else cls(**request.json), *args, **kwargs)
		return wrapper
	return decorator


def mongodb(f, db_name, *args, **kwargs):
	return f(client[identifier(db_name)], *args, **kwargs)


@app.route('/<x>.jsx', methods=['GET'])
def jsx(x):
	return send_from_directory('static', '%s.jsx' % x)

@app.route('/<x>.js', methods=['GET'])
def js(x):
	return send_from_directory('static', '%s.js' % x)


@app.route('/exchanges/<db_name>/', methods=['GET'])
@decorate(mongodb)
def get_exchange(db):
	return current_app.jinja_env.render('index.html', scripts=('common.jsx', 'index.jsx'))

@app.route('/exchanges/<db_name>/<n>.html', methods=['GET'])
@decorate(mongodb)
def get_exchange_html(db, n, template=app.jinja_env.get_template('index.html'), mapping={
		'manage': ('common.jsx', 'manage.jsx'),
	}):
	return template.render(scripts=mapping.get(n, ()))


def stock(f, db, stock_name, *args, **kwargs):
	return f(db, must_find_one(db, 'stocks', {'name': identifier(stock_name)}), *args, **kwargs)


def list_collection_deco(collection_name):
	def deco(f, db, *args, **kwargs):
		return f(db, list(db[identifier(collection_name)].find({})), *args, **kwargs)
	return deco
		
@app.route('/exchanges/<db_name>/stocks', methods=['GET'])
@decorate(mongodb)
@decorate(list_collection_deco('stocks'))
def list_objects(db, collection):
	return jsonify(collection)

@app.route('/exchanges/<db_name>/stock/<stock_name>', methods=['GET'])
@decorate(mongodb)
@decorate(stock)
def get_stock(db, stock):
	return jsonify(dict(stock))


class Stock(object):
	def __init__(self, name, initpx, tick):
		self.name = name
		import decimal
		self.px = decimal.Decimal(initpx)
		self.tick = decimal.Decimal(tick)


@app.route('/exchanges/<db_name>/stock/<stock_name>', methods=['POST'])
@decorate(mongodb)
@from_json(Stock)
def new_stock(new_stock, db, stock_name):
	if stock_name != new_stock.name:
		raise BadRequest('%r != %r' % (stock_name, new_stock.name))
	db['stocks'].create_index([('name', pymongo.ASCENDING)], unique=True)
	o = {'name': identifier(new_stock.name), 'px': Decimal128(new_stock.px), 'tick': Decimal128(new_stock.tick)}
	ins_result = db['stocks'].insert_one(o)
	o['_id'] = ins_result.inserted_id
	return jsonify(o)
		

@app.route('/exchanges/<db_name>/stock/<stock_name>', methods=['PUT'])
@decorate(mongodb)
@decorate(stock)
@from_json(Stock)
def update_stock(updated_stock, db, stock):
	db['stocks'].update_one({'_id': stock['_id']}, {'$set': {'px': Decimal128(updated_stock.px), 'tick': Decimal128(updated_stock.tick)}})
	return jsonify(dict(stock))



@app.route('/exchanges/<db_name>/stock/<stock_name>', methods=['DELETE'])
@decorate(mongodb)
@decorate(stock)
def delete_stock(db, stock):
	db['stocks'].delete_one({'_id': stock['_id']})
	return jsonify(dict(stock))




