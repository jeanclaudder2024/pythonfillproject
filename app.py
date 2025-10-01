from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import uuid
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor
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
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    vessel_imo = request.form.get('vessel_imo', '').strip()
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if not vessel_imo:
        flash('Please provide vessel IMO number')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(original_path)
        
        try:
            # Process the document
            processor = DocumentProcessor()
            word_output, pdf_output = processor.process_document(original_path, vessel_imo, file_id)
            
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
        return render_template('results.html', file_id=file_id, pdf_available=pdf_available, fallback_available=fallback_available)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)