# Open Weather API

This project is a Flask-based RESTful API for collecting and tracking weather data from the OpenWeather API. It allows
users to submit a list of city IDs, and then retrieves and tracks the weather data collection process asynchronously.

## Features

- **Weather Data Collection**: Submit city IDs and get weather data including temperature and humidity.
- **Progress Tracking**: Track the progress of the weather data collection in real-time.
- **Asynchronous Processing**: Utilizes `asyncio` and `aiohttp` for non-blocking, asynchronous API requests.
- **RESTful Design**: Built with Flask-RESTx, providing clear API namespaces, routes, and response models.

## Installation

### Prerequisites

- Python 3.8 or later
- `pip` (Python package manager)
- [OpenWeather API Key](https://openweathermap.org/api) (free to obtain after signing up)

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/open-weather-api.git
    cd open-weather-api
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project root and add your OpenWeather API token:

    ```plaintext
    OPENWEATHER_API_TOKEN=your_openweather_api_key
    ```

5. Run the application:

    ```bash
    python app.py
    ```

   The API will be available at `http://0.0.0.0:5000/`.

## Using Docker

This project includes a `Dockerfile`, which simplifies building and running the application in a Docker container.

### Building the Docker Image

To build the Docker image, run the following command in the project root directory:

```bash
docker build -t open-weather-api .
```

### Running the Docker Container

After building the image, you can run the container with:

```bash
docker run -d -p 5000:5000 --env-file .env open-weather-api

```

## Usage

### API Endpoints

#### 1. Start Weather Data Collection

- **Endpoint**: `/weather/`
- **Method**: `POST`
- **Description**: Initiates weather data collection for a specified user and list of city IDs.

- **Request Body**:
    ```json
    {
        "user_id": "string",
        "city_ids": [123456, 654321]
    }
    ```

- **Responses**:
    - `202 Accepted`: Weather data collection started.
    - `400 Bad Request`: Invalid input or user ID already exists.

#### 2. Check Weather Data Collection Progress

- **Endpoint**: `/weather/{user_id}`
- **Method**: `GET`
- **Description**: Returns the progress and collected weather data for the specified user.

- **Response Example**:
    ```json
    {
        "user_id": "string",
        "datetime": "2024-08-17T12:34:56.789123",
        "progress": 50.0,
        "weather_data": [
            {
                "city_id": 123456,
                "temperature": 25.3,
                "humidity": 78
            }
        ]
    }
    ```

- **Responses**:
    - `200 OK`: Returns progress and weather data.
    - `404 Not Found`: Invalid user ID.

## Environment Variables

- `OPENWEATHER_API_TOKEN`: Your API token from OpenWeather. Required for the API to function.

## Running Tests

### Prerequisites

- Ensure that all dependencies are installed by following the installation steps above.
- Tests are written using the `pytest` framework.

### Running Tests Locally

To run the tests locally, use the following command:
```pytest```

## Contributing

Contributions are welcome! Please fork this repository, create a new branch, and submit a pull request.

## License

This project is licensed under the MIT License.
