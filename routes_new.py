"""
Routes module for Tea Processing Monitor application
Defines all application routes and API endpoints
"""

from flask import render_template, jsonify, request, g
from pymongo import MongoClient
from views_new import dashboard_view, machine_view
from controllers import get_process_data, get_machine_data, update_machine_status
import datetime
import traceback

def register_routes(app):
    """Register all application routes"""
    
    # Web UI routes
    @app.route('/')
    def index():
        """Main dashboard page"""
        return dashboard_view()
    
    @app.route('/machine/<process_name>/<machine_id>')
    def machine_detail(process_name, machine_id):
        """Machine detail view"""
        return machine_view(process_name, machine_id)
        
    @app.route('/simple')
    def simple_dashboard():
        """Simplified dashboard page without custom CSS"""
        print("Loading simple dashboard with minimal CSS")
        try:
            # Create a dedicated MongoDB connection for this view
            mongo_client = MongoClient(app.config['MONGO_URI'])
            db = mongo_client.get_database()
            
            # Make db available to the controller functions
            g.db = db
            
            try:
                # Get data for all processes and machines
                processes_data = get_process_data()
                
                # Calculate overview counts
                running = 0
                idle = 0
                maintenance = 0
                fault = 0
                
                # Loop through processes and machines to count status
                for process in processes_data:
                    for machine in process.get('machines', []):
                        status = machine.get('status', '').lower()
                        if status == 'running': running += 1
                        elif status == 'idle': idle += 1
                        elif status == 'maintenance': maintenance += 1
                        elif status in ['fault', 'error']: fault += 1
                
                overview_data = {
                    'running': running,
                    'idle': idle,
                    'maintenance': maintenance,
                    'fault': fault
                }
                
                return render_template(
                    'dashboard_simple.html',
                    title='Simple Dashboard - Tea Processing Monitor',
                    processes=processes_data,
                    overview=overview_data
                )
            
            except Exception as e:
                print(f"Error in simple_dashboard: {e}")
                traceback.print_exc()
                return render_template(
                    'dashboard_simple.html',
                    title='Error - Tea Processing Monitor',
                    processes=[],
                    overview={'running': 0, 'idle': 0, 'maintenance': 0, 'fault': 0},
                    error_message=f"Failed to load dashboard data: {str(e)}"
                )
            
            finally:
                mongo_client.close()
                print("MongoDB connection closed in simple_dashboard view")
        
        except Exception as e:
            print(f"Error connecting to MongoDB in simple_dashboard: {e}")
            traceback.print_exc()
            return render_template(
                'dashboard_simple.html',
                title='Database Error - Tea Processing Monitor',
                processes=[],
                overview={'running': 0, 'idle': 0, 'maintenance': 0, 'fault': 0},
                error_message="Failed to connect to database"
            )
    
    # API routes
    @app.route('/api/process-data', methods=['GET'])
    def process_data():
        """Get data for all processes"""
        print("API endpoint /api/process-data called")
        try:
            # Create a dedicated connection for this API call
            mongo_client = MongoClient(app.config['MONGO_URI'])
            db = mongo_client.get_database()
            print("MongoDB connection established for /api/process-data")
            
            # Make db available to the get_process_data function
            g.db = db
            
            try:
                # Get process data
                data = get_process_data()
                print(f"API returned data: {type(data)} with {len(data) if isinstance(data, list) else 'ERROR'} items")
                return jsonify(data)
            except Exception as e:
                print(f"Error in process_data API when getting data: {e}")
                traceback.print_exc()
                return jsonify({"error": str(e)}), 500
            finally:
                # Always close the connection
                mongo_client.close()
                print("MongoDB connection closed for /api/process-data")
        except Exception as e:
            print(f"Error in process_data API when connecting to MongoDB: {e}")
            traceback.print_exc()
            return jsonify({"error": f"MongoDB connection error: {str(e)}"}), 500
    
    @app.route('/api/process/<process_name>', methods=['GET'])
    def process_detail(process_name):
        """Get data for a specific process"""
        print(f"API endpoint /api/process/{process_name} called")
        try:
            # Create a dedicated connection for this API call
            mongo_client = MongoClient(app.config['MONGO_URI'])
            db = mongo_client.get_database()
            
            # Make db available to the get_process_data function
            g.db = db
            
            try:
                data = get_process_data(process_name)
                return jsonify(data)
            except Exception as e:
                print(f"Error in process_detail API: {e}")
                traceback.print_exc()
                return jsonify({"error": str(e)}), 500
            finally:
                # Always close the connection
                mongo_client.close()
                print(f"MongoDB connection closed for /api/process/{process_name}")
        except Exception as e:
            print(f"Error in process_detail API when connecting to MongoDB: {e}")
            traceback.print_exc()
            return jsonify({"error": f"MongoDB connection error: {str(e)}"}), 500
    
    # Machine status endpoint
    @app.route('/api/machine/<machine_id>/status', methods=['GET'])
    def machine_status(machine_id):
        """Get status and data for a specific machine"""
        print(f"API endpoint /api/machine/{machine_id}/status called")
        try:
            # Create a dedicated connection for this API call
            mongo_client = MongoClient(app.config['MONGO_URI'])
            db = mongo_client.get_database()
            
            # Make db available to the get_machine_data function
            g.db = db
            
            try:
                data = get_machine_data(machine_id)
                return jsonify(data)
            except Exception as e:
                print(f"Error in machine_status API: {e}")
                traceback.print_exc()
                return jsonify({"error": str(e)}), 500
            finally:
                # Always close the connection
                mongo_client.close()
                print(f"MongoDB connection closed for /api/machine/{machine_id}/status")
        except Exception as e:
            print(f"Error in machine_status API when connecting to MongoDB: {e}")
            traceback.print_exc()
            return jsonify({"error": f"MongoDB connection error: {str(e)}"}), 500
    
    # Machine readings endpoint with time range filter
    @app.route('/api/machine/<machine_id>/readings', methods=['GET'])
    def machine_readings(machine_id):
        """Get readings for a specific machine with optional time range"""
        print(f"API endpoint /api/machine/{machine_id}/readings called")
        # Get time range from query parameters
        time_range = request.args.get('range', '24h')  # Default to 24 hours
        
        try:
            # Create a dedicated connection for this API call
            mongo_client = MongoClient(app.config['MONGO_URI'])
            db = mongo_client.get_database()
            
            # Make db available to the get_machine_data function
            g.db = db
            
            try:
                # Get machine data
                machine_data = get_machine_data(machine_id)
                
                # Filter readings based on time range
                if 'readings' in machine_data:
                    current_time = datetime.datetime.utcnow()
                    
                    # Calculate time delta based on range parameter
                    if time_range == '1h':
                        delta = datetime.timedelta(hours=1)
                    elif time_range == '6h':
                        delta = datetime.timedelta(hours=6)
                    else:  # Default to 24h
                        delta = datetime.timedelta(hours=24)
                    
                    # Filter readings
                    cutoff_time = current_time - delta
                    filtered_readings = [
                        r for r in machine_data['readings'] 
                        if datetime.datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) > cutoff_time
                    ]
                    
                    machine_data['readings'] = filtered_readings
                
                return jsonify(machine_data)
            except Exception as e:
                print(f"Error in machine_readings API: {e}")
                traceback.print_exc()
                return jsonify({"error": str(e)}), 500
            finally:
                # Always close the connection
                mongo_client.close()
                print(f"MongoDB connection closed for /api/machine/{machine_id}/readings")
        except Exception as e:
            print(f"Error in machine_readings API when connecting to MongoDB: {e}")
            traceback.print_exc()
            return jsonify({"error": f"MongoDB connection error: {str(e)}"}), 500
    
    # Machine control endpoint
    @app.route('/api/machine/<machine_id>/control', methods=['POST'])
    def machine_control(machine_id):
        """Control a machine (start, stop, maintenance, etc.)"""
        print(f"API endpoint /api/machine/{machine_id}/control called")
        if not request.json or 'action' not in request.json:
            return jsonify({'success': False, 'error': 'Invalid request'}), 400
        
        action = request.json['action']
        timestamp = datetime.datetime.utcnow().isoformat()
        
        # Map actions to statuses
        status_map = {
            'start': 'running',
            'pause': 'idle',
            'maintenance': 'maintenance',
            'emergency-stop': 'error'
        }
        
        # Validate action
        if action not in status_map:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        try:
            # Create a dedicated connection for this API call
            mongo_client = MongoClient(app.config['MONGO_URI'])
            db = mongo_client.get_database()
            
            # Make db available to the update_machine_status function
            g.db = db
            
            try:
                # Update machine status
                result = update_machine_status(machine_id, {
                    'status': status_map[action],
                    'timestamp': timestamp
                })
                
                return jsonify(result)
            except Exception as e:
                print(f"Error in machine_control API: {e}")
                traceback.print_exc()
                return jsonify({"error": str(e), "success": False}), 500
            finally:
                # Always close the connection
                mongo_client.close()
                print(f"MongoDB connection closed for /api/machine/{machine_id}/control")
        except Exception as e:
            print(f"Error in machine_control API when connecting to MongoDB: {e}")
            traceback.print_exc()
            return jsonify({"error": f"MongoDB connection error: {str(e)}", "success": False}), 500
