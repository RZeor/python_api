from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Folders
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'success',
        'service': 'Spatial Clustering API',
        'endpoints': {
            'clustering': 'POST /api/clustering',
            'get_results': 'GET /api/results',
            'health': 'GET /health'
        }
    })

@app.route('/api/clustering', methods=['POST'])
def clustering():
    """Run clustering analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type. Use CSV or Excel'}), 400
        
        # Parameters
        linkage = request.form.get('linkage', 'ward')
        metric = request.form.get('metric', 'euclidean')
        n_clusters = request.form.get('n_clusters', '3')
        
        # Save file
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        # Output path
        output_path = os.path.join(RESULTS_FOLDER, 'cluster_results.json')
        
        # Run clustering script
        cmd = [
            'python', 'clustering_script.py',
            input_path,
            output_path,
            '--linkage', linkage,
            '--metric', metric,
            '--n_clusters', n_clusters
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'message': 'Clustering failed',
                'error': result.stderr,
                'output': result.stdout
            }), 500
        
        # Read and return results
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            return jsonify({
                'success': True,
                'message': 'Clustering completed successfully',
                'data': results
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Results file not created'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'message': 'Clustering timeout'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get clustering results"""
    try:
        results_path = os.path.join(RESULTS_FOLDER, 'cluster_results.json')
        
        if not os.path.exists(results_path):
            return jsonify({'success': False, 'message': 'No results found'}), 404
        
        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        return jsonify({'success': True, 'data': results})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'Spatial Clustering API'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
