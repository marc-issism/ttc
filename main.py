import json
import requests
import time
from latloncalc.latlon import LatLon, Latitude, Longitude
from shapely.geometry import Polygon

API_ROUTE_CONFIG = "https://retro.umoiq.com/service/publicJSONFeed?command=routeConfig&a=ttc&r="
API_ROUTE_LIST = "https://retro.umoiq.com/service/publicJSONFeed?command=routeList&a=ttc"
TTC_JSON_PATH = "./ttc.json"
TTC_CONNECTIONS_PATH = "./connections.json"
MAX_DISTANCE = 0.25

def get_route_list_json() -> None:
    """Create or write to a JSON file. Contents are all the TTC routes as JSON objects.
    """

    ### Get list of routes
    route_nums = []
    request = requests.get(API_ROUTE_LIST).json()
    for route in request["route"]:
        route_nums.append(route["tag"])
    print(route_nums)


    ### Create json of routes with route config information
    data = {}

    for route_num in route_nums:
        request = requests.get(API_ROUTE_CONFIG + route_num).json()
        print(request["route"]["title"])
        data.update(
            {
                request["route"]["tag"] : request["route"]
            }
        )
        time.sleep(0.25)


    with open(TTC_JSON_PATH, 'w') as ttc:
        json.dump(data, ttc)
   

def has_intersection(t_latMin:float, t_latMax:float, t_lonMin:float, t_lonMax:float,
                     latMin:float, latMax:float, lonMin:float, lonMax:float) -> bool:
    """Return True if the target rectangle intersects with another given rectangle
    given the four sides of each rectangle."""

    t_rect = Polygon([
        (t_lonMin, t_latMax),
        (t_lonMax, t_latMax),
        (t_lonMax, t_latMin),
        (t_lonMin, t_latMin)
    ])

    rect = Polygon([
        (lonMin, latMax),
        (lonMax, latMax),
        (lonMax, latMin),
        (lonMin, latMin)
    ])

    return t_rect.intersects(rect)
    
    
def get_connecting_routes(route_num:str) -> None:
    """Append to a list of 'connectingStops' for the given 'route_num' TTC object."""



    with open(TTC_JSON_PATH, 'r') as ttc:
        data = json.load(ttc)

    t_route = data[route_num] 

    ### Get list of routes within extent of target route
    routes = []
    for tag in data:
        route = data[str(tag)]
        if str(tag) != route_num and has_intersection(t_route["latMin"], t_route["latMax"], t_route["lonMin"], t_route["lonMax"],
                            route["latMin"], route["latMax"], route["lonMin"], route["lonMax"]):
            routes.append(route["tag"])

    ### Get list of connecting stops from list of routes within
    connectingRoutes = []

    for t_stop in data[route_num]["stop"]:
        t_latlon = LatLon(Latitude(t_stop["lat"]), Longitude(t_stop["lon"]))
        for tag in routes:
            for stop in data[tag]["stop"]:
                latlon = LatLon(Latitude(stop["lat"]), Longitude(stop["lon"]))
                if (tag not in connectingRoutes) and (t_latlon.distance(latlon) < MAX_DISTANCE):
                    connectingRoutes.append(tag)
            

    with open(TTC_CONNECTIONS_PATH, 'r') as connections:
        data = json.load(connections)

    connectingRoutes.sort()
    data.update({route_num : connectingRoutes})

    with open(TTC_CONNECTIONS_PATH, 'w') as connections:
        json.dump(data, connections)

    print(routes)

    # for t_stop in t_route["stop"]:
    #     print(t_stop)

    a = LatLon(Latitude(43.7331599), Longitude(-79.45294))
    b = LatLon(Latitude(43.7372999), Longitude(-79.43323))
    print(a.distance(b))
    print(len(connectingRoutes))


    ### Check route criteria:
    # fits within the extent of target route
    # then check every stop if it is within 400m of that target stop



if __name__ == "__main__":
    print('hello')
    get_connecting_routes("68")