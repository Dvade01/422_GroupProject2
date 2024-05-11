import requests

# API access tokens stored securely
IPINFO_ACCESS_TOKEN = '04994b1dbb44df'
IPSTACK_ACCESS_KEY = 'e6c6fa04228565e63ccdf65903e6b9f2'  # limit 100
IPGEOLOCATION_API_KEY = '0a300624c7df43dbb115d35cd7ca17fe'  # limit 1000
IPSTACK_REQUEST_LIMIT = 100
IPSTACK_USAGE_FILE = 'ipstack_usage.txt'


def read_request_count():
    try:
        with open(IPSTACK_USAGE_FILE, 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0


def increment_request_count():
    count = read_request_count() + 1
    with open(IPSTACK_USAGE_FILE, 'w') as file:
        file.write(str(count))


def get_ipinfo_geolocation(ip):
    """ Query IPinfo.io for geolocation data. """
    url = f"https://ipinfo.io/{ip}/json?token={IPINFO_ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {"city": data.get('city', 'Unknown City'),
                    "region": data.get('region', 'Unknown Region'),
                    "country": data.get('country', 'Unknown Country')}
        else:
            return None
    except Exception as e:
        print(f"IPinfo API error: {e}")
        return None


def get_ipstack_geolocation(ip):
    """ Query IPStack for geolocation data if under the request limit. """
    if read_request_count() >= IPSTACK_REQUEST_LIMIT:
        return None  # Skip the API call if limit is reached

    url = f"http://api.ipstack.com/{ip}?access_key={IPSTACK_ACCESS_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            increment_request_count()  # Update the request count only on successful API call
            data = response.json()
            return {"city": data.get('city', 'Unknown City'),
                    "region": data.get('region', 'Unknown Region'),
                    "country": data.get('country_name', 'Unknown Country')}
        else:
            return None
    except Exception as e:
        print(f"IPStack API error: {e}")
        return None


def get_ipgeolocation_geolocation(ip):
    """ Query IPGeolocation API for geolocation data. """
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={IPGEOLOCATION_API_KEY}&ip={ip}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {"city": data.get('city', 'Unknown City'),
                    "region": data.get('state_prov', 'Unknown Region'),
                    "country": data.get('country_name', 'Unknown Country')}
        else:
            return None
    except Exception as e:
        print(f"IPGeolocation API error: {e}")
        return None


def get_ip_geolocation(ip):
    """ Attempt to get geolocation data from multiple sources. """
    if ip.startswith('10.') or (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31) or ip.startswith(
            '192.168'):
        return {"city": "Private Network", "region": "N/A", "country": "N/A"}

    # Try IPinfo first
    data = get_ipinfo_geolocation(ip)
    if data and data["country"] != "Unknown Country":
        return data

    # Fallback: IPGeolocation
    data = get_ipgeolocation_geolocation(ip)
    if data and data["country"] != "Unknown Country":
        return data

    # Fallback to IPStack last resort
    data = get_ipstack_geolocation(ip)
    if data and data["country"] != "Unknown Country":
        return data

    return {"city": "Unknown City", "region": "Unknown Region", "country": "Unknown Country"}
