#!/usr/bin/env python
"""
MongoDB connection test script for Render.com environment.
This script tests the MongoDB connection before starting the app
to diagnose SSL/TLS issues.
"""

import os
import sys
import ssl
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection():
    print("Testing MongoDB connection...")
    
    # Get MongoDB URI from environment or use default
    mongo_uri = os.environ.get(
        'MONGO_URI', 
        'mongodb+srv://gowrish:ftG3flLkxYpdZ0tN@cluster0.el1hbyt.mongodb.net/gowrish?retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsAllowInvalidCertificates=false'
    )
    
    # Detect if running on Render
    is_render = os.environ.get('RENDER', False)
    
    connection_methods = []
    
    # Method 1: Basic connection
    connection_methods.append(("Standard connection", {
        "uri": mongo_uri,
        "serverSelectionTimeoutMS": 5000
    }))
    
    # Method 2: With SSL configuration
    connection_methods.append(("SSL configuration", {
        "uri": mongo_uri,
        "serverSelectionTimeoutMS": 5000,
        "ssl": True,
        "ssl_cert_reqs": ssl.CERT_REQUIRED,
        "ssl_ca_certs": certifi.where()
    }))
    
    # Method 3: With TLS configuration
    connection_methods.append(("TLS configuration", {
        "uri": mongo_uri,
        "serverSelectionTimeoutMS": 5000, 
        "tls": True,
        "tlsCAFile": certifi.where()
    }))
    
    # Method 4: Render-specific with system certs
    if is_render:
        connection_methods.append(("Render system certs", {
            "uri": mongo_uri,
            "serverSelectionTimeoutMS": 5000,
            "ssl": True,
            "tls": True,
            "tlsCAFile": "/etc/ssl/certs/ca-certificates.crt"
        }))
    
    # Test all connection methods
    success = False
    successful_method = None
    
    for method_name, config in connection_methods:
        print(f"\nTrying {method_name}...")
        uri = config.pop("uri")
        
        try:
            client = MongoClient(uri, **config)
            # Force a connection to verify it works
            client.admin.command('ping')
            print(f"✓ {method_name} SUCCESSFUL")
            success = True
            successful_method = method_name
            client.close()
            break
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"✗ {method_name} FAILED: {e}")
        except Exception as e:
            print(f"✗ {method_name} ERROR: {type(e).__name__}: {e}")
    
    if success:
        print(f"\n✓ MongoDB connection successful using {successful_method}")
        print("You can use these settings in your application")
        return 0
    else:
        print("\n✗ All MongoDB connection methods failed")
        print("Check your MongoDB URI, network connection, and SSL/TLS settings")
        return 1

if __name__ == "__main__":
    sys.exit(test_mongodb_connection())
