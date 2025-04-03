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
TTC_CONNECTIONS_PATH = "./connectingRoutes.json"
MAX_DISTANCE = 0.25

def get_routes_list() -> list:
    """Return a list of all TTC routes as their tags as strings."""
    print("SUBTASK: Getting list of TTC routes")

    routes = []
    req = requests.get(API_ROUTE_LIST).json()
    for route in req["route"]:
        routes.append(route["tag"])

    print("SUBTASK COMPLETE: Retrieved a list of all TTC routes as TTC objects")
    return routes


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


def get_routes_within_extent(route_num:str) -> list:
    """
    Return a list of TTC routes within the extent of 'route'\n
    Requires routeInfo.json. \n
    route: tag of TTC route 
    """
    with open(TTC_ROUTE_INFO_PATH, 'r') as route_info_json:
        data = json.load(route_info_json)

    t_route = data["routeInfo"][route_num]

    extent_routes = []
    for tag in data["routeInfo"]:
        route = data["routeInfo"][tag]
        print(route["tag"])
        if route["tag"] != t_route["tag"] and has_intersection(t_route["latMin"], t_route["latMax"], t_route["lonMin"], t_route["lonMax"],
                            route["latMin"], route["latMax"], route["lonMin"], route["lonMax"]):
            extent_routes.append(route["tag"])
    return extent_routes
    

def sort_string_integers(string_integers:list) -> list:
    """
    Return 'string_integers' sorted by their value in integers as a list of strings.
    """
    temp_ints = []
    for string in string_integers:
        temp_ints.append(int(string))
    temp_ints.sort()
    string_integers.clear()
    for integer in temp_ints:
        string_integers.append(str(integer))
    return string_integers
    

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
    route_nums = get_routes_list()

    ### Create json of routes with route config information
    data = {"date": str(datetime.now())}
    inner_data = {}

    for route_num in route_nums:
        req = requests.get(API_ROUTE_CONFIG + route_num).json()
        inner_data.update(
            {
                req["route"]["tag"] : req["route"]
            }
        )
        print(f'INFO: {req["route"]["title"]} retrieved')
        time.sleep(0.25) # To not surpass the limit of 10MB/10sec
    data.update({"routeInfo":inner_data})

    with open(TTC_ROUTE_INFO_PATH, 'w') as route_info_json:
        json.dump(data, route_info_json)
    
    print("TASK COMPLETE: Generated routeInfo.json")


def generate_connecting_routes_json() -> None:
    """Generate a JSON file containing all the connecting TTC routes per route."""
    print("TASK: Generating connectingRoutes.json")

    with open(TTC_ROUTE_INFO_PATH, 'r') as route_info_json:
        data = json.load(route_info_json)

    ### Get list of all routes
    all_routes = get_routes_list()
    
    for tag_i in all_routes:
        t_route = data[tag_i]
        for tag_j in data:
            route = data[tag_j]
            if route["tag"] != t_route["tag"] and has_intersection(t_route["latMin"], t_route["latMax"], t_route["lonMin"], t_route["lonMax"],
                            route["latMin"], route["latMax"], route["lonMin"], route["lonMax"]):
                connecting_routes = []
                for t_stop in t_route["stop"]:
                    t_latlon = LatLon(Latitude(t_stop["lat"]), Longitude(t_stop["lon"]))
                    for tag_k in data:
                        for stop in data[tag_k]["stop"]:
                            latlon = LatLon(Latitude(stop["lat"]), Longitude(stop["lon"]))
                            if (tag_k not in connecting_routes) and (t_latlon.distance(latlon) < MAX_DISTANCE):
                                connecting_routes.append(tag_k)
                print(connecting_routes)
        

    ### Get list of connecting stops from list of routes within
    
            


    ### Check route criteria:
    # fits within the extent of target route
    # then check every stop if it is within 400m of that target stop



if __name__ == "__main__":
    print('hello')
    # generate_routes_json()
    # generate_route_info_json()
    # print(sort_string_integers(["2", "1", "301", "901", "10"]))
    # print(routes_within_extent("68"))
    # print(routes_within_extent("68"))
    generate_connecting_routes_json()
