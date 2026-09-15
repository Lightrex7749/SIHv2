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
    },
    {
        "id": "H007",
        "name": "Saptari Terai Flood Scenario",
        "district": "Saptari",
        "state": "Koshi Province, Nepal",
        "region": "Nepal Terai",
        "latitude": 26.63,
        "longitude": 86.75,
        "population": 980,
        "vulnerability_score": 78.0,
        "risk_score": 79.0,
        "risk_level": "HIGH",
        "relocation_priority": "SHORT_TERM",
        "elevation": 76.0,
        "slope": 2.0,
        "rainfall": 185.0,
        "historical_events": 4,
        "description": "Seeded cross-border flood scenario for testing regional relocation workflows; verify against official incident feeds before operational use.",
        "hazard_type": "FLOOD",
        "data_status": "SCENARIO_SEEDED"
    },
    {
        "id": "H008",
        "name": "Darbhanga Kosi Flood Scenario",
        "district": "Darbhanga",
        "state": "Bihar, India",
        "region": "Bihar",
        "latitude": 26.15,
        "longitude": 85.90,
        "population": 1450,
        "vulnerability_score": 82.0,
        "risk_score": 84.0,
        "risk_level": "CRITICAL",
        "relocation_priority": "IMMEDIATE",
        "elevation": 52.0,
        "slope": 1.5,
        "rainfall": 210.0,
        "historical_events": 5,
        "description": "Seeded Kosi flood scenario for regional decision-support testing; connect official flood and shelter feeds for live deployment.",
        "hazard_type": "FLOOD",
        "data_status": "SCENARIO_SEEDED"
    },
    {
        "id": "H009",
        "name": "Dhemaji Brahmaputra Flood Scenario",
        "district": "Dhemaji",
        "state": "Assam, India",
        "region": "Assam",
        "latitude": 27.48,
        "longitude": 94.58,
        "population": 1180,
        "vulnerability_score": 80.0,
        "risk_score": 81.0,
        "risk_level": "HIGH",
        "relocation_priority": "SHORT_TERM",
        "elevation": 102.0,
        "slope": 2.5,
        "rainfall": 225.0,
        "historical_events": 6,
        "description": "Seeded Brahmaputra flood scenario for regional workflow testing; verify current conditions with official Assam alerts before action.",
        "hazard_type": "FLOOD",
        "data_status": "SCENARIO_SEEDED"
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
    },
    {
        "site_id": "S005",
        "name": "Rajbiraj Raised Community Terrace",
        "region": "Nepal Terai",
        "latitude": 26.54,
        "longitude": 86.75,
        "elevation": 92.0,
        "available_area": 42000.0,
        "estimated_capacity": 1800,
        "hazard_score": 18.0,
        "road_access_score": 78.0,
        "healthcare_access_score": 70.0,
        "water_access_score": 82.0,
        "school_access_score": 76.0,
        "suitability_score": 80.0,
        "description": "Seeded raised-terrain candidate for Nepal Terai flood scenario demonstrations; validate land and shelter availability before use."
    },
    {
        "site_id": "S006",
        "name": "Darbhanga Elevated Relief Campus",
        "region": "Bihar",
        "latitude": 26.17,
        "longitude": 85.89,
        "elevation": 66.0,
        "available_area": 50000.0,
        "estimated_capacity": 2200,
        "hazard_score": 20.0,
        "road_access_score": 84.0,
        "healthcare_access_score": 80.0,
        "water_access_score": 86.0,
        "school_access_score": 82.0,
        "suitability_score": 83.0,
        "description": "Seeded elevated candidate for Bihar flood scenario demonstrations; verify drainage, access, and land-use status before use."
    },
    {
        "site_id": "S007",
        "name": "Dhemaji Raised Relief Zone",
        "region": "Assam",
        "latitude": 27.47,
        "longitude": 94.55,
        "elevation": 125.0,
        "available_area": 46000.0,
        "estimated_capacity": 1900,
        "hazard_score": 22.0,
        "road_access_score": 76.0,
        "healthcare_access_score": 72.0,
        "water_access_score": 80.0,
        "school_access_score": 74.0,
        "suitability_score": 79.0,
        "description": "Seeded raised candidate for Assam flood scenario demonstrations; verify embankment, drainage, and shelter readiness before use."
    }
]

