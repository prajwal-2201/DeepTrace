from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import os
import threading
from core.disk_analysis import DiskAnalyzer
from core.file_recovery import FileRecoverer
from core.metadata_extractor import MetadataExtractor
from core.registry_parser import RegistryParser
from core.browser_parser import BrowserParser
from analysis.entropy_checker import EntropyChecker
from analysis.anomaly_detector import AnomalyDetector
from analysis.yara_scanner import YaraScanner
from analysis.pii_detector import PIIDetector
from integrity.hash_generator import HashGenerator
from report.timeline_builder import TimelineBuilder
from report.report_generator import ReportGenerator
from stego.lsb_detector import LSBDetector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forensics_secret_key'
# Using threading for compatibility; in prod use eventlet/gevent
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

analysis_status = "idle"

def log_msg(msg, is_error=False):
    print(f"> {msg}")
    # Emit instantly to connected frontend clients
    socketio.emit('log_event', {'msg': msg, 'is_error': is_error})

def run_analysis_pipeline(image_path, options):
    global analysis_status
    analysis_status = "running"
    
    try:
        log_msg(f"Initializing Enterprise Scan for target: {image_path}")
        
        # Init modules
        yara_scanner = YaraScanner()
        
        # 1. Target Acquisition
        analyzer = None
        try:
            analyzer = DiskAnalyzer(image_path)
            analyzer.load_image()
            log_msg("Disk image loaded successfully via pytsk3/pyewf.")
        except Exception as e:
            log_msg(f"WARNING: Disk load failed ({e}). Attempting logical directory scan...", is_error=True)

        # 2. Extract Metadata & Timeline
        all_metadata = []
        if options.get("metadata") and analyzer and analyzer.fs_info:
            log_msg("Extracting file system metadata for Timeline analysis...")
            root_dir = analyzer.get_root_directory()
            all_metadata = MetadataExtractor.walk_and_extract(root_dir)
            log_msg(f"Extracted metadata for {len(all_metadata)} files.")

        # 3. File Recovery
        recovered_files = []
        if options.get("recover") and analyzer and analyzer.fs_info:
            log_msg("Carving unallocated space for deleted artifacts...")
            recoverer = FileRecoverer(analyzer.fs_info)
            recovered_files = recoverer.recover_deleted_files(analyzer.get_root_directory())
            log_msg(f"Recovered {len(recovered_files)} deleted files.")

        scan_target_dir = "data/recovered" if recovered_files else image_path
        
        # 4. Deep Inspection (Hashes, Entropy, YARA, PII, Magic Bytes)
        anomalies = []
        hashes = []
        chart_data = {"entropy": []} # For the frontend Chart.js
        
        if os.path.isdir(scan_target_dir):
            log_msg("Executing Threat Hunting heuristics (YARA, PII, Entropy)...")
            for root, dirs, files in os.walk(scan_target_dir):
                for f in files:
                    filepath = os.path.join(root, f)
                    
                    # Hash
                    file_hash = HashGenerator.generate_hashes(filepath)
                    if file_hash: hashes.append(file_hash)
                    
                    # Threat Intel (YARA)
                    yara_hits = yara_scanner.scan_file(filepath)
                    for hit in yara_hits:
                        anomalies.append(hit)
                        
                    # Data Leak (PII)
                    pii_hits = PIIDetector.scan_file(filepath)
                    for hit in pii_hits:
                        anomalies.append(hit)
                    
                    # Entropy (Encryption/Stego detection)
                    ent = EntropyChecker.analyze_file(filepath)
                    chart_data["entropy"].append({"file": f[:10]+"...", "val": ent["entropy"]})
                    if ent.get("is_encrypted_or_packed"):
                        anomalies.append({
                            "file": filepath, "severity": "MEDIUM", "reason": f"High Entropy ({ent['entropy']})"
                        })
                        
                    # Magic Byte Mismatch
                    mismatch = AnomalyDetector.detect_mismatch(filepath)
                    if mismatch: anomalies.append(mismatch)

                    # Steganography Detection (Images)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        stego_res = LSBDetector.detect_hidden_data(filepath)
                        if stego_res.get("suspicious"):
                            anomalies.append({
                                "file": filepath,
                                "type": "STEGO_SUSPECT",
                                "severity": "HIGH",
                                "reason": f"Suspicious LSB Entropy ({stego_res['lsb_entropy']})"
                            })
                    
                    # OS/App Parsers
                    if f.upper() in ["SAM", "SYSTEM", "NTUSER.DAT"]:
                        log_msg(f"Found Windows Hive: {f}. Parsing...")
                        reg_res = RegistryParser.parse_hive(filepath)
                        if reg_res: log_msg(f"Registry Findings: {reg_res}")
                        
                    if f.lower() == "history":
                        log_msg("Found Browser History SQLite DB. Parsing...")
                        hist_res = BrowserParser.parse_chrome_history(filepath)
                        if hist_res: log_msg(f"Browser History parsed successfully.")

        # 5. Timeline & Reporting
        timeline = TimelineBuilder.build_timeline(all_metadata)
        
        report_data = {
            "target_image": image_path,
            "recovered_files": recovered_files,
            "anomalies": anomalies,
            "hashes": hashes,
            "timeline": timeline
        }
        
        log_msg("Compiling Enterprise Forensic Report...")
        rg = ReportGenerator()
        json_path = rg.generate_json(report_data)
        pdf_path = rg.generate_pdf(report_data)
        
        if json_path:
            log_msg(f"JSON Report generated: {json_path}")
        else:
            log_msg("WARNING: JSON Report generation failed.", is_error=True)
            
        if pdf_path:
            log_msg(f"PDF Report generated: {pdf_path}")
        else:
            log_msg("WARNING: PDF Report generation failed. (Check ReportLab installation)", is_error=True)
            
        log_msg("Analysis Pipeline COMPLETE.", is_error=False)
        
        analysis_status = "complete"
        socketio.emit('scan_complete', {
            "parsed": len(all_metadata) if all_metadata else len(hashes),
            "recovered": len(recovered_files),
            "anomalies": len(anomalies),
            "chart_data": chart_data
        })
        
    except Exception as e:
        log_msg(f"CRITICAL ERROR: {str(e)}", is_error=True)
        analysis_status = "error"
        socketio.emit('scan_error')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    global analysis_status
    if analysis_status == "running":
        return jsonify({"status": "error", "message": "Analysis already in progress."}), 400
        
    data = request.json
    image_path = data.get("path")
    options = data.get("options", {})
    
    if not image_path:
        return jsonify({"status": "error", "message": "Image path required"}), 400

    thread = threading.Thread(target=run_analysis_pipeline, args=(image_path, options))
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "processing", "message": "Analysis started"})
    
@app.route('/api/download/json')
def download_json():
    return send_from_directory(os.path.join(os.getcwd(), 'data/reports'), 'forensic_report.json', as_attachment=True)

@app.route('/api/download/pdf')
def download_pdf():
    return send_from_directory(os.path.join(os.getcwd(), 'data/reports'), 'forensic_report.pdf', as_attachment=True)

