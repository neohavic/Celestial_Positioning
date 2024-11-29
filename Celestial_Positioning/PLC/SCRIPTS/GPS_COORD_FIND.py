import pyads
import geocoder
from geopy.geocoders import ArcGIS
import datetime
import pytz
import tzlocal
import requests
import time
import serial

ser = serial.Serial('COM3', 9600, timeout=1)

# Get GPS cordinates of current IP location
nom = ArcGIS()
g = geocoder.ip('me')
location = nom.geocode(g)

# Convert the offset to a timezone identifier (not always accurate)
timezone_identifier = tzlocal.get_localzone()
tz_utc = pytz.timezone(str(timezone_identifier)).localize(datetime.datetime.now()).strftime('%z')
tz_utc = str(tz_utc)[:-2]

# Get altitude data from latitude and longitude
lat, lon = (location.latitude, location.longitude)
url = f"https://api.opentopodata.org/v1/aster30m?locations={lat},{lon}"
r = requests.get(url)
data = r.json()
elevation = data['results'][0]['elevation']

latitude = location.latitude
longitude = location.longitude
altitude = location.altitude

# Try to establish connection to HPT Teststand at known NetID; If unable, print error to console and exit
AMSAddr = "192.168.1.16.1.1"
Port = 851
try:
    print("Connecting to TwinCAT...")
    plc = pyads.Connection(AMSAddr, Port)
    plc.open()
    print("Local address: " + str(plc.get_local_address()) + "\n")
    print("CONNECTED TO TWINCAT")
except:
    print("Could not connect to hardpoint teststand.\n Check that the NetID of the local machine is entered correctly.\n Now exiting.")

print("latitude = " + str(latitude))
print("longitude = " + str(longitude))
print("Elevation = " + str(elevation))
print("Timezone UTC = " + str(tz_utc))

plc.write_by_name("MAIN.fbSPA.fLatitude", latitude)
plc.write_by_name("MAIN.fbSPA.fLongitude", longitude)
plc.write_by_name("MAIN.fbSPA.fElevation", elevation)
plc.write_by_name("MAIN.fbSPA.fTimezone", int(tz_utc))
go = True
plc.write_by_name("MAIN.go", go)