# Source-attributed reference points for map context. These are not additional
# model scores; they identify locations and datasets that should be checked
# before an authority uses the decision engine operationally.
FLOOD_REFERENCE_POINTS = [
    {
        "id": "FREF-NPL-01",
        "name": "Rasuwagadhi / Upper Trishuli",
        "country": "Nepal",
        "region": "Nepal Flood 2026",
        "latitude": 28.283,
        "longitude": 85.379,
        "hazard_type": "FLOOD",
        "event_date": "2026-08-27",
        "data_status": "SOURCE_ATTRIBUTED_REFERENCE",
        "source_name": "HDX / HOT Nepal Flood 2026 Flood Affected Area",
        "source_url": "https://data.humdata.org/dataset/hot_flood_npl",
    },
    {
        "id": "FREF-NPL-02",
        "name": "Nuwakot Trishuli Corridor",
        "country": "Nepal",
        "region": "Nepal Flood 2026",
        "latitude": 27.916,
        "longitude": 85.166,
        "hazard_type": "FLOOD",
        "event_date": "2026-08-27",
        "data_status": "SOURCE_ATTRIBUTED_REFERENCE",
        "source_name": "HDX / HOT Nepal Flood 2026 River Corridor",
        "source_url": "https://data.humdata.org/dataset/hot_flood_npl_corridor",
    },
    {
        "id": "FREF-NPL-03",
        "name": "Devghat / Narayani Confluence",
        "country": "Nepal",
        "region": "Nepal Flood 2026",
        "latitude": 27.735,
        "longitude": 84.438,
        "hazard_type": "FLOOD",
        "event_date": "2026-08-27",
        "data_status": "SOURCE_ATTRIBUTED_REFERENCE",
        "source_name": "HDX / HOT Nepal Flood 2026 River Corridor",
        "source_url": "https://data.humdata.org/dataset/hot_flood_npl_corridor",
    },
    {
        "id": "FREF-IND-BR-01",
        "name": "Darbhanga / Kosi Basin Reference",
        "country": "India",
        "region": "Bihar",
        "latitude": 26.154,
        "longitude": 85.891,
        "hazard_type": "FLOOD",
        "event_date": None,
        "data_status": "ADMINISTRATIVE_REFERENCE",
        "source_name": "OpenStreetMap place reference; live flood status not asserted",
        "source_url": "https://www.openstreetmap.org/#map=10/26.154/85.891",
    },
    {
        "id": "FREF-IND-AS-01",
        "name": "Dibrugarh / Brahmaputra Plain Reference",
        "country": "India",
        "region": "Assam",
        "latitude": 27.472,
        "longitude": 94.912,
        "hazard_type": "FLOOD",
        "event_date": "2018-06-15",
        "data_status": "SOURCE_ATTRIBUTED_REFERENCE",
        "source_name": "UNITAR-UNOSAT satellite-detected waters in Assam and Northeast India",
        "source_url": "https://unosat-maps.web.cern.ch/unosat-maps/BD/FL20180619BGD/",
    },
]

FLOOD_REFERENCE_AREAS = [
    {
        "id": "FAREA-NPL-2026",
        "name": "Nepal Flood 2026 observed extent (source bounding box)",
        "source_name": "HDX / HOT Nepal Flood 2026 Flood Affected Area",
        "source_url": "https://data.humdata.org/dataset/hot_flood_npl",
        "data_status": "SOURCE_BBOX_VISUALIZATION",
        "event_date": "2026-08-27",
        "bbox": [
            [27.795150, 84.556395],
            [27.795150, 85.379843],
            [28.280699, 85.379843],
            [28.280699, 84.556395],
            [27.795150, 84.556395],
        ],
    },
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


def get_flood_reference_points() -> List[Dict[str, Any]]:
    return FLOOD_REFERENCE_POINTS


def get_flood_reference_areas() -> Dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": area["id"],
                "properties": {key: value for key, value in area.items() if key != "bbox"},
                "geometry": {"type": "Polygon", "coordinates": [[
                    [longitude, latitude] for latitude, longitude in area["bbox"]
                ]]},
            }
            for area in FLOOD_REFERENCE_AREAS
        ],
    }


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
                    "region": h.get("region", "Chamoli"),
                    "data_status": h.get("data_status", "PILOT_SEEDED"),
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
                    "region": s.get("region", "Chamoli"),
                    "data_status": s.get("data_status", "SCENARIO_SEEDED"),
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
