"""
DrishtiSetu — GIS Data Service (Member 3)
GeoJSON layer providers and spatial datasets for Chamoli Pilot District, Uttarakhand.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .conflict import check_land_use_conflict, get_conflict_zones_geojson


# Habitations in Pilot District (Chamoli, Uttarakhand)
HABITATIONS_DATA = [
    {
        "id": "H001",
        "name": "Joshimath (Sunil Ward)",
        "district": "Chamoli",
        "state": "Uttarakhand",
        "latitude": 30.556,
        "longitude": 79.566,
        "population": 1250,
        "vulnerability_score": 74.0,
        "risk_score": 82.5,
        "risk_level": "CRITICAL",
        "relocation_priority": "IMMEDIATE",
        "elevation": 1890.0,
        "slope": 34.0,
        "rainfall": 145.0,
        "historical_events": 5,
        "description": "Severe land subsidence and continuous tension fissures affecting 180+ masonry structures along Sunil-Manohar slope.",
        "hazard_type": "LANDSLIDE"
    },
    {
        "id": "H002",
        "name": "Raini Village (Upper & Lower)",
        "district": "Chamoli",
        "state": "Uttarakhand",
        "latitude": 30.485,
        "longitude": 79.702,
        "population": 420,
        "vulnerability_score": 81.0,
        "risk_score": 89.0,
        "risk_level": "CRITICAL",
        "relocation_priority": "IMMEDIATE",
        "elevation": 2100.0,
        "slope": 38.0,
        "rainfall": 160.0,
        "historical_events": 6,
        "description": "Rishi Ganga flash flood & glacial lake outburst debris scour path; vulnerable alluvial-colluvial toe scarp.",
        "hazard_type": "CLOUD_BURST"
    },
    {
        "id": "H003",
        "name": "Helang Habitation",
        "district": "Chamoli",
        "state": "Uttarakhand",
        "latitude": 30.528,
        "longitude": 79.510,
        "population": 890,
        "vulnerability_score": 68.0,
        "risk_score": 71.5,
        "risk_level": "HIGH",
        "relocation_priority": "SHORT_TERM",
        "elevation": 1450.0,
        "slope": 28.0,
        "rainfall": 125.0,
        "historical_events": 3,
        "description": "Active road-cut slope failure and rockfall hazards along Badrinath National Highway bypass.",
        "hazard_type": "LANDSLIDE"
    },
    {
        "id": "H004",
        "name": "Pipalkoti Settlement",
        "district": "Chamoli",
        "state": "Uttarakhand",
        "latitude": 30.430,
        "longitude": 79.430,
        "population": 1600,
        "vulnerability_score": 45.0,
        "risk_score": 48.0,
        "risk_level": "MODERATE",
        "relocation_priority": "LONG_TERM",
        "elevation": 1260.0,
        "slope": 18.0,
        "rainfall": 95.0,
        "historical_events": 1,
        "description": "Moderate river terrace terrain with minor gully erosion.",
        "hazard_type": "FLOOD"
    },
    {
        "id": "H005",
        "name": "Ghat Habitation",
        "district": "Chamoli",
        "state": "Uttarakhand",
        "latitude": 30.260,
        "longitude": 79.450,
        "population": 1100,
        "vulnerability_score": 48.0,
        "risk_score": 52.0,
        "risk_level": "MODERATE",
        "relocation_priority": "LONG_TERM",
        "elevation": 1180.0,
        "slope": 22.0,
        "rainfall": 110.0,
        "historical_events": 2,
        "description": "Nandakini river tributary junction with seasonal monsoon toe erosion.",
        "hazard_type": "FLOOD"
    },
    {
        "id": "H006",
        "name": "Urgam Valley Hamlet",
        "district": "Chamoli",
        "state": "Uttarakhand",
        "latitude": 30.575,
        "longitude": 79.490,
        "population": 310,
        "vulnerability_score": 64.0,
        "risk_score": 66.0,
        "risk_level": "HIGH",
        "relocation_priority": "SHORT_TERM",
        "elevation": 2250.0,
        "slope": 31.0,
        "rainfall": 130.0,
        "historical_events": 3,
        "description": "Isolated high altitude agrarian settlement vulnerable to road cutoffs during heavy precipitation.",
        "hazard_type": "LANDSLIDE"
    }
]

# Candidate Relocation Sites (with land-use conflict evaluation)
CANDIDATE_SITES_DATA = [
    {
        "site_id": "S001",
        "name": "Dhak Plateau Safe Terrace",
        "latitude": 30.535,
        "longitude": 79.585,
        "elevation": 1800.0,
        "available_area": 45000.0,
        "estimated_capacity": 1800,
        "hazard_score": 18.0,
        "road_access_score": 85.0,
        "healthcare_access_score": 75.0,
        "water_access_score": 90.0,
        "school_access_score": 80.0,
        "suitability_score": 84.5,
        "description": "Gentle, stable quartz-mica schist plateau with deep soil mantle and natural drainage away from scarp."
    },
    {
        "site_id": "S002",
        "name": "Pipalkoti Upper Tableland",
        "latitude": 30.445,
        "longitude": 79.415,
        "elevation": 1320.0,
        "available_area": 60000.0,
        "estimated_capacity": 2400,
        "hazard_score": 12.0,
        "road_access_score": 92.0,
        "healthcare_access_score": 88.0,
        "water_access_score": 92.0,
        "school_access_score": 86.0,
        "suitability_score": 88.0,
        "description": "Expansive non-flood terrace with established access roads and municipal grid connectivity."
    },
    {
        "site_id": "S003",
        "name": "Nanda Devi Buffer Ridge Site (Protected Area)",
        "latitude": 30.505,
        "longitude": 79.660,
        "elevation": 2150.0,
        "available_area": 35000.0,
        "estimated_capacity": 1400,
        "hazard_score": 35.0,
        "road_access_score": 45.0,
        "healthcare_access_score": 30.0,
        "water_access_score": 60.0,
        "school_access_score": 35.0,
        "suitability_score": 42.0,
        "description": "High ridge terrain within ecologically protected biosphere transition zone."
    },
    {
        "site_id": "S004",
        "name": "Gauchar Safe Alluvial Terrace",
        "latitude": 30.285,
        "longitude": 79.155,
        "elevation": 820.0,
        "available_area": 75000.0,
        "estimated_capacity": 3000,
        "hazard_score": 10.0,
        "road_access_score": 95.0,
        "healthcare_access_score": 92.0,
        "water_access_score": 90.0,
        "school_access_score": 90.0,
        "suitability_score": 91.0,
        "description": "Wide, flat airstrip-adjacent alluvial terrace with robust disaster logistics access."
    }
]


def get_habitations() -> List[Dict[str, Any]]:
    return HABITATIONS_DATA


def get_habitation_by_id(habitation_id: str) -> Optional[Dict[str, Any]]:
    for h in HABITATIONS_DATA:
        if h["id"].upper() == habitation_id.upper():
            return h
    return None


def get_relocation_sites() -> List[Dict[str, Any]]:
    """Returns candidate sites enriched with land_use_conflict assessment."""
    enriched = []
    for site in CANDIDATE_SITES_DATA:
        has_conflict, reason, _ = check_land_use_conflict(site["latitude"], site["longitude"])
        item = dict(site)
        item["land_use_conflict"] = has_conflict
        item["land_use_conflict_reason"] = reason
        enriched.append(item)
    return enriched


def get_layer_geojson(layer_name: str) -> Dict[str, Any]:
    norm_name = layer_name.lower().replace("_", "-")

    if norm_name in ["habitations", "habitation"]:
        features = []
        for h in HABITATIONS_DATA:
            features.append({
                "type": "Feature",
                "id": h["id"],
                "properties": {
                    "name": h["name"],
                    "district": h["district"],
                    "state": h["state"],
                    "population": h["population"],
                    "risk_score": h["risk_score"],
                    "risk_level": h["risk_level"],
                    "vulnerability_score": h["vulnerability_score"],
                    "relocation_priority": h["relocation_priority"],
                    "hazard_type": h.get("hazard_type", "MULTI_HAZARD"),
                    "description": h.get("description", ""),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [h["longitude"], h["latitude"]]
                }
            })
        return {"type": "FeatureCollection", "features": features}

    elif norm_name in ["red-zones", "red_zones", "hazards"]:
        # GeoJSON Polygons demarcating Chamoli high-risk Red Zones
        features = [
            {
                "type": "Feature",
                "id": "RZ_JOSHIMATH",
                "properties": {
                    "name": "Joshimath Slope Subsidence Red Zone",
                    "hazard_type": "LANDSLIDE",
                    "severity": "CRITICAL",
                    "area_sq_km": 2.8,
                    "warning": "Active slope creep, tension fissures, ground deformation exceeding 5cm/month."
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [79.545, 30.540],
                        [79.585, 30.542],
                        [79.580, 30.570],
                        [79.540, 30.565],
                        [79.545, 30.540]
                    ]]
                }
            },
            {
                "type": "Feature",
                "id": "RZ_RAINI",
                "properties": {
                    "name": "Raini Gorge Debris Surge Red Zone",
                    "hazard_type": "CLOUD_BURST",
                    "severity": "CRITICAL",
                    "area_sq_km": 4.1,
                    "warning": "Steep talus slope with high susceptibility to moraine-dam breach and debris flows."
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [79.680, 30.470],
                        [79.725, 30.475],
                        [79.720, 30.505],
                        [79.675, 30.495],
                        [79.680, 30.470]
                    ]]
                }
            }
        ]
        return {"type": "FeatureCollection", "features": features}

    elif norm_name in ["relocation-sites", "relocation_sites", "sites"]:
        sites = get_relocation_sites()
        features = []
        for s in sites:
            features.append({
                "type": "Feature",
                "id": s["site_id"],
                "properties": {
                    "name": s["name"],
                    "available_area": s["available_area"],
                    "estimated_capacity": s["estimated_capacity"],
                    "suitability_score": s["suitability_score"],
                    "hazard_score": s["hazard_score"],
                    "road_access_score": s["road_access_score"],
                    "healthcare_access_score": s["healthcare_access_score"],
                    "land_use_conflict": s["land_use_conflict"],
                    "land_use_conflict_reason": s.get("land_use_conflict_reason"),
                    "description": s.get("description", "")
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [s["longitude"], s["latitude"]]
                }
            })
        return {"type": "FeatureCollection", "features": features}

    elif norm_name in ["land-use-conflict", "land_use_conflict", "land-use-zones", "land_use_zones"]:
        return get_conflict_zones_geojson()

    else:
        return {"type": "FeatureCollection", "features": []}


def get_risk_layers_manifest() -> Dict[str, Any]:
    """Returns layer catalog as per API_CONTRACT.md section 5"""
    return {
        "layers": [
            {"name": "red_zones", "type": "geojson", "url": "/api/v1/gis/layers/red-zones"},
            {"name": "habitations", "type": "geojson", "url": "/api/v1/gis/layers/habitations"},
            {"name": "relocation_sites", "type": "geojson", "url": "/api/v1/gis/layers/relocation-sites"},
            {"name": "land_use_conflict", "type": "geojson", "url": "/api/v1/gis/layers/land-use-conflict"}
        ]
    }
