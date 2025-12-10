import os
import requests
import math
from typing import Dict, List, Optional, Tuple

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")


def geocode_address(address: str) -> Optional[Dict]:
    if not GOOGLE_MAPS_API_KEY:
        return None
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": GOOGLE_MAPS_API_KEY,
            "region": "in"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK" and data["results"]:
            result = data["results"][0]
            location = result["geometry"]["location"]
            
            return {
                "latitude": location["lat"],
                "longitude": location["lng"],
                "formatted_address": result["formatted_address"],
                "place_id": result.get("place_id"),
                "address_components": result.get("address_components", [])
            }
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None


def search_place(query: str, location: str = "India") -> Optional[Dict]:
    if not GOOGLE_MAPS_API_KEY:
        return None
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{query} {location}",
            "key": GOOGLE_MAPS_API_KEY,
            "region": "in"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK" and data["results"]:
            result = data["results"][0]
            location = result["geometry"]["location"]
            
            return {
                "name": result.get("name"),
                "address": result.get("formatted_address"),
                "latitude": location["lat"],
                "longitude": location["lng"],
                "place_id": result.get("place_id"),
                "business_status": result.get("business_status"),
                "types": result.get("types", []),
                "rating": result.get("rating"),
                "user_ratings_total": result.get("user_ratings_total")
            }
        return None
    except Exception as e:
        print(f"Place search error: {e}")
        return None


def get_satellite_image_url(latitude: float, longitude: float, zoom: int = 18, size: str = "600x400") -> str:
    if not GOOGLE_MAPS_API_KEY:
        return ""
    
    url = f"https://maps.googleapis.com/maps/api/staticmap"
    url += f"?center={latitude},{longitude}"
    url += f"&zoom={zoom}"
    url += f"&size={size}"
    url += f"&maptype=satellite"
    url += f"&key={GOOGLE_MAPS_API_KEY}"
    
    return url


def get_satellite_image_with_marker(latitude: float, longitude: float, zoom: int = 18) -> str:
    if not GOOGLE_MAPS_API_KEY:
        return ""
    
    url = f"https://maps.googleapis.com/maps/api/staticmap"
    url += f"?center={latitude},{longitude}"
    url += f"&zoom={zoom}"
    url += f"&size=600x400"
    url += f"&maptype=satellite"
    url += f"&markers=color:red%7C{latitude},{longitude}"
    url += f"&key={GOOGLE_MAPS_API_KEY}"
    
    return url


def calculate_polygon_area(coordinates: List[Tuple[float, float]]) -> float:
    if len(coordinates) < 3:
        return 0.0
    
    EARTH_RADIUS = 6378137
    
    def to_radians(degrees):
        return degrees * math.pi / 180
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        dlat = to_radians(lat2 - lat1)
        dlon = to_radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(to_radians(lat1)) * math.cos(to_radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return EARTH_RADIUS * c
    
    n = len(coordinates)
    area = 0.0
    
    center_lat = sum(c[0] for c in coordinates) / n
    center_lon = sum(c[1] for c in coordinates) / n
    
    x_coords = []
    y_coords = []
    
    for lat, lon in coordinates:
        x = haversine_distance(center_lat, center_lon, center_lat, lon)
        if lon < center_lon:
            x = -x
        y = haversine_distance(center_lat, center_lon, lat, center_lon)
        if lat < center_lat:
            y = -y
        x_coords.append(x)
        y_coords.append(y)
    
    for i in range(n):
        j = (i + 1) % n
        area += x_coords[i] * y_coords[j]
        area -= x_coords[j] * y_coords[i]
    
    area = abs(area) / 2.0
    return area


def meters_to_sqft(meters: float) -> float:
    return meters * 10.764


def estimate_building_area_from_coords(latitude: float, longitude: float, building_footprint_meters: float = None) -> Dict:
    if building_footprint_meters:
        area_sqm = building_footprint_meters
        area_sqft = meters_to_sqft(area_sqm)
    else:
        area_sqm = None
        area_sqft = None
    
    return {
        "latitude": latitude,
        "longitude": longitude,
        "area_sqm": area_sqm,
        "area_sqft": area_sqft,
        "measurement_method": "polygon_trace" if building_footprint_meters else "estimated"
    }


def get_place_details(place_id: str) -> Optional[Dict]:
    if not GOOGLE_MAPS_API_KEY or not place_id:
        return None
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": GOOGLE_MAPS_API_KEY,
            "fields": "name,formatted_address,geometry,formatted_phone_number,website,opening_hours,business_status,types,vicinity"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            result = data["result"]
            location = result.get("geometry", {}).get("location", {})
            
            return {
                "name": result.get("name"),
                "address": result.get("formatted_address"),
                "vicinity": result.get("vicinity"),
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
                "phone": result.get("formatted_phone_number"),
                "website": result.get("website"),
                "business_status": result.get("business_status"),
                "types": result.get("types", []),
                "opening_hours": result.get("opening_hours", {}).get("weekday_text", [])
            }
        return None
    except Exception as e:
        print(f"Place details error: {e}")
        return None


def verify_business_location(business_name: str, declared_address: str) -> Dict:
    result = {
        "verified": False,
        "google_found": False,
        "address_match": False,
        "discrepancies": [],
        "google_data": None,
        "satellite_url": None
    }
    
    place_data = search_place(business_name)
    
    if place_data:
        result["google_found"] = True
        result["google_data"] = place_data
        
        if place_data.get("latitude") and place_data.get("longitude"):
            result["satellite_url"] = get_satellite_image_with_marker(
                place_data["latitude"],
                place_data["longitude"]
            )
        
        google_address = place_data.get("address", "").lower()
        declared_lower = declared_address.lower()
        
        common_words = set(declared_lower.split()) & set(google_address.split())
        match_ratio = len(common_words) / max(len(declared_lower.split()), 1)
        
        if match_ratio > 0.4:
            result["address_match"] = True
            result["verified"] = True
        else:
            result["discrepancies"].append(f"Address mismatch: Declared '{declared_address}' vs Google '{place_data.get('address')}'")
        
        if place_data.get("business_status") == "CLOSED_TEMPORARILY":
            result["discrepancies"].append("Business is marked as temporarily closed on Google")
        elif place_data.get("business_status") == "CLOSED_PERMANENTLY":
            result["discrepancies"].append("Business is marked as permanently closed on Google")
            result["verified"] = False
    else:
        result["discrepancies"].append("Business not found on Google Maps - may indicate shell company")
    
    return result


def create_map_html(latitude: float, longitude: float, zoom: int = 16) -> str:
    if not GOOGLE_MAPS_API_KEY:
        return "<p>Google Maps API key not configured</p>"
    
    html = f"""
    <div id="map" style="width: 100%; height: 400px;"></div>
    <script>
        function initMap() {{
            var location = {{lat: {latitude}, lng: {longitude}}};
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: {zoom},
                center: location,
                mapTypeId: 'satellite'
            }});
            var marker = new google.maps.Marker({{
                position: location,
                map: map,
                title: 'Business Location'
            }});
        }}
    </script>
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap">
    </script>
    """
    return html


def get_nearby_businesses(latitude: float, longitude: float, radius: int = 500) -> List[Dict]:
    if not GOOGLE_MAPS_API_KEY:
        return []
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            businesses = []
            for place in data["results"][:20]:
                businesses.append({
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "types": place.get("types", []),
                    "rating": place.get("rating"),
                    "place_id": place.get("place_id")
                })
            return businesses
        return []
    except Exception as e:
        print(f"Nearby search error: {e}")
        return []
