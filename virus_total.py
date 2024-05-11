import requests

VIRUSTOTAL_API_KEY = 'efde8975518f872ae1cadf5f3d5f703764013681f0fa307c14bd61b6de498f7a'


def query_virustotal(ip):
    """ Query VirusTotal API for IP address reputation. """
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {"error": f"Failed to fetch data from VirusTotal: {response.status_code}"}


def analyze_ip_reputation(ip):
    """ Analyze the reputation of an IP using VirusTotal. """
    result = query_virustotal(ip)
    if 'error' not in result:
        # Example: Extract some information from the VirusTotal response
        malicious_votes = result['data']['attributes']['last_analysis_stats']['malicious']
        harmless_votes = result['data']['attributes']['last_analysis_stats']['harmless']
        return {
            "IP": ip,
            "Malicious Votes": malicious_votes,
            "Harmless Votes": harmless_votes,
            "Details": "Likely malicious" if malicious_votes > harmless_votes else "Likely harmless"
        }
    return result


# Example usage
ip_analysis = analyze_ip_reputation('8.8.8.8')
print(ip_analysis)
