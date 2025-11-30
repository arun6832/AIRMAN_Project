import os
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
def fetch_metar_decoded(icao):
    icao = (icao or '').strip().upper()
    if not icao:
        return {'error':'no_icao'}
    # demo fallback
    return {
        'raw': None,
        'wind_dir': 210,
        'wind_speed_kt': 12,
        'visibility_km': 6.0,
        'clouds': [{'amount':'SCT','base_ft_agl':1800}],
        'conditions': ''
    }
