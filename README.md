# Leaf Logic AI - Tea Processing AI Monitor

Real-time monitoring and control system for tea processing operations. This web-based dashboard provides comprehensive visualization and management tools for the entire tea production process.

## Features

- **Real-time Monitoring**: Track all six stages of tea processing (withering, rolling, fermentation, drying, sorting, packing)
- **Machine Control**: Interactive interface for controlling tea processing machines
- **Alerts and Notifications**: Fault detection and maintenance scheduling
- **User Authentication**: Secure access control with login system
- **Responsive Design**: Works on desktop and mobile devices
- **Technical Specifications**: Detailed information for each machine type
- **Modern UI/UX**: Dark-themed interface with data visualizations

## Installation

1. Clone this repository:
```
git clone https://github.com/gowrish005/Leaf-Logic.AI.git
cd tea-processing-ai-monitor
```

2. Create and activate a virtual environment:
```
python -m venv venv
```

On Windows:
```
venv\Scripts\activate
```

On macOS/Linux:
```
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example` with your database credentials:
```
cp .env.example .env
```

Then edit the `.env` file with your MongoDB connection string and other settings.

## Configuration

The application can be configured using environment variables or a `.env` file:

- `MONGO_URI`: MongoDB connection string (required)
- `SECRET_KEY`: Secret key for session encryption
- `DEBUG`: Enable debug mode (default: False)
- `TESTING`: Enable testing mode (default: False)
- `SKIP_DB_INIT`: Skip database initialization on startup (default: False)
- `PORT`: Port to run the application on (default: 5000)

## Running the Application

For development:
```
python app.py
```

For production (using gunicorn):
```
gunicorn app:app
```

Access the application at http://localhost:5000

## Deployment

This application can be deployed to any platform that supports Python web applications.

### Deploying to Render

1. Create a new Web Service in Render
2. Link your repository
3. Set the build command to `pip install -r requirements.txt`
4. Set the start command to `gunicorn app:app`
5. Add the required environment variables:
   - `MONGO_URI`: Your MongoDB connection string
   - `SECRET_KEY`: A secure random string
   - `SKIP_DB_INIT`: Set to `True`

## Application Structure

- `app.py`: Main application entry point
- `config.py`: Configuration settings
- `models.py`: Data models and database operations
- `controllers.py`: Business logic and request handling
- `routes.py`: URL routing definitions
- `views.py`: Template rendering
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, images and other assets

## Technologies Used

- **Backend**: Flask, PyMongo, MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Libraries**: Bootstrap 5, Chart.js, Font Awesome, ScrollReveal.js
- **Authentication**: Werkzeug security for password hashing
- **Database**: MongoDB
