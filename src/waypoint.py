class Waypoint:
    def __init__(self, latitude, longitude, altitude):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

    def __str__(self):
        return ('Latitude: ' + str(self.latitude)  + ', Longitude: ' + str(self.longitude) + ', Altitude: ' + str(self.altitude))
