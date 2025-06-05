from flask import render_template, jsonify, request, redirect, url_for, flash
from views import dashboard_view, machine_view
from controllers import get_process_data, get_machine_data, update_machine_status, register_user, authenticate_user, logout_user, login_required
import datetime

def register_routes(app):
    """Register all application routes"""
    
    # Web UI routes
    @app.route('/')
    @login_required
    def index():
        """Main dashboard page"""
        return dashboard_view()
    
    @app.route('/machine/<process_name>/<machine_id>')
    def machine_detail(process_name, machine_id):
        """Machine detail view"""
        return machine_view(process_name, machine_id)
        
    # User authentication routes
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            success, message = register_user(email, password)
            if success:
                flash(message, 'success')
                return redirect(url_for('login'))
            else:
                flash(message, 'danger')
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            success, message = authenticate_user(email, password)
            if success:
                flash(message, 'success')
                return redirect(url_for('index'))
            else:
                flash(message, 'danger')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        flash('Logged out successfully.', 'info')
        return redirect(url_for('login'))
        
    # API routes
    @app.route('/api/process-data', methods=['GET'])
    def process_data():
        """Get data for all processes"""
        print("API endpoint /api/process-data called")
        from pymongo import MongoClient
        from flask import g
        
        try:
            # Create a dedicated connection for this API call
            mongo_client = MongoClient(app.config['MONGO_URI'])
            db = mongo_client.get_database()
            print("MongoDB connection established")
            
            # Make db available to the get_process_data function
            g.db = db
            
            try:
                data = get_process_data()
                print(f"API returned data: {type(data)} with {len(data) if isinstance(data, list) else 'ERROR'} items")
                return jsonify(data)
            except Exception as e:
                print(f"Error in process_data API when getting data: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": str(e)}), 500
            finally:
                # Always close the connection
                mongo_client.close()
                print("MongoDB connection closed")
        except Exception as e:
            print(f"Error in process_data API when connecting to MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"MongoDB connection error: {str(e)}"}), 500
    
    @app.route('/api/process/<process_name>', methods=['GET'])
    def process_detail(process_name):
        """Get data for a specific process"""
        from pymongo import MongoClient
        from flask import g
        
        # Create a dedicated connection for this API call
        mongo_client = MongoClient(app.config['MONGO_URI'])
        db = mongo_client.get_database()
        
        # Make db available to the get_process_data function
        g.db = db
        
        try:
            data = get_process_data(process_name)
            return jsonify(data)
        finally:
            # Always close the connection
            mongo_client.close()
    
    # New endpoint for machine status
    @app.route('/api/machine/<machine_id>/status', methods=['GET'])
    def machine_status(machine_id):
        """Get status and data for a specific machine"""
        return jsonify(get_machine_data(machine_id))
    
    # New endpoint for machine readings with time range filter
    @app.route('/api/machine/<machine_id>/readings', methods=['GET'])
    def machine_readings(machine_id):
        """Get readings for a specific machine with optional time range"""
        # Get time range from query parameters
        time_range = request.args.get('range', '24h')  # Default to 24 hours
        
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
    
    # New endpoint for machine control
    @app.route('/api/machine/<machine_id>/control', methods=['POST'])
    def machine_control(machine_id):
        """Control a machine (start, stop, maintenance, etc.)"""
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
        
        # Update machine status
        result = update_machine_status(machine_id, {
            'status': status_map[action],
            'timestamp': timestamp
        })
        
        return jsonify(result)
    
    # Add health check endpoint for Render.com
    @app.route('/health')
    def health_check():
        """Health check endpoint for Render.com"""
        try:
            # Try to get a database connection to verify everything is working
            from models import get_db
            from flask import g
            
            try:
                db = get_db()
                # Just ping the database
                db.command('ping')
                status = "healthy"
                db_status = "connected"
            except Exception as e:
                status = "degraded"
                db_status = f"error: {str(e)}"
            finally:
                # Close the connection if it exists
                if hasattr(g, 'mongo_client'):
                    g.mongo_client.close()
                    
            # Return health status
            from flask import jsonify
            return jsonify({
                "status": status,
                "database": db_status,
                "timestamp": str(datetime.datetime.now())
            })
        except Exception:
            from flask import jsonify
            return jsonify({
                "status": "unhealthy", 
                "database": "unavailable",
                "timestamp": str(datetime.datetime.now())
            }), 500