import json
from models import SensorData
from flask import Flask, request
from flask.helpers import make_response
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, utils
from flask import Flask, render_template, session, g, redirect
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from models import db, Role, User
import os
from werkzeug.serving import WSGIRequestHandler
basedir = os.path.abspath(os.path.dirname(__file__, ))

app = Flask(__name__, template_folder="./templates")
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = basedir
# just to not have the runtime complain about it. tells us its not a production grade software, but we know this.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# sqlite is probably not the best database to use, but this is not for production(so far at least)!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'Database.db')
print(basedir)
# secrets.token_urlsafe().encode()
app.config['SECRET_KEY'] = b'7hW0ekQpq5CIgf9h4X7n82OLkiLttPPIbB1gTPmCiT_1r7naBHWCf_xctAW4wOhGe4tEhY9w_ZBqZJn8OdnMHsCvW_JbzBaMXg4wB6R2PyFjcIhFg87kuUFoIbkK3fv01F5JLN07eF57ib-khEYUFvr2KGYpKBUX5ew5r6HXOrw'
# str(secrets.SystemRandom().getrandbits(246)).encode()
app.config['SECURITY_PASSWORD_SALT'] = b'56233859612521323627298837306511598084560641616274247380468871052333874302'

db.init_app(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def create_user():
    db.create_all()
    if not user_datastore.get_user("email2@m.com"):
        user = User(email="email2@m.com",
                    password="passord", active=True)
        db.session.add(user)
    db.session.commit()


@app.before_request
def before_request():
    g.user = current_user


@app.route("/")
def hello():
    resp = make_response(render_template("index.html"))
    return resp


@app.route("/sensors")
def sensors():
    return render_template("sensors.html")


@app.route("/sensors/add", methods=["POST", "GET"])
def add_sensordata():
    resp = make_response(request.json)
    data = request.json
    if data:
        db.session.add(SensorData(humidity=data["humidity"], temperature=data["temperature"],
                                  pm25=data["pm25"], pm10=data["pm10"], northing="", easting=""))
        db.session.commit()

    q = SensorData.query.order_by(SensorData.id).all()
    for item in q:
        print(item.temperature, item.humidity)
    return resp


@app.route("/sensors/all")
def get_sensordata():
    from flask import jsonify
    q = SensorData.query.order_by(SensorData.id).all()
    data = {}
    for item in q:
        data[item.id] = {"temperature": item.temperature, "humidity": item.humidity, "pm10": item.pm10,
                         "pm25": item.pm25, "northing": item.northing, "easting": item.easting}

    return jsonify(data=data)


if __name__ == "__main__":
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(port=8080)
