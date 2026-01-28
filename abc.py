from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# File to store attendance records
ATTENDANCE_FILE = 'attendance_records.json'

def load_records():
    """Load attendance records from file"""
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r') as f:
            return json.load(f)
    return []

def save_records(records):
    """Save attendance records to file"""
    with open(ATTENDANCE_FILE, 'w') as f:
        json.dump(records, f, indent=4)

@app.route("/")
def index():
    """Render the main attendance tracker page"""
    return render_template("index.html")

@app.route("/api/attendance", methods=['GET'])
def get_attendance():
    """Get all attendance records"""
    records = load_records()
    return jsonify(records)

@app.route("/api/attendance", methods=['POST'])
def add_attendance():
    """Add a new attendance record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['name', 'date', 'status']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new record
        new_record = {
            'id': datetime.now().timestamp(),
            'name': data['name'],
            'date': data['date'],
            'status': data['status'],
            'remarks': data.get('remarks', ''),
            'created_at': datetime.now().isoformat()
        }
        
        # Load existing records and add new one
        records = load_records()
        records.append(new_record)
        save_records(records)
        
        return jsonify(new_record), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/attendance/<float:record_id>", methods=['DELETE'])
def delete_attendance(record_id):
    """Delete an attendance record"""
    try:
        records = load_records()
        records = [r for r in records if r['id'] != record_id]
        save_records(records)
        
        return jsonify({'message': 'Record deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/attendance/<float:record_id>", methods=['PUT'])
def update_attendance(record_id):
    """Update an attendance record"""
    try:
        data = request.get_json()
        records = load_records()
        
        for record in records:
            if record['id'] == record_id:
                record.update(data)
                record['updated_at'] = datetime.now().isoformat()
                save_records(records)
                return jsonify(record), 200
        
        return jsonify({'error': 'Record not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/attendance/stats", methods=['GET'])
def get_stats():
    """Get attendance statistics"""
    try:
        records = load_records()
        
        stats = {
            'total': len(records),
            'present': len([r for r in records if r['status'] == 'Present']),
            'absent': len([r for r in records if r['status'] == 'Absent']),
            'late': len([r for r in records if r['status'] == 'Late'])
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/attendance/search", methods=['GET'])
def search_attendance():
    """Search attendance records by name or date"""
    try:
        name = request.args.get('name', '').lower()
        date = request.args.get('date', '')
        
        records = load_records()
        
        filtered_records = records
        if name:
            filtered_records = [r for r in filtered_records if name in r['name'].lower()]
        if date:
            filtered_records = [r for r in filtered_records if r['date'] == date]
        
        return jsonify(filtered_records), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
