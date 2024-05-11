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
        return response.json()
    else:
        return {"error": f"Failed to fetch data from VirusTotal: {response.status_code}"}


def analyze_ip_reputation(ip):
    """ Analyze the reputation of an IP using VirusTotal with prioritization for specific vendors. """
    result = query_virustotal(ip)
    if 'error' not in result:
        analysis_results = result['data']['attributes']['last_analysis_results']
        preferred_vendors = ['Webroot', 'Fortinet', 'Bitdefender']
        vendor_reports = {}

        for vendor in preferred_vendors:
            vendor_report = analysis_results.get(vendor, {})
            vendor_reports[vendor] = {
                "Detected": vendor_report.get("detected", "No data"),
                "Result": vendor_report.get("result", "No data")
            }

        malicious_votes = result['data']['attributes']['last_analysis_stats']['malicious']
        harmless_votes = result['data']['attributes']['last_analysis_stats']['harmless']

        analysis_details = {
            "IP": ip,
            "Malicious Votes": malicious_votes,
            "Harmless Votes": harmless_votes,
            "Preferred Vendor Reports": vendor_reports,
            "General Assessment": "Likely malicious" if malicious_votes > harmless_votes else "Likely harmless"
        }

        # Formatting the dictionary output more vertically
        formatted_output = "\n".join([f"{key}: {value}" for key, value in analysis_details.items()])
        return formatted_output

    return "Error in retrieving data"


# Example usage
ip_analysis = analyze_ip_reputation('8.8.8.8')
print(ip_analysis)