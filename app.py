from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from llama import extract_data
import json
import re
from pymongo import MongoClient
from datetime import datetime
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size 

# MongoDB connection
# Replace with your MongoDB connection string
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client['document_verification']
forms_collection = db['forms']

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Document type configurations
DOCUMENT_CONFIGS = {
    'aadhar': {
        'prompt': """
        Extract the following from the attached Aadhaar Card and provide the details in JSON format (keep the keys exactly same as mentioned below):
        - name
        - dob
        - gender
        - aadhar (not aadhar_number)
        """,
        'fields': ['name', 'dob', 'gender', 'aadhar']
    },
    'pan': {
        'prompt': """
        Extract the following from the attached PAN Card and provide the details in JSON format (keep the keys exactly same as mentioned below):
        - name
        - pan (not pan_number)
        """,
        'fields': ['name', 'pan']
    },
    'marksheet': {
        'prompt': """
        Extract the following from the attached Marksheet and provide the details in JSON format (keep the keys exactly same as mentioned below):
        - name (extract the full name of the student)
        - semester
        - rollNumber
        - cgpa (value is written under the block named 'CGPA')
        - sgpa (value is written under the block containing field as 'SGPA' and it is also possible that both cgpa and sgpa are identical)
        """,
        'fields': ['name', 'semester', 'rollNumber', 'cgpa', 'sgpa']
    }
}

def compare_values(form_value, doc_value, field):
    """Compare form value with document value, handling different data types"""
    if not form_value or not doc_value:
        return False
        
    if field in ['cgpa', 'sgpa']:
        try:
            form_float = float(form_value)
            doc_float = float(doc_value)
            return abs(form_float - doc_float) < 0.01  # Allow small floating point differences
        except ValueError:
            return False
    elif field == 'dob':
        # Normalize date format for comparison
        form_date = form_value.split('T')[0]  # Remove time part if present
        # Convert DD/MM/YYYY to YYYY-MM-DD for comparison
        if '/' in doc_value:
            day, month, year = doc_value.split('/')
            doc_value = f"{year}-{month}-{day}"
        return form_date.lower() == doc_value.lower()
    elif field == 'aadhar':
        # Special handling for Aadhar number (ignore spaces)
        form_normalized = re.sub(r'\s+', '', form_value).lower()
        doc_normalized = re.sub(r'\s+', '', doc_value).lower()
        return form_normalized == doc_normalized
    else:
        return str(form_value).lower().strip() == str(doc_value).lower().strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate-document', methods=['POST'])
def validate_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    doc_type = request.form.get('type')
    
    if not doc_type or doc_type not in DOCUMENT_CONFIGS:
        return jsonify({'error': 'Invalid document type'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save the file temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Extract data from document using Llama model
        doc_data = extract_data(filepath, DOCUMENT_CONFIGS[doc_type]['prompt'])
        
        if not doc_data:
            return jsonify({'error': 'Failed to extract data from document'}), 400
        
        # Get form data for comparison
        form_data = {}
        for field in DOCUMENT_CONFIGS[doc_type]['fields']:
            form_data[field] = request.form.get(field)
        
        # Compare values and collect mismatches
        mismatches = []
        validated_fields = []
        
        for field in DOCUMENT_CONFIGS[doc_type]['fields']:
            if field in doc_data and field in form_data:
                if not compare_values(form_data[field], doc_data[field], field):
                    mismatches.append({
                        'field': field,
                        'formValue': form_data[field],
                        'docValue': doc_data[field]
                    })
                else:
                    validated_fields.append(field)
        
        # Clean up the temporary file
        os.remove(filepath)
        
        return jsonify({
            'mismatches': mismatches,
            'validatedFields': validated_fields,
            'docData': doc_data  # Return document data for revalidation
        })
        
    except Exception as e:
        # Clean up the temporary file in case of error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Get all form data
        form_data = {
            'name': request.form.get('name'),
            'dob': request.form.get('dob'),
            'gender': request.form.get('gender'),
            'aadhar': request.form.get('aadhar'),
            'pan': request.form.get('pan'),
            'semester': request.form.get('semester'),
            'rollNumber': request.form.get('rollNumber'),
            'cgpa': request.form.get('cgpa'),
            'sgpa': request.form.get('sgpa'),
            'submissionDate': datetime.now(),
            'hasMismatches': request.form.get('hasMismatches', 'false').lower() == 'true'  # Get hasMismatches from form
        }
        
        # Check for document files
        documents = {}
        for doc_type in ['aadhar', 'pan', 'marksheet']:
            if doc_type in request.files and request.files[doc_type].filename:
                file = request.files[doc_type]
                filename = secure_filename(file.filename)
                
                # Save file temporarily
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract data from document
                doc_data = extract_data(filepath, DOCUMENT_CONFIGS[doc_type]['prompt'])
                
                # Store document data
                documents[doc_type] = {
                    'filename': filename,
                    'data': doc_data
                }
                
                # Check for mismatches
                if doc_data:
                    for field in DOCUMENT_CONFIGS[doc_type]['fields']:
                        if field in doc_data and field in form_data:
                            if not compare_values(form_data[field], doc_data[field], field):
                                form_data['hasMismatches'] = True
                
                # Clean up the temporary file
                os.remove(filepath)
        
        # Add documents to form data
        form_data['documents'] = documents
        
        # Save to MongoDB
        result = forms_collection.insert_one(form_data)
        
        return jsonify({
            'success': True,
            'message': 'Form submitted successfully',
            'data': {
                'id': str(result.inserted_id),
                'hasMismatches': form_data['hasMismatches']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True) 