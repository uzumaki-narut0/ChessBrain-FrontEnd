from flask import Flask
from flask_restful import Resource, Api
import os

app = Flask(__name__)
CORS(app)
api = Api(app)

class ChessBrain(Resource):
    def get(self):
        return {'fen_layout': 'start'}

api.add_resource(ChessBrain, '/')

port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)