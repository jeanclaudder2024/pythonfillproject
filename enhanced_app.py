from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from enhanced_document_processor import EnhancedDocumentProcessor
from database_integration import SupabaseIntegration
import zipfile
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Get list of available vessels from database
    db_integration = SupabaseIntegration()
    vessels = db_integration.get_all_vessels(50)  # Get first 50 vessels
    
    return render_template('enhanced_index.html', vessels=vessels)

@app.route('/api/vessels')
def api_vessels():
    """API endpoint to get vessel list"""
    db_integration = SupabaseIntegration()
    vessels = db_integration.get_all_vessels(100)
    return jsonify(vessels)

@app.route('/api/vessel/<vessel_imo>')
def api_vessel_data(vessel_imo):
    """API endpoint to get specific vessel data"""
    db_integration = SupabaseIntegration()
    vessel_data = db_integration.get_vessel_data(vessel_imo)
    return jsonify(vessel_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    vessel_imo = request.form.get('vessel_imo', '').strip()
    vessel_id = request.form.get('vessel_id', '').strip()
    use_random_data = request.form.get('use_random_data') == 'on'
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if not vessel_imo and not vessel_id and not use_random_data:
        flash('Please provide vessel IMO number, select a vessel, or enable random data')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(original_path)
        
        try:
            # Process the document
            processor = EnhancedDocumentProcessor()
            
            if use_random_data:
                word_output, pdf_output = processor.process_document(original_path, file_id=file_id)
            elif vessel_imo:
                word_output, pdf_output = processor.process_document(original_path, vessel_imo=vessel_imo, file_id=file_id)
            elif vessel_id:
                word_output, pdf_output = processor.process_document(original_path, vessel_id=int(vessel_id), file_id=file_id)
            
            return redirect(url_for('results', file_id=file_id))
        
        except Exception as e:
            flash(f'Error processing document: {str(e)}')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload a .docx file')
        return redirect(url_for('index'))

@app.route('/results/<file_id>')
def results(file_id):
    word_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_filled.docx")
    pdf_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_filled.pdf")
    fallback_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_filled_fallback.txt")
    
    if os.path.exists(word_file):
        pdf_available = os.path.exists(pdf_file)
        fallback_available = os.path.exists(fallback_file)
        return render_template('enhanced_results.html', 
                             file_id=file_id, 
                             pdf_available=pdf_available, 
                             fallback_available=fallback_available)
    else:
        flash('Files not found')
        return redirect(url_for('index'))

@app.route('/download/<file_id>/<file_type>')
def download_file(file_id, file_type):
    if file_type == 'word':
        filename = f"{file_id}_filled.docx"
        mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file_type == 'pdf':
        filename = f"{file_id}_filled.pdf"
        mimetype = 'application/pdf'
    elif file_type == 'fallback':
        filename = f"{file_id}_filled_fallback.txt"
        mimetype = 'text/plain'
    else:
        flash('Invalid file type')
        return redirect(url_for('index'))
    
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename, mimetype=mimetype)
    else:
        if file_type == 'pdf':
            flash('PDF conversion failed. Please download the Word document instead.')
        else:
            flash('File not found')
        return redirect(url_for('results', file_id=file_id))

@app.route('/download_both/<file_id>')
def download_both(file_id):
    word_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_filled.docx")
    pdf_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_filled.pdf")
    fallback_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_filled_fallback.txt")
    
    if os.path.exists(word_file):
        # Create a zip file containing available documents
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            zf.write(word_file, f"filled_document.docx")
            if os.path.exists(pdf_file):
                zf.write(pdf_file, f"filled_document.pdf")
            elif os.path.exists(fallback_file):
                zf.write(fallback_file, f"pdf_conversion_failed.txt")
        memory_file.seek(0)
        
        return send_file(memory_file, as_attachment=True, download_name=f"filled_documents_{file_id}.zip", mimetype='application/zip')
    else:
        flash('Files not found')
        return redirect(url_for('index'))

@app.route('/test-database')
def test_database():
    """Test database connection and show available data"""
    db_integration = SupabaseIntegration()
    
    if not db_integration.enabled:
        return jsonify({"error": "Database integration disabled"})
    
    # Get sample data
    vessels = db_integration.get_all_vessels(10)
    
    return jsonify({
        "status": "connected",
        "vessels_count": len(vessels),
        "sample_vessels": vessels
    })

if __name__ == '__main__':
    print("Starting Enhanced Document Auto-Fill System")
    print("Database integration:", "Enabled" if SupabaseIntegration().enabled else "Disabled")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
