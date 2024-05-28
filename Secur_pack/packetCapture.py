import pyshark
import requests
import os
import json
import time
from virus_total import analyze_ip_reputation
from nfstreamer import analyze_pcap_with_nfstream


# Function to extract IPs, MAC addresses, and hostnames from a pcap file
def extract_info_from_pcap(pcap_file):
    if not os.path.isfile(pcap_file):
        raise FileNotFoundError(f"[Errno 2] No such file or directory: '{pcap_file}'")

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
        if 'DNS' in packet:
            if hasattr(packet.dns, 'qry_name'):
                hostnames.add(packet.dns.qry_name)

    cap.close()
    return list(ips), list(mac_addresses), list(hostnames)


# Function to lookup OUI
def lookup_mac_oui(mac_address, retries=3):
    url = f"https://api.macvendors.com/{mac_address}"
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                time.sleep(2 ** attempt)
                attempt += 1
        except requests.exceptions.RequestException:
            time.sleep(2 ** attempt)
            attempt += 1
    return "Unknown"


# Function to handle rate limiting with exponential backoff
def rate_limit_sleep(attempt):
    time.sleep(min(2 ** attempt, 60))


def analyze_reports(ip_reports):
    malicious_ips = []
    for ip, report in ip_reports.items():
        if report['Malicious Votes'] > 0:
            malicious_ips.append(ip)
    return malicious_ips


def deep_packet_inspection(pcap_file):
    cap = pyshark.FileCapture(pcap_file)
    suspicious_payloads = []

    for packet in cap:
        try:
            if 'TCP' in packet and hasattr(packet.tcp, 'payload'):
                payload = bytes.fromhex(packet.tcp.payload.replace(':', ''))
                if b'malicious' in payload or b'exploit' in payload:
                    suspicious_payloads.append(payload)
        except Exception as e:
            pass

    cap.close()
    return suspicious_payloads


def main():
    # Path to the pcap file
    pcap_file = 'C:/Users/David/Desktop/422_GroupProject2/pcap_dir/2023-01-Unit42-Wireshark-quiz.pcap/2023-01-Unit42-Wireshark-quiz.pcap'

    # Extract IP addresses, MAC addresses, and hostnames from the pcap file
    ips, mac_addresses, hostnames = extract_info_from_pcap(pcap_file)
    print("Extracted IPs:", ips)
    print("Extracted MAC Addresses:", mac_addresses)
    print("Extracted Hostnames:")
    for hostname in hostnames:
        print(hostname)

    for mac in mac_addresses:
        oui = lookup_mac_oui(mac)
        print(f"MAC Address: {mac}, OUI Lookup: {oui}")

    # Analyze unique IP addresses using VirusTotal
    unique_ips = set(ips)
    queried_ips = set()
    ip_reports = {}
    for ip in unique_ips:
        if ip not in queried_ips:
            for attempt in range(5):
                try:
                    vt_report = analyze_ip_reputation(ip)
                    ip_reports[ip] = vt_report
                    print(f"VirusTotal Report for IP {ip}:", json.dumps(vt_report, indent=4))
                    queried_ips.add(ip)
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Error querying VirusTotal for IP {ip}: {e}")
                    rate_limit_sleep(attempt)

    # Perform Deep Packet Inspection
    suspicious_payloads = deep_packet_inspection(pcap_file)
    if suspicious_payloads:
        print("Suspicious payloads detected:")
        for payload in suspicious_payloads:
            print(payload)
    else:
        print("No suspicious payloads detected.")

    # Perform Deep Packet Inspection using NFStream
    dpi_results = analyze_pcap_with_nfstream(pcap_file)

    # Analyze DPI results (example: detect anomalies, identify suspicious flows, etc.)
    suspicious_flows = []
    for result in dpi_results:
        if result['application_name'] == 'Unknown' or result['protocol'] not in [6, 17]:
            suspicious_flows.append(result)

    if suspicious_flows:
        print("Suspicious flows detected:")
        for flow in suspicious_flows:
            print(flow)
    else:
        print("No suspicious flows detected.")

    # Analyze the reports to summarize the conclusion
    malicious_ips = analyze_reports(ip_reports)
    if malicious_ips:
        print("Conclusion: The following IP addresses are flagged as potentially dangerous:")
        for ip in malicious_ips:
            print(f"- {ip}")
    else:
        print("Conclusion: No malicious activity detected in the analyzed IP addresses.")


if __name__ == "__main__":
    main()
