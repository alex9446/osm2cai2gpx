import json
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


GPX_NS = 'http://www.topografix.com/GPX/1/1'
ET.register_namespace('', GPX_NS)


class Location(TypedDict):
    time: int
    latitude: float
    longitude: float
    altitude: float


class Form(TypedDict):
    title: str
    description: str


class Properties(TypedDict):
    name: str
    form: Form
    locations: list[Location]


class Feature(TypedDict):
    properties: Properties


class GeoJSON(TypedDict):
    features: list[Feature]


def tag(name: str) -> str:
    return f'{{{GPX_NS}}}{name}'


def add_element(parent: ET.Element, name: str, value: str) -> None:
    element = ET.SubElement(parent, tag(name))
    element.text = value


def convert_time(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    return dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def convert_geojson_to_gpx(input_file: Path, output_file: Path) -> None:
    with input_file.open(encoding='utf-8') as file:
        data: GeoJSON = json.load(file)

    gpx = ET.Element(
        tag('gpx'), {'version': '1.1', 'creator': 'GeoJSON to GPX'}
    )

    for feature in data['features']:
        properties = feature['properties']
        form = properties['form']

        track = ET.SubElement(gpx, tag('trk'))

        add_element(track, 'name', form['title'])

        if form['description']:
            add_element(track, 'desc', form['description'])

        segment = ET.SubElement(track, tag('trkseg'))

        for location in properties['locations']:
            lat = str(location['latitude'])
            lon = str(location['longitude'])
            latlon = {'lat': lat, 'lon': lon}

            point = ET.SubElement(segment, tag('trkpt'), latlon)
            add_element(point, 'ele', str(location['altitude']))
            add_element(point, 'time', convert_time(location['time']))

    ET.indent(gpx, space='  ')

    ET.ElementTree(gpx).write(
        output_file,
        encoding='utf-8',
        xml_declaration=True
    )


if __name__ == '__main__':
    convert_geojson_to_gpx(Path('percorso.geojson'), Path('percorso.gpx'))
