from flask import Flask, request, render_template, redirect, url_for
import os
import json
import requests
import pyshark

# Create Flask app
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email Analysis Functionality
@app.route('/')
@app.route('/email_analysis')
def email_analysis():
    return render_template('Email Analysis.html')

@app.route('/analyze_email', methods=['POST'])
def analyze_email():
    raw_email = request.form['email_data']
    result = analyze_headers(raw_email)
    return render_template('Email Analysis.html', result=result)

# Geolocation Quiz Functionality
@app.route('/geolocation_quiz')
def geolocation_quiz():
    return render_template('Geolocation Quiz.html')

@app.route('/analyze_ip', methods=['POST'])
def analyze_ip():
    ip_address = request.form['ip_address']
    location = get_ip_geolocation(ip_address)
    result = f"IP Address: {ip_address}, Location: {location}"
    return render_template('Geolocation Quiz.html', result=result)

# Virus Detection Functionality
@app.route('/virus_detection')
def virus_detection():
    return render_template('Virus Detection.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        result = scan_file(filepath)
        return render_template('Virus Detection.html', result=result)

# Packet Capture Functionality
@app.route('/packet_capture')
def packet_capture():
    return render_template('Packet Capture.html')

@app.route('/upload_pcap', methods=['POST'])
def upload_pcap():
    if 'pcap_file' not in request.files:
        return redirect(request.url)

    file = request.files['pcap_file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        result = analyze_pcap(filepath)
        return render_template('Packet Capture.html', result=result)

# Helper Functions for Email Analysis
def analyze_headers(raw_email):
    # Your email analysis logic here
    return "Email analysis result"

# Helper Functions for Geolocation Quiz
def get_ip_geolocation(ip):
    # Your IP geolocation logic here
    return "Geolocation result"

# Helper Functions for Virus Detection
def scan_file(filepath):
    # Your virus detection logic here
    return "Virus detection result"

# Helper Functions for Packet Capture
def extract_info_from_pcap(pcap_file):
    cap = pyshark.FileCapture(pcap_file)
    ips = set()
    mac_addresses = set()
    hostnames = set()

    for packet in cap:
        if 'IP' in packet:
            ips.add(packet.ip.src)
            ips.add(packet.ip.dst)
        if 'eth' in packet:
            mac_addresses.add(packet.eth.src)
            mac_addresses.add(packet.eth.dst)
        if 'DNS' in packet and hasattr(packet.dns, 'qry_name'):
            hostnames.add(packet.dns.qry_name)

    cap.close()
    return list(ips), list(mac_addresses), list(hostnames)

def analyze_ips(ips):
    ip_reports = {}
    for ip in ips:
        ip_reports[ip] = analyze_ip_reputation(ip)
    return ip_reports

def analyze_ip_reputation(ip):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": "YOUR_VIRUSTOTAL_API_KEY"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

def deep_packet_inspection(pcap_file):
    cap = pyshark.FileCapture(pcap_file)
    suspicious_payloads = []

    for packet in cap:
        try:
            if 'TCP' in packet and hasattr(packet.tcp, 'payload'):
                payload = bytes.fromhex(packet.tcp.payload.replace(':', ''))
                if b'malicious' in payload or b'exploit' in payload:
                    suspicious_payloads.append(payload)
        except Exception:
            pass

    cap.close()
    return suspicious_payloads

def analyze_pcap_with_nfstream(pcap_file):
    # Example function to analyze with nfstream
    return []

def identify_suspicious_flows(dpi_results):
    suspicious_flows = []
    for result in dpi_results:
        if result.get('application_name') == 'Unknown' or result.get('protocol') not in [6, 17]:
            suspicious_flows.append(result)
    return suspicious_flows

def analyze_pcap(pcap_file):
    ips, mac_addresses, hostnames = extract_info_from_pcap(pcap_file)
    ip_reports = analyze_ips(ips)
    suspicious_payloads = deep_packet_inspection(pcap_file)
    dpi_results = analyze_pcap_with_nfstream(pcap_file)
    suspicious_flows = identify_suspicious_flows(dpi_results)

    report = f"Extracted IPs: {ips}<br>Extracted MAC Addresses: {mac_addresses}<br>Hostnames: {hostnames}<br>"
    report += f"VirusTotal Reports: {json.dumps(ip_reports, indent=4)}<br>"
    report += f"Suspicious Payloads: {suspicious_payloads}<br>"
    report += f"Suspicious Flows: {suspicious_flows}<br>"
    return report

if __name__ == "__main__":
    app.run(debug=True)
