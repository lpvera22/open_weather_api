from unittest.mock import patch, AsyncMock

import pytest

from app import app, requests_store, fetch_weather_for_cities, WeatherCollection


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('app.aiohttp.ClientSession.get')
def test_weather_collection_start(mock_get, client):
    """
    Asserts that the response status code is 202, and that the user is added to the requests_store with the correct
    information.
    """
    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value={
        'main': {
            'temp': 20.0,
            'humidity': 60
        }
    })

    payload = {
        "user_id": "test_user",
        "city_ids": [12345, 67890]
    }

    # Directly call the post-method from the view
    with app.test_request_context('/weather/', method='POST', json=payload):
        view = WeatherCollection()
        response = view.post()

    assert response[1] == 202
    assert 'test_user' in requests_store
    assert requests_store['test_user']['total_cities'] == 2
    assert requests_store['test_user']['progress'] == 100


def test_weather_collection_start_bad_request(client):
    """
    Tests the behavior of the weather_collection_start endpoint when a bad request is made. It verifies that
    the response code is 400.
    """
    payload = {
        "city_ids": [12345, 67890]
    }

    with app.test_request_context('/weather/', method='POST', json=payload):
        view = WeatherCollection()
        response = view.post()

    assert response[1] == 400


def test_weather_progress(client):
    """
    Test the progress of weather data retrieval.
    """
    requests_store['test_user'] = {
        'datetime': '2024-08-17T12:00:00',
        'progress': 50,
        'total_cities': 2,
        'completed_cities': 1,
        'weather_data': [
            {'city_id': 12345, 'temperature': 20.0, 'humidity': 60}
        ]
    }

    response = client.get('/weather/test_user')
    assert response.status_code == 200
    assert response.json['progress'] == 50
    assert len(response.json['weather_data']) == 1


def test_weather_progress_user_not_found(client):
    """
    Tests the behavior of the weather progress API when an unknown user is requested.
    """
    response = client.get('/weather/unknown_user')
    assert response.status_code == 404


@patch('app.aiohttp.ClientSession.get')
@pytest.mark.asyncio
async def test_fetch_weather_for_cities(mock_get):
    """
    Tests the fetch weather information for multiple cities.
    """
    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value={
        'main': {
            'temp': 20.0,
            'humidity': 60
        }
    })

    requests_store['test_user'] = {
        'datetime': '2024-08-17T12:00:00',
        'progress': 0,
        'total_cities': 2,
        'completed_cities': 0,
        'weather_data': []
    }

    await fetch_weather_for_cities('test_user', [12345, 67890])

    assert requests_store['test_user']['progress'] == 100
    assert len(requests_store['test_user']['weather_data']) == 2
    assert requests_store['test_user']['weather_data'][0]['city_id'] == 12345
