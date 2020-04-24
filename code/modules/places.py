
from .utilities import posix_to_utc, isblank


class Visit:

    def __init__(self, x, owner):
        self.x = x
        self.owner = owner

    @property
    def latitude(self):    
        return self.x['centerLatE7'] / 1E7

    @property
    def longitude(self):    
        return self.x['centerLngE7'] / 1E7
    
    @property
    def gps(self):
        return [self.latitude, self.longitude]

    @property
    def place_id(self):    
        return self.x['location']['placeId']

    @property
    def name(self):        
        return self.x['location']['name']

    @property
    def address(self):    
        if 'address' in self.x['location']:
            return self.x['location']['address']
        else:
            return None

    @property
    def visit_confidence(self):    
        return self.x['visitConfidence']

    @property
    def place_confidence(self):
        return self.x['placeConfidence']

    @property
    def duration(self):    
        return self.time_stop - self.time_start

    @property
    def time_start(self):
        return posix_to_utc(self.x['duration']['startTimestampMs'])

    @property
    def time_stop(self):
        return posix_to_utc(self.x['duration']['endTimestampMs'])

    def to_record(self):
        return {
            'place_id': self.place_id,
            'time_start': self.time_start,
            'time_stop': self.time_stop,
            'owner': self.owner
            }

    @property
    def all_places(self):

        location = Location(self.x['location']).to_json()
        location['address'] = self.address
        locations = [location]
        
        if 'otherCandidateLocations' in self.x.keys():        
            for record in self.x['otherCandidateLocations']:
                location = Location(record).to_json()
                location['address'] = self.address
                locations.append(location)
                    
        return locations


class Location:
    
    def __init__(self, x):
        self.x = x
        
    @property
    def place_id(self):
        return self.x['placeId']
    
    @property
    def name(self):
        if 'name' in self.x.keys():
            return self.x['name']
        else:
            return None
    
    @property
    def latitude(self):
        return self.x['latitudeE7'] / 1E7
    
    @property
    def longitude(self):
        return self.x['longitudeE7'] / 1E7
    
    def to_json(self):
        return {
            'id': self.place_id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude
        }





country_codes = {
        'france': 'FR', 
        'italia': 'IT',
        'italy': 'IT',
        'uk': 'UK', 
        'česko': 'CZ', 
        'deutschland': 'DE',
        'österreich': 'AT',
        'austria' : 'AT',
        'slovenia': 'SI',
        'slovenija': 'SI', 
        'hrvatska': 'HR', 
        'croatia': 'HR', 
        'espanya': 'ES',
        'españa': 'ES',
        'spain': 'ES',
        'المغرب': 'MA', 
        'morocco': 'MA',
        'maroc': 'MA', 
        'usa': 'US'
    }

def get_country_code(country):
    
    if type(country) == str:
        if country not in country_codes.keys():
            return None
        else:
            return country_codes[country]
    else:
        return None


def get_state_code(record):
    if type(record.state) == str:
        return record.state.upper()[:2]
    else:
        return None


def get_city_name(record):
    
    if isblank(record.city):
        
        try:
            if not isblank(record.city_district):
                return record.city_district
            
            if not isblank(record.suburb):
                return record.suburb

            if not isblank(record.state_district):
                return record.state_district
            
            if not isblank(record.house):
                return record.house

        except:
            return None
    
    else:
        return record.city
    
    
def get_location_str(record):
    
    country_code = record.country_code
    if country_code == 'US' and type(record.state) == str:
        country_code = record.state.upper()
    
    if country_code is None or record.city is None:
        return None

    else:
        city = record.city.title()
        return '{:s}, {:s}'.format(city, country_code)
