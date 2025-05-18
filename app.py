from flask import Flask
from routes import register_routes
from models import init_db, clean_database, initialize_models, generate_readings
from controllers import get_process_data
import threading
import time
import os
from pymongo import MongoClient
from config import Config

app = Flask(__name__, 
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

# Load configuration from Config class
app.config.from_object(Config)

# Toggle this to enable/disable test/console output
app.testing = Config.TESTING

# Initialize database
init_db(app)

# Background data generation thread
def background_data_generation():
    """Generate data in the background every 30 seconds"""
    with app.app_context():
        while True:
            try:
                # Create a fresh connection each time to avoid connection timeout issues
                mongo_client = MongoClient(app.config['MONGO_URI'])
                db = mongo_client.get_database()
                
                # Make db available to the generate_readings function
                from flask import g
                g.db = db
                
                # Generate new readings
                generate_readings()
                
                # Close the connection after use
                mongo_client.close()
            except Exception as e:
                if getattr(app, 'testing', True):
                    print(f"Error in background data generation: {e}")
            
            # Sleep for 30 seconds before next cycle
            time.sleep(30)

# Add context processor to make processes data available to all templates
@app.context_processor
def inject_processes():
    """Make processes data available to all templates"""    
    try:
        # Create a dedicated MongoDB connection for this context processor
        mongo_client = MongoClient(app.config['MONGO_URI'])
        db = mongo_client.get_database()
        
        # Make db available to the get_process_data function
        from flask import g
        g.db = db
        
        # Get the process data
        try:
            processes = get_process_data()
            # Close the connection after use
            mongo_client.close()
            return {'processes': processes}
        except Exception as e:
            if getattr(app, 'testing', True):
                print(f"Error getting process data in context processor: {e}")
                import traceback
                traceback.print_exc()
            # Close the connection if error
            mongo_client.close()
            return {'processes': []}
    except Exception as e:
        # In case of error, return an empty list to prevent the app from crashing
        if getattr(app, 'testing', True):
            print(f"Error in inject_processes context processor: {e}")
            import traceback
            traceback.print_exc()
        return {'processes': []}

# Register routes
register_routes(app)

if __name__ == '__main__':
    # Clean and initialize database on startup if not skipped
    if not app.config.get('SKIP_DB_INIT', False):
        with app.app_context():
            try:
                # Create a direct database connection for startup operations
                mongo_client = MongoClient(app.config['MONGO_URI'])
                db = mongo_client.get_database()
                
                # Make db available to the clean_database and other functions
                from flask import g
                g.db = db
                
                clean_database()
                initialize_models()
                generate_readings()  # Generate initial readings
                
                # Close the startup connection
                mongo_client.close()
                print("Database initialized successfully")
            except Exception as e:
                print(f"Error initializing database: {e}")
                print("Continuing without database initialization.")
      # Start background data generation
    bg_thread = threading.Thread(target=background_data_generation)
    bg_thread.daemon = True  # Thread will exit when main thread exits
    bg_thread.start()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])