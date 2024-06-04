import email
from email import policy
from datetime import datetime, timezone
from ip_geolocation import get_ip_geolocation  # Ensure this module is correctly implemented
from virus_total import analyze_ip_reputation  # This is from virus total
import requests

def parse_timestamp(timestamp_str):
    timestamp_str = re.sub(r'\s*\(\s*GMT\s*\)\s*', '', timestamp_str)
    timestamp_str = timestamp_str.replace('GMT', '').strip()
    timestamp_str = re.sub(r'\s+', ' ', timestamp_str)
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    print(f"Failed to parse timestamp: {timestamp_str}")
    return "Unknown"

def parse_email_headers(raw_email):
    msg = email.message_from_string(raw_email, policy=policy.default)
    headers = {
        "from": msg.get('From'),
        "to": msg.get('To'),
        "subject": msg.get('Subject'),
        "date": msg.get('Date'),
        "received": msg.get_all('Received')
    }
    ip_regex = re.compile(
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        r'|\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b'
        r'|\b(?:[a-fA-F0-9]{1,4}:){1,7}:(?:[a-fA-F0-9]{1,4}){1,7}\b'
    )
    if headers["received"]:
        headers["received_details"] = []
        for received in headers["received"]:
            details = {}
            parts = received.split(';')
            if len(parts) > 1:
                details['timestamp'] = parse_timestamp(parts[1].strip())
                ips_found = ip_regex.findall(parts[0])
                ip = ips_found[-1] if ips_found else "Unknown"
                details['ip'] = ip
                details['location'] = get_ip_geolocation(ip)
                headers["received_details"].append(details)
    return headers

def calculate_delays(received_details):
    delays = []
    for i in range(1, len(received_details)):
        previous = received_details[i - 1]['timestamp']
        current = received_details[i]['timestamp']
        if previous == "Unknown" or current == "Unknown":
            delays.append("Timestamp missing")
        elif isinstance(previous, datetime) and isinstance(current, datetime):
            delay = (current - previous).total_seconds()
            delays.append(f"{abs(delay):.2f} seconds")
        else:
            delays.append("Incompatible timestamp types")
    return delays

def assess_phishing_risk(locations):
    high_risk_countries = {'CN', 'RU', 'NG', 'IR', 'KP', 'SY', 'VE', 'PK', 'ID'}
    suspicious_patterns = []
    risk_score = 0
    for loc in locations:
        if loc['country'] in high_risk_countries:
            risk_score += 1
            suspicious_patterns.append(f"High-risk country: {loc['country']}")
    for i in range(1, len(locations)):
        if locations[i]['country'] != "Unknown Country" and locations[i - 1]['country'] != "Unknown Country":
            if locations[i]['country'] != locations[i - 1]['country']:
                suspicious_patterns.append(f"Jump from {locations[i - 1]['country']} to {locations[i]['country']}")
    if risk_score > 2:
        return True, suspicious_patterns
    return False, suspicious_patterns

def generate_report(parsed_headers, delays, phishing_risk, patterns, vt_results):
    report = []
    report.append("Email Analysis Report\n")
    report.append(f"Source (Sender): {parsed_headers.get('from')}")
    report.append(f"Destination (Recipient): {parsed_headers.get('to')}")
    report.append(f"Subject: {parsed_headers.get('subject')}")
    report.append(f"Date Sent: {parsed_headers.get('date')}\n")
    report.append("Detailed Path Analysis:")
    for idx, detail in enumerate(parsed_headers.get('received_details', [])):
        location_info = detail['location']
        location_display = f"{location_info['city']}, {location_info['region']}, {location_info['country']}"
        report.append(f"  Hop {idx + 1}: IP: {detail['ip']} - {location_display}")
        report.append(f"       Timestamp: {detail['timestamp']}")
    report.append("\nDelays Between Hops:")
    for idx, delay in enumerate(delays):
        report.append(f"  Delay {idx + 1}: {delay}")
    report.append("\nPhishing Risk Assessment:")
    report.append("Suspicious?" if phishing_risk else "Looks Safe")
    for pattern in patterns:
        report.append(f"- {pattern}")
    report.append("\nVirusTotal Analysis:")
    for ip, result in vt_results.items():
        report.append(f"IP: {ip}")
        for key, value in result.items():
            report.append(f"  {key}: {value}")
        report.append("")
    return "\n".join(report)

def analyze_headers(raw_email):
    parsed_headers = parse_email_headers(raw_email)
    locations = [detail['location'] for detail in parsed_headers.get('received_details', [])]
    is_suspicious, patterns = assess_phishing_risk(locations)
    unique_ips = list(set(detail['ip'] for detail in parsed_headers.get('received_details', [])))
    vt_results = {ip: analyze_ip_reputation(ip) for ip in unique_ips if ip != "Unknown"}
    delays = calculate_delays(parsed_headers.get('received_details', []))
    report = generate_report(parsed_headers, delays, is_suspicious, patterns, vt_results)
    return report

if __name__ == "__main__":
    raw_email = input("Paste email headers below:\n").strip()
    if raw_email:
        report = analyze_headers(raw_email)
        with open('email_analysis_report.txt', 'w', encoding='utf-8') as report_file:
            report_file.write(report)
        print("Email analysis report generated and saved to 'email_analysis_report.txt'.")
    else:
        print("No email headers provided.")
