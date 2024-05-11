import email
from email import policy
from datetime import datetime
from ip_geolocation import get_ip_geolocation  # Ensure this module is correctly implemented

from virus_total import query_virustotal, analyze_ip_reputation # this is from virus total

import re

from datetime import datetime, timezone


def parse_timestamp(timestamp_str):
    # Normalize the timestamp string
    timestamp_str = re.sub(r'\s*\(\s*GMT\s*\)\s*', '', timestamp_str)  # Remove '(GMT)' if present
    timestamp_str = timestamp_str.replace('GMT', '').strip()  # Remove 'GMT'
    timestamp_str = re.sub(r'\s+', ' ', timestamp_str)  # Replace multiple spaces with a single space

    # Possible datetime formats to attempt
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # E.g., 'Tue, 23 Apr 2024 20:07:23 +0000'
        "%a, %d %b %Y %H:%M:%S",  # Without timezone
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)  # Assign UTC if no timezone
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

    # Updated regex for both IPv4 and IPv6
    ip_regex = re.compile(
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b'  # IPv4 addresses
        r'|\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b'  # IPv6 addresses
        r'|\b(?:[a-fA-F0-9]{1,4}:){1,7}:(?:[a-fA-F0-9]{1,4}){1,7}\b'  # Shortened IPv6
    )

    if headers["received"]:
        headers["received_details"] = []
        for received in headers["received"]:
            details = {}
            parts = received.split(';')
            if len(parts) > 1:
                details['timestamp'] = parse_timestamp(parts[1].strip())
                ips_found = ip_regex.findall(parts[0])
                ip = ips_found[-1] if ips_found else "Unknown"  # Use the last IP found
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
    """ Assess the phishing risk based on the locations of the IP addresses. """
    high_risk_countries = {'CN', 'RU', 'NG'}  # Example set of high-risk countries
    suspicious_patterns = []
    risk_score = 0

    # Check for high-risk countries
    for loc in locations:
        if loc['country'] in high_risk_countries:
            risk_score += 1
            suspicious_patterns.append(f"High-risk country: {loc['country']}")

    # Check for erratic geographical movements
    for i in range(1, len(locations)):
        if locations[i]['country'] != "Unknown Country" and locations[i - 1]['country'] != "Unknown Country":
            if locations[i]['country'] != locations[i - 1]['country']:
                suspicious_patterns.append(f"Jump from {locations[i - 1]['country']} to {locations[i]['country']}")

    # Simple heuristic: if more than two high-risk indicators are found, flag as suspicious
    if risk_score > 2:
        return True, suspicious_patterns
    return False, suspicious_patterns


# Modify the main function to include phishing risk assessment
def main():
    try:
        with open('headers.txt', 'r', encoding='utf-8') as file:
            raw_email = file.read()
    except FileNotFoundError:
        print("Error: 'headers.txt' file not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    parsed_headers = parse_email_headers(raw_email)
    locations = [detail['location'] for detail in parsed_headers.get('received_details', [])]
    is_suspicious, patterns = assess_phishing_risk(locations)

    print("\nEmail Analysis Results:")
    print(f"Source (Sender): {parsed_headers.get('from')}")
    print(f"Destination (Recipient): {parsed_headers.get('to')}")
    print(f"Subject: {parsed_headers.get('subject')}")
    print(f"Date Sent: {parsed_headers.get('date')}\n")

    print("Detailed Path Analysis:")
    for idx, detail in enumerate(parsed_headers.get('received_details', [])):
        location_info = detail['location']
        location_display = f"{location_info['city']}, {location_info['region']}, {location_info['country']}"
        print(f"  Hop {idx + 1}: IP: {detail['ip']} - {location_display}")
        print(f"       Timestamp: {detail['timestamp']}")

    print("\nDelays Between Hops:")
    delays = calculate_delays(parsed_headers.get('received_details', []))
    for idx, delay in enumerate(delays):
        print(f"  Delay {idx + 1}: {delay}")

    print("\nPhishing Risk Assessment:")
    print("Suspicious?" if is_suspicious else "Looks Safe")
    for pattern in patterns:
        print(f"- {pattern}")


if __name__ == "__main__":
    main()
