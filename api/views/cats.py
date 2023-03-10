from flask import Blueprint, jsonify, request
from api.middleware import login_required, read_token

from api.models.db import db
from api.models.cat import Cat
from api.models.feeding import Feeding
from api.models.toy import Toy
from api.models.toy import Association

cats = Blueprint('cats', 'cats')

@cats.route('/', methods=["POST"])
@login_required
def create():
  data = request.get_json()
  profile = read_token(request)
  data["profile_id"] = profile["id"]
  cat = Cat(**data)
  db.session.add(cat)
  db.session.commit()
  return jsonify(cat.serialize()), 201

@cats.route('/', methods=["GET"])
def index():
  cats = Cat.query.all()
  return jsonify([cat.serialize() for cat in cats]), 200

@cats.route('/<id>', methods=["GET"])
def show(id):
  cat = Cat.query.filter_by(id=id).first()
  cat_data = cat.serialize()
  cat_data["fed"] = cat.fed_for_today()

  # Add the following:
  toys = Toy.query.filter(Toy.id.notin_([toy.id for toy in cat.toys])).all()
  toys=[toy.serialize() for toy in toys]

  return jsonify(cat=cat_data, available_toys=toys), 200 # <=== Include toys in response

@cats.route('/<id>', methods=["PUT"]) 
@login_required
def update(id):
  data = request.get_json()
  profile = read_token(request)
  cat = Cat.query.filter_by(id=id).first()

  if cat.profile_id != profile["id"]:
    return 'Forbidden', 403

  for key in data:
    setattr(cat, key, data[key])

  db.session.commit()
  return jsonify(cat.serialize()), 200

@cats.route('/<id>', methods=["DELETE"])
@login_required
def delete(id):
  profile = read_token(request)
  cat = Cat.query.filter_by(id=id).first()

  if cat.profile_id != profile["id"]:
    return 'Forbidden', 403

  db.session.delete(cat)
  db.session.commit()
  return jsonify(message="Success"), 200

@cats.route('/<id>/feedings', methods=["POST"])
@login_required
def add_feeding(id):
  data = request.get_json()
  data["cat_id"] = id

  profile = read_token(request)
  cat = Cat.query.filter_by(id=id).first()

  if cat.profile_id != profile["id"]:
    return 'Forbidden', 403

  feeding = Feeding(**data)

  db.session.add(feeding)
  db.session.commit()

  cat_data = cat.serialize()
  cat_data["fed"] = cat.fed_for_today()

  return jsonify(cat_data), 201

@cats.route('/<cat_id>/toys/<toy_id>', methods=["LINK"])
@login_required
def assoc_toy(cat_id, toy_id):
  data = { "cat_id": cat_id, "toy_id": toy_id}

  profile = read_token(request)
  cat = Cat.query.filter_by(id=cat_id).first()

  if cat.profile_id != profile["id"]:
    return 'Forbidden', 403

  assoc = Association(**data)
  db.session.add(assoc)
  db.session.commit()

  cat = Cat.query.filter_by(id=cat_id).first()
  return jsonify(cat.serialize()), 201

@cats.errorhandler(Exception)          
def basic_error(err):
  return jsonify(err=str(err)), 500