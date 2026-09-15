"""
DrishtiSetu — GIS Data & Spatial Conflict Detection (Member 3)
Evaluates candidate relocation sites against eco-sensitive, forest, and protected zones.
"""

from typing import Tuple, Optional, List, Dict, Any

# Bounding polygons for Chamoli District pilot conflict zones (WGS84 EPSG:4326)
PROTECTED_ZONES = [
    {
        "id": "ZONE_NANDA_DEVI_BUFFER",
        "name": "Nanda Devi Biosphere Eco-Sensitive Transition Zone",
        "zone_type": "ECO_SENSITIVE",
        "source": "Forest Survey of India (FSI) & MoEFCC Protected Area Portal 2024",
        "min_lat": 30.470,
        "max_lat": 30.525,
        "min_lon": 79.630,
        "max_lon": 79.730,
        "reason": "Overlaps Nanda Devi Biosphere Eco-Sensitive Buffer Zone. Construction prohibited under Forest Conservation Act 1980.",
    },
    {
        "id": "ZONE_ALAKNANDA_FLOOD_PLAIN",
        "name": "Alaknanda 100-Year High Flood Plain Line",
        "zone_type": "HIGH_FLOOD_LINE",
        "source": "CWC / State Disaster Management Authority River Hazard Mapping",
        "min_lat": 30.520,
        "max_lat": 30.533,
        "min_lon": 79.495,
        "max_lon": 79.520,
        "reason": "Located within active 100-year River Flash Flood Inundation Buffer.",
    },
    {
        "id": "ZONE_RESERVE_FOREST_COMP14",
        "name": "Uttarakhand Forest Dept Reserved Compartment 14",
        "zone_type": "FOREST",
        "source": "Uttarakhand Forest Department Working Plan (Chamoli Division)",
        "min_lat": 30.560,
        "max_lat": 30.590,
        "min_lon": 79.520,
        "max_lon": 79.555,
        "reason": "Designated Reserve Forest Compartment — non-forestry land diversion requires Central MoEFCC clearance.",
    }
]


def point_in_bbox(lat: float, lon: float, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> bool:
    return (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon)


def check_land_use_conflict(latitude: float, longitude: float) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Performs spatial conflict check for a candidate site.
    Returns (has_conflict: bool, reason: Optional[str], zone_name: Optional[str])
    """
    for zone in PROTECTED_ZONES:
        if point_in_bbox(latitude, longitude, zone["min_lat"], zone["max_lat"], zone["min_lon"], zone["max_lon"]):
            return True, zone["reason"], zone["name"]
    return False, None, None


def get_conflict_zones_geojson() -> Dict[str, Any]:
    """
    Generates GeoJSON FeatureCollection of protected land-use conflict zones.
    """
    features = []
    for zone in PROTECTED_ZONES:
        min_lat, max_lat = zone["min_lat"], zone["max_lat"]
        min_lon, max_lon = zone["min_lon"], zone["max_lon"]
        coords = [
            [
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat],
            ]
        ]
        features.append({
            "type": "Feature",
            "id": zone["id"],
            "properties": {
                "name": zone["name"],
                "zone_type": zone["zone_type"],
                "source": zone["source"],
                "reason": zone["reason"],
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": coords
            }
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }
