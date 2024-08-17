import asyncio
import datetime
import os

import aiohttp
from dotenv import load_dotenv
from flask import Flask, request, Blueprint
from flask_restx import Api, Namespace, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)

# In-memory store to keep track of the requests
requests_store = {}
app.wsgi_app = ProxyFix(app.wsgi_app)

# Register blueprint
blueprint = Blueprint('api', __name__)
app.register_blueprint(blueprint)

api = Api(app, title='Open Weather API', version='1.0', description='API for collecting weather data')

# Define the weather namespace
weather_ns = Namespace('weather', description='Weather related operations')

# Define models for request and response data
weather_request_model = weather_ns.model('WeatherRequest', {
    'user_id': fields.String(required=True, description='The ID of the user making the request'),
    'city_ids': fields.List(fields.Integer, required=True, description='List of city IDs to collect weather data for')
})

weather_progress_model = weather_ns.model('WeatherProgress', {
    'user_id': fields.String(description='The ID of the user'),
    'progress': fields.Float(description='Progress of weather data collection'),
    'weather_data': fields.List(fields.Nested(weather_ns.model('CityWeather', {
        'city_id': fields.Integer(description='City ID'),
        'temperature': fields.Float(description='Temperature in Celsius'),
        'humidity': fields.Float(description='Humidity percentage'),
    })))
})

# Load OpenWeather API token from environment variables
OPENWEATHER_API_TOKEN = os.getenv('OPENWEATHER_API_TOKEN')


@weather_ns.route('/')
class WeatherCollection(Resource):
    @weather_ns.expect(weather_request_model)
    @weather_ns.response(202, 'Weather data collection started')
    @weather_ns.response(400, 'Bad Request')
    def post(self):
        """
        Collect weather data for specified cities and user.
        """
        data = request.json
        user_id = data.get('user_id')
        city_ids = data.get('city_ids')

        if not user_id or not city_ids:
            return {"error": "user_id and city_ids are required"}, 400

        if user_id in requests_store:
            return {"error": "user_id must be unique"}, 400

        requests_store[user_id] = {
            'datetime': datetime.datetime.now().isoformat(),
            'progress': 0,
            'total_cities': len(city_ids),
            'completed_cities': 0,
            'weather_data': []
        }

        # Run the async function in an event loop
        asyncio.run(fetch_weather_for_cities(user_id, city_ids))

        return {"message": "Weather data collection started", "user_id": user_id}, 202


@weather_ns.route('/<string:user_id>')
@weather_ns.response(404, 'User ID not found')
class WeatherProgress(Resource):
    @weather_ns.response(200, 'Weather data collection progress', model=weather_progress_model)
    def get(self, user_id):
        """
        Get the progress of weather data collection for a user.
        """
        if user_id not in requests_store:
            return {"error": "Invalid user_id"}, 404
        return {
            "user_id": user_id,
            "datetime": requests_store[user_id]['datetime'],
            "progress": requests_store[user_id]['progress'],
            "weather_data": requests_store[user_id]['weather_data']
        }, 200


# Register the weather namespace
api.add_namespace(weather_ns, path='/weather')


async def fetch_weather_for_cities(user_id: str, city_ids: list):
    """
    Fetches weather data for the given list of city IDs using the OpenWeather API.
    """
    headers = {
        'Content-Type': 'application/json',
    }

    async with aiohttp.ClientSession() as session:
        for city_id in city_ids:
            if requests_store[user_id]['completed_cities'] < requests_store[user_id]['total_cities']:
                url = (f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&"
                       f"appid={OPENWEATHER_API_TOKEN}&units=metric")
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        weather_data = await response.json()
                        requests_store[user_id]['weather_data'].append({
                            'city_id': city_id,
                            'temperature': weather_data['main']['temp'],
                            'humidity': weather_data['main']['humidity'],
                        })
                        requests_store[user_id]['completed_cities'] += 1
                        requests_store[user_id]['progress'] = (requests_store[user_id]['completed_cities'] /
                                                               requests_store[user_id]['total_cities']) * 100
                await asyncio.sleep(1)  # To respect the rate limit (60 cities per minute)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
