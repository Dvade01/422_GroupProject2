import pyshark
import requests
import re
import os
import json
import time
from virus_total import query_virustotal, analyze_ip_reputation


# Function to extract hostnames, IPs, and MAC addresses from a pcap file
def extract_info_from_pcap(pcap_file):
    if not os.path.isfile(pcap_file):
        raise FileNotFoundError(f"[Errno 2] No such file or directory: '{pcap_file}'")

    cap = pyshark.FileCapture(pcap_file, display_filter="(http.request or tls.handshake.type eq 1) and !(ssdp)")
    hostnames = set()
    ips = set()
    mac_addresses = set()

    for packet in cap:
        if 'IP' in packet:
            ips.add(packet.ip.src)
            ips.add(packet.ip.dst)
        if 'DNS' in packet:
            if hasattr(packet.dns, 'qry_name'):
                hostnames.add(packet.dns.qry_name)
        if 'eth' in packet:
            mac_addresses.add(packet.eth.src)
            mac_addresses.add(packet.eth.dst)

    cap.close()
    return list(hostnames), list(ips), list(mac_addresses)


# Function to extract user accounts and hostnames from a pcap file
def extract_user_accounts_and_hostnames(pcap_file):
    cap = pyshark.FileCapture(pcap_file)
    user_accounts = set()
    hostnames = set()

    for packet in cap:
        if 'NBNS' in packet:
            if hasattr(packet.nbns, 'query_name'):
                hostnames.add(packet.nbns.query_name)
        if 'SMB' in packet or 'SMB2' in packet:
            if hasattr(packet, 'smb'):
                if hasattr(packet.smb, 'cname_string'):
                    hostnames.add(packet.smb.cname_string)
                if hasattr(packet.smb, 'username'):
                    user_accounts.add(packet.smb.username)
            if hasattr(packet, 'smb2'):
                if hasattr(packet.smb2, 'cname_string'):
                    hostnames.add(packet.smb2.cname_string)
                if hasattr(packet.smb2, 'username'):
                    user_accounts.add(packet.smb2.username)
        if 'KERBEROS' in packet:
            if hasattr(packet.kerberos, 'cname_string'):
                user_accounts.add(packet.kerberos.cname_string)

    cap.close()
    return user_accounts, hostnames


# Function to lookup OUI
def lookup_mac_oui(mac_address):
    url = f"https://api.macvendors.com/{mac_address}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "Unknown"
    except Exception as e:
        return str(e)


# Function to handle rate limiting with exponential backoff
def rate_limit_sleep(attempt):
    time.sleep(min(2 ** attempt, 60))


def main():
    # Path to the pcap file
    pcap_file = 'C:/Users/David/Desktop/422_GroupProject2/pcap_dir/2023-01-Unit42-Wireshark-quiz.pcap/2023-01-Unit42-Wireshark-quiz.pcap'

    # Extract hostnames, IP addresses, and MAC addresses from the pcap file
    hostnames, ips, mac_addresses = extract_info_from_pcap(pcap_file)
    print("Extracted Hostnames:", hostnames)
    print("Extracted IPs:", ips)
    print("Extracted MAC Addresses:", mac_addresses)

    for mac in mac_addresses:
        oui = lookup_mac_oui(mac)
        print(f"MAC Address: {mac}, OUI Lookup: {oui}")

    # Extract user accounts and additional hostnames from the pcap file
    user_accounts, additional_hostnames = extract_user_accounts_and_hostnames(pcap_file)
    print("Extracted User Accounts:", user_accounts)
    print("Extracted Additional Hostnames:", additional_hostnames)

    # Combine hostnames
    hostnames.extend(additional_hostnames)

    # Analyze hostnames using VirusTotal
    queried_hostnames = set()
    for hostname in hostnames:
        if hostname not in queried_hostnames:
            for attempt in range(5):
                try:
                    vt_report = query_virustotal(hostname)
                    print(f"VirusTotal Report for Hostname {hostname}:", json.dumps(vt_report, indent=4))
                    queried_hostnames.add(hostname)
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Error querying VirusTotal for Hostname {hostname}: {e}")
                    rate_limit_sleep(attempt)

    # Analyze unique IP addresses using VirusTotal
    unique_ips = set(ips)
    queried_ips = set()
    for ip in unique_ips:
        if ip not in queried_ips:
            for attempt in range(5):
                try:
                    vt_report = analyze_ip_reputation(ip)
                    print(f"VirusTotal Report for IP {ip}:", json.dumps(vt_report, indent=4))
                    queried_ips.add(ip)
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Error querying VirusTotal for IP {ip}: {e}")
                    rate_limit_sleep(attempt)


if __name__ == "__main__":
    main()
