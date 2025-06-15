from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime

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

if __name__ == '__main__':
    app.run(debug=True)
    
    