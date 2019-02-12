import codecs
import re
from geopy.geocoders import ArcGIS
import folium
from geopy.exc import GeocoderTimedOut


def read_file(path):
    # "Read_file" function reads the file with different data and returns the list with elements.
    """

    :param path: str
    :return: list
    """

    list_of_lines = []
    list_of_lines1 = []

    with codecs.open(path, "r", encoding='utf-8', errors='ignore') as file:
        read_from_file = file.readlines()
        counter = 0
        for line in read_from_file:
            counter += 1
            if counter < 15:
                continue
            list_of_lines.append(line.strip("\n").split("\t"))
        for lines in list_of_lines:
            first_element = lines[0]
            result = re.findall(r'\d{4}', first_element)
            if not len(result):
                continue
            last_element = lines[-1]
            if last_element[-1] == ")":
                last_element = lines[-2]
            list_of_lines1.append([result[0], last_element])
    return list_of_lines1


def search_year(list_of_data, year):
    # "Search_a_year" function receive a list with all years, but returns data for only one specified year.
    """

    :param list_of_data: list
    :param year: int
    :return: list
    """
    if type(year) == int:
        lst = [elements for elements in list_of_data if str(year) in elements]
        if len(lst) == 0:
            return "Sorry, but year you chose wasn`t found."
        return lst
    else:
        return "Please, enter other year."


def coordinates(list_of_years_places):
    # "Coordinates" function converts location names to coordinates.
    """

    :param list_of_years_places: list
    :return: list
    """
    locators = ArcGIS()

    for contents in list_of_years_places:
        try:
            location = locators.geocode(contents[1], timeout=100)
        except GeocoderTimedOut:
            continue
        contents[1] = [location.latitude, location.longitude]
    return list_of_years_places


def making_map(list_of_coordinates):
    # "Making_map" function creates a map with layers of this parameters:
    # the places where movies of entered year were shot and the population of countries.
    """

    :param list_of_coordinates: list
    """
    new_map = folium.Map(tiles="Mapbox Control Room", zoom_start=2)
    open_file = open('world.json', 'r', encoding='utf-8-sig').read()
    films_cities = folium.FeatureGroup(name="Films")

    for i in list_of_coordinates:
        films_cities.add_child(
            folium.Marker(location=i[1], icon=folium.features.CustomIcon('clapperboard.png', icon_size=(25, 25))))

    population = folium.FeatureGroup(name="Population")

    def layer_population(x):
        return {'fillColor': 'white' if x['properties']['POP2005'] < 10000000 else 'darkred' if 10000000 <= x
                                                       ['properties']['POP2005'] < 20000000 else 'lightgray'}

    population.add_child(folium.GeoJson(data=open_file, style_function=layer_population))

    area = folium.FeatureGroup(name="Area")

    def layer_area(x):
        return {'fillColor': 'pink' if x['properties']['AREA'] > 250000 else 'red' if 2500 <= x['properties']
                                                                                               ['AREA'] < 50000
                else 'blue'}

    area.add_child(folium.GeoJson(data=open_file, style_function=layer_area))

    new_map.add_child(films_cities)
    new_map.add_child(population)
    new_map.add_child(area)
    new_map.add_child(folium.LayerControl())
    new_map.save('map.html')
    return "Your map are ready."


if __name__ == "__main__":
    result_of_reading_file = read_file("locations.list.txt")
    result_of_searching_year = search_year(result_of_reading_file, 1893)
    result_of_searching_coordinates = coordinates(result_of_searching_year)
    print(making_map(result_of_searching_coordinates))
