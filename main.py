import json
import requests
import time
from datetime import datetime
from latloncalc.latlon import LatLon, Latitude, Longitude
from shapely.geometry import Polygon

API_ROUTE_CONFIG = "https://retro.umoiq.com/service/publicJSONFeed?command=routeConfig&a=ttc&r="
API_ROUTE_LIST = "https://retro.umoiq.com/service/publicJSONFeed?command=routeList&a=ttc"
TTC_ROUTE_INFO_PATH = "./routeInfo.json"
TTC_ROUTES_PATH = "./routes.json"
MAX_DISTANCE = 0.25

def generate_routes_json() -> None:
    """Generate a list of all TTC routes in a JSON file."""
    print("TASK: Generating routes.json")

    routes = []
    req = requests.get(API_ROUTE_LIST).json()

    for route in req["route"]:
        routes.append(route)

    data = {"date":str(datetime.now()),"routes":routes}

    with open(TTC_ROUTES_PATH, 'w') as routes_json:
        json.dump(data, routes_json)
        print("TASK COMPLETE: Generated routes.json")


def generate_route_info_json() -> None:
    """Generate a JSON file. Contents are all the TTC routes as JSON objects.
    """
    print("TASK: Generating routeInfo.json")

    ### Get list of routes
    route_nums = []
    req = requests.get(API_ROUTE_LIST).json()
    for route in req["route"]:
        route_nums.append(route["tag"])

    ### Create json of routes with route config information
    data = {"date": str(datetime.now())}

    for route_num in route_nums:
        req = requests.get(API_ROUTE_CONFIG + route_num).json()
        data.update(
            {
                req["route"]["tag"] : req["route"]
            }
        )
        print(f'INFO: {req["route"]["title"]} retrieved')
        time.sleep(0.25) # To not surpass the limit of 10MB/10sec

    with open(TTC_ROUTE_INFO_PATH, 'w') as route_info_json:
        json.dump(data, route_info_json)
    
    print("TASK COMPLETE: Generated routeInfo.json")
   

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

    print(len(connectingRoutes))


    ### Check route criteria:
    # fits within the extent of target route
    # then check every stop if it is within 400m of that target stop



if __name__ == "__main__":
    print('hello')
    # generate_routes_json()
    generate_route_info_json()