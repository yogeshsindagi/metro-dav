import requests

def geocode_address(address: str):
    """
    Geocodes an address to latitude and longitude using Nominatim (OpenStreetMap).
    Returns {"lat": float, "lng": float} or None if not found.
    """
    if not address or not address.strip():
        return None
        
    try:
        # Nominatim requires a user-agent
        headers = {
            "User-Agent": "TransitCostAnalyzer/1.0 (contact@example.com)"
        }
        # Add 'Bangalore' or 'Bengaluru' to help improve local search if needed,
        # but we'll assume the user includes it or we just search the raw address.
        query = f"{address}, Bengaluru, India"
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 1
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            return {
                "lat": float(data[0]["lat"]),
                "lng": float(data[0]["lon"])
            }
            
    except Exception as e:
        print(f"Geocoding error for address '{address}': {e}")
        
    return None
