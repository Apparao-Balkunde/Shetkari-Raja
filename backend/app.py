from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

app = Flask(__name__)
CORS(app)

# Mock database
ADVISORIES = {
    'maharashtra': [
        "रब्बी पिकांसाठी जमीन तयार करा",
        "गहू लागवडीसाठी उत्तम वेळ",
        "इंद्रधनुष्य फॅटिंगसाठी योग्य हवामान"
    ],
    'karnataka': [
        "कापूस काढणीसाठी तयार व्हा",
        "सोयाबीनची किंमत वाढणार"
    ]
}

MARKET_PRICES = {
    'maharashtra': [
        {"crop": "सोयाबीन", "price": "₹4,200/क्विंटल"},
        {"crop": "कापूस", "price": "₹6,500/क्विंटल"}
    ],
    'karnataka': [
        {"crop": "रागी", "price": "₹3,800/क्विंटल"},
        {"crop": "कॉफी", "price": "₹8,200/क्विंटल"}
    ]
}

@app.route('/api/weather/<district>', methods=['GET'])
def get_weather(district):
    """Fetch weather data - in production, call IMD API here"""
    # Example of how to call an actual API:
    # response = requests.get(f"https://api.imd.gov.in/weather/{district}")
    # return jsonify(response.json())
    
    # Mock response
    return jsonify({
        "temp": "28°C",
        "rainfall": "15mm",
        "humidity": "65%",
        "forecast": "Partly cloudy",
        "district": district,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/advisory/<state>', methods=['GET'])
def get_advisory(state):
    """Get crop advisories for the state"""
    state = state.lower()
    return jsonify(ADVISORIES.get(state, ADVISORIES['maharashtra']))

@app.route('/api/market/<state>', methods=['GET'])
def get_market_prices(state):
    """Get market prices for the state"""
    state = state.lower()
    return jsonify(MARKET_PRICES.get(state, MARKET_PRICES['maharashtra']))

@app.route('/api/soil/<village>', methods=['GET'])
def get_soil_info(village):
    """Get soil information - could integrate with Google Maps API"""
    # In production, call Google Maps API here
    return jsonify({
        "village": village,
        "soil_type": "काळी माती",
        "ph_level": "7.2",
        "nutrients": {
            "नायट्रोजन": "मध्यम",
            "पोटॅश": "उच्च",
            "फॉस्फरस": "कमी"
        }
    })
    
@app.route('/api/nearest-mandi', methods=['GET'])
def get_nearest_mandi():
    """
    Find distance to nearest agricultural market (mandi)
    Parameters:
    - origin_lat, origin_lng: farmer's location
    """
    try:
        origin_lat = request.args.get('origin_lat')
        origin_lng = request.args.get('origin_lng')
        
        if not origin_lat or not origin_lng:
            return jsonify({"status": "error", "message": "Origin coordinates are required"}), 400
        
        # First find nearby mandis
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places_params = {
            "location": f"{origin_lat},{origin_lng}",
            "radius": "20000",  # 20km radius
            "keyword": "agriculture market|mandi",
            "key": GOOGLE_MAPS_API_KEY,
            "language": "mr"
        }
        
        places_response = requests.get(places_url, params=places_params)
        places_data = places_response.json()
        
        if not places_data.get('results'):
            return jsonify({"status": "success", "message": "No mandis found nearby", "count": 0})
        
        # Get details of the first mandi found
        mandi = places_data['results'][0]
        dest_lat = mandi['geometry']['location']['lat']
        dest_lng = mandi['geometry']['location']['lng']
        
        # Calculate distance
        distance_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        distance_params = {
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{dest_lat},{dest_lng}",
            "key": GOOGLE_MAPS_API_KEY,
            "language": "mr"
        }
        
        distance_response = requests.get(distance_url, params=distance_params)
        distance_data = distance_response.json()
        
        result = {
            "mandi_name": mandi.get('name'),
            "mandi_address": mandi.get('vicinity'),
            "distance": distance_data['rows'][0]['elements'][0]['distance']['text'],
            "duration": distance_data['rows'][0]['elements'][0]['duration']['text'],
            "location": mandi['geometry']['location']
        }
        
        return jsonify({
            "status": "success",
            "result": result
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500   


@app.route('/api/water-resources', methods=['GET'])
def get_water_resources():
    """
    Find water resources in specified area
    Parameters:
    - lat, lng: coordinates
    - radius: search radius (meters)
    """
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        radius = request.args.get('radius', '10000')  # Default 10km radius
        
        if not lat or not lng:
            return jsonify({"status": "error", "message": "Latitude and longitude are required"}), 400
        
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": "river|lake|pond|well|water",
            "key": GOOGLE_MAPS_API_KEY,
            "language": "mr"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        water_resources = []
        for place in data.get('results', []):
            water_resources.append({
                "name": place.get('name', 'अज्ञात'),
                "type": "|".join(place.get('types', [])) if place.get('types') else "अज्ञात",
                "location": place.get('geometry', {}).get('location')
            })

        return jsonify({
            "status": "success",
            "count": len(water_resources),
            "water_resources": water_resources
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/soil-health-centers', methods=['GET'])
def get_soil_health_centers():
    """
    Find soil health centers in Maharashtra
    Parameters (as query params):
    - district: filter by district (optional)
    """
    try:
        district = request.args.get('district', '')
        
        # This would query your database in production
        # Here's a mock implementation with Google Places API
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        query = "soil health center Maharashtra"
        if district:
            query += f" {district}"
            
        params = {
            "query": query,
            "key": GOOGLE_MAPS_API_KEY,
            "language": "mr"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        centers = []
        for place in data.get('results', []):
            centers.append({
                "name": place.get('name'),
                "address": place.get('formatted_address'),
                "location": place.get('geometry', {}).get('location'),
                "rating": place.get('rating')
            })
        
        return jsonify({
            "status": "success",
            "count": len(centers),
            "centers": centers
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
@app.route('/api/nearby-services', methods=['GET'])
def get_nearby_services():
    """
    Find nearby agricultural services
    Parameters (as query params):
    - lat: latitude
    - lng: longitude
    - radius: search radius in meters (default: 5000)
    """
    try:
        lat = request.args.get('lat', '18.5204')  # Default to Pune coordinates
        lng = request.args.get('lng', '73.8567')
        radius = request.args.get('radius', '5000')
        
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": "agriculture|fertilizer|seed|tractor",
            "key": GOOGLE_MAPS_API_KEY,
            "language": "mr"  # Marathi language support
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        simplified_results = []
        for place in data.get('results', []):
            simplified_results.append({
                "name": place.get('name'),
                "address": place.get('vicinity'),
                "type": place.get('types', [])[0] if place.get('types') else "unknown",
                "location": place.get('geometry', {}).get('location')
            })
        
        return jsonify({
            "status": "success",
            "results": simplified_results,
            "count": len(simplified_results)
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
                       
if __name__ == '__main__':
    app.run(debug=True)
    
    