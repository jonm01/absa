from flask import Flask
from flask_restful import Api, Resource, reqparse
import scrap
import mine
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
api = Api(app)

class Crawl(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("pid")
        args = parser.parse_args()
        data=scrap.readp(args['pid'])
        return data, 200

class Analyse(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("pid")
        args = parser.parse_args()
        data=mine.startMine(args['pid'])
        return data, 200

api.add_resource(Crawl, "/scrap")
api.add_resource(Analyse, "/analyse")
app.run(debug=False)
