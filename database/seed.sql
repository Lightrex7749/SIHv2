-- ==============================================================================
-- DrishtiSetu v2 — PostgreSQL / PostGIS Schema & Pilot District Seed Dataset
-- Pilot District: Chamoli, Uttarakhand (Joshimath, Raini, Helang, Pipalkoti)
-- Reference: DATABASE_SCHEMA.md v2 & DATA_SOURCES.md
-- ==============================================================================

-- Enable PostGIS extension if available
CREATE EXTENSION IF NOT EXISTS postgis;

-- -------------------------------------------------------------
-- 1. habitations
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS habitations (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    population INTEGER NOT NULL,
    vulnerability_score DOUBLE PRECISION NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    relocation_priority VARCHAR(50) NOT NULL,
    elevation DOUBLE PRECISION,
    slope DOUBLE PRECISION,
    rainfall DOUBLE PRECISION,
    historical_events INTEGER DEFAULT 0,
    hazard_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- 2. hazards
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hazards (
    id VARCHAR(50) PRIMARY KEY,
    habitation_id VARCHAR(50) REFERENCES habitations(id) ON DELETE CASCADE,
    hazard_type VARCHAR(100) NOT NULL, -- LANDSLIDE, FLOOD, COASTAL_EROSION, CLOUD_BURST
    severity VARCHAR(50) NOT NULL,
    source VARCHAR(255) NOT NULL,
    event_date DATE,
    description TEXT
);

-- -------------------------------------------------------------
-- 3. disaster_history
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS disaster_history (
    id VARCHAR(50) PRIMARY KEY,
    habitation_id VARCHAR(50) REFERENCES habitations(id) ON DELETE CASCADE,
    hazard_type VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    severity VARCHAR(50) NOT NULL,
    source VARCHAR(255) NOT NULL,
    description TEXT
);

-- -------------------------------------------------------------
-- 4. infrastructure
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS infrastructure (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL, -- HOSPITAL, SCHOOL, ROAD, WATER_SOURCE, SHELTER, HEALTH_CENTER
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    capacity INTEGER
);

-- -------------------------------------------------------------
-- 5. relocation_sites
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS relocation_sites (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    available_area DOUBLE PRECISION NOT NULL,
    estimated_capacity INTEGER NOT NULL,
    hazard_score DOUBLE PRECISION NOT NULL,
    road_access_score DOUBLE PRECISION NOT NULL,
    healthcare_access_score DOUBLE PRECISION NOT NULL,
    water_access_score DOUBLE PRECISION NOT NULL,
    school_access_score DOUBLE PRECISION NOT NULL,
    suitability_score DOUBLE PRECISION NOT NULL,
    land_use_conflict BOOLEAN DEFAULT FALSE,
    land_use_conflict_reason TEXT
);

-- -------------------------------------------------------------
-- 6. cv_detections
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cv_detections (
    id VARCHAR(50) PRIMARY KEY,
    image_id VARCHAR(255) NOT NULL,
    location_id VARCHAR(50),
    hazard_type VARCHAR(100) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    severity VARCHAR(50) NOT NULL,
    model_disclosure TEXT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- 7. risk_assessments
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS risk_assessments (
    id VARCHAR(50) PRIMARY KEY,
    habitation_id VARCHAR(50) REFERENCES habitations(id) ON DELETE CASCADE,
    hazard_score DOUBLE PRECISION NOT NULL,
    vulnerability_score DOUBLE PRECISION NOT NULL,
    historical_score DOUBLE PRECISION NOT NULL,
    infrastructure_score DOUBLE PRECISION NOT NULL,
    overall_score DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    formula_version VARCHAR(50) DEFAULT 'v1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- 8. relocation_recommendations
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS relocation_recommendations (
    id VARCHAR(50) PRIMARY KEY,
    habitation_id VARCHAR(50) REFERENCES habitations(id) ON DELETE CASCADE,
    site_id VARCHAR(50) REFERENCES relocation_sites(id),
    suitability_score DOUBLE PRECISION NOT NULL,
    capacity_available INTEGER NOT NULL,
    recommendation TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'PROPOSED', -- PROPOSED, ACCEPTED, REJECTED, DEFERRED
    estimated_cost BIGINT,
    cost_basis TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- 9A. decision_log (Required v2 Append-Only Audit Trail)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decision_log (
    id VARCHAR(50) PRIMARY KEY,
    habitation_id VARCHAR(50) NOT NULL,
    recommendation_id VARCHAR(50),
    reviewed_by VARCHAR(255) NOT NULL,
    decision VARCHAR(50) NOT NULL, -- ACCEPTED, REJECTED, DEFERRED
    notes TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- 9B. land_use_zones (Land-Use Conflict Layer)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS land_use_zones (
    id VARCHAR(50) PRIMARY KEY,
    zone_type VARCHAR(100) NOT NULL, -- FOREST, ECO_SENSITIVE, EXISTING_SETTLEMENT, PROTECTED
    name VARCHAR(255) NOT NULL,
    source VARCHAR(255) NOT NULL,
    reason TEXT,
    min_lat DOUBLE PRECISION NOT NULL,
    max_lat DOUBLE PRECISION NOT NULL,
    min_lon DOUBLE PRECISION NOT NULL,
    max_lon DOUBLE PRECISION NOT NULL
);

-- ==============================================================================
-- SEED DATA: PILOT DISTRICT (CHAMOLI, UTTARAKHAND)
-- Source: Census of India 2011, SRTM/CartoDEM, IMD Gridded Rainfall, FSI 2024
-- ==============================================================================

-- Habitations
INSERT INTO habitations (id, name, district, state, latitude, longitude, population, vulnerability_score, risk_score, risk_level, relocation_priority, elevation, slope, rainfall, historical_events, hazard_type, description)
VALUES
('H001', 'Joshimath (Sunil Ward)', 'Chamoli', 'Uttarakhand', 30.556, 79.566, 1250, 74.0, 82.5, 'CRITICAL', 'IMMEDIATE', 1890.0, 34.0, 145.0, 5, 'LANDSLIDE', 'Severe land subsidence and active tensile ground fissures along Sunil-Manohar slope.'),
('H002', 'Raini Village (Upper & Lower)', 'Chamoli', 'Uttarakhand', 30.485, 79.702, 420, 81.0, 89.0, 'CRITICAL', 'IMMEDIATE', 2100.0, 38.0, 160.0, 6, 'CLOUD_BURST', 'Rishi Ganga flash flood & glacial lake outburst debris scour path.'),
('H003', 'Helang Habitation', 'Chamoli', 'Uttarakhand', 30.528, 79.510, 890, 68.0, 71.5, 'HIGH', 'SHORT_TERM', 1450.0, 31.0, 130.0, 3, 'LANDSLIDE', 'Debris slide zone near Alaknanda confluence; road undercut vulnerability.'),
('H004', 'Pipalkoti Settlement', 'Chamoli', 'Uttarakhand', 30.430, 79.430, 2400, 42.0, 38.0, 'LOW', 'MONITOR', 1330.0, 12.0, 95.0, 1, 'FLOOD', 'Low-gradient river terrace with established road infrastructure; recipient zone.'),
('H005', 'Dharali Hamlet', 'Chamoli', 'Uttarakhand', 30.510, 79.540, 310, 72.0, 76.0, 'HIGH', 'SHORT_TERM', 1720.0, 33.0, 140.0, 4, 'LANDSLIDE', 'Active scree slope and seepage-induced toe cutting.'),
('H006', 'Gauchar Plateau', 'Chamoli', 'Uttarakhand', 30.290, 79.150, 3800, 30.0, 24.0, 'LOW', 'MONITOR', 800.0, 5.0, 85.0, 0, 'FLOOD', 'Stable alluvial terrace plateau; high safety factor.')
ON CONFLICT (id) DO NOTHING;

-- Relocation Sites
INSERT INTO relocation_sites (id, name, latitude, longitude, available_area, estimated_capacity, hazard_score, road_access_score, healthcare_access_score, water_access_score, school_access_score, suitability_score, land_use_conflict, land_use_conflict_reason)
VALUES
('SITE_DHAK_01', 'Dhak Plateau Safe Terrace (S001)', 30.535, 79.585, 45.0, 1800, 18.0, 85.0, 72.0, 88.0, 75.0, 84.5, FALSE, NULL),
('SITE_PIPALKOTI_NORTH', 'Pipalkoti Upper Tableland (S002)', 30.445, 79.415, 65.0, 2400, 14.0, 92.0, 84.0, 90.0, 82.0, 88.0, FALSE, NULL),
('SITE_NANDA_DEVI_BUFFER', 'Nanda Devi Transition Terrace (S003)', 30.505, 79.660, 50.0, 1400, 22.0, 60.0, 45.0, 70.0, 50.0, 42.0, TRUE, 'Overlaps Nanda Devi Biosphere Eco-Sensitive Buffer Zone. Construction prohibited under Forest Conservation Act 1980.'),
('SITE_GAUCHER_PLATEAU', 'Gauchar Safe Alluvial Terrace (S004)', 30.295, 79.155, 90.0, 3500, 10.0, 95.0, 90.0, 92.0, 88.0, 92.5, FALSE, NULL)
ON CONFLICT (id) DO NOTHING;

-- Land Use Zones (Conflict Detection)
INSERT INTO land_use_zones (id, zone_type, name, source, reason, min_lat, max_lat, min_lon, max_lon)
VALUES
('ZONE_NANDA_DEVI_BUFFER', 'ECO_SENSITIVE', 'Nanda Devi Biosphere Eco-Sensitive Transition Zone', 'Forest Survey of India (FSI) & MoEFCC Protected Area Portal 2024', 'Overlaps Nanda Devi Biosphere Eco-Sensitive Buffer Zone. Construction prohibited under Forest Conservation Act 1980.', 30.470, 30.525, 79.630, 79.730),
('ZONE_ALAKNANDA_FLOOD_PLAIN', 'HIGH_FLOOD_LINE', 'Alaknanda 100-Year High Flood Plain Line', 'CWC / State Disaster Management Authority River Hazard Mapping', 'Located within active 100-year River Flash Flood Inundation Buffer.', 30.520, 30.533, 79.495, 79.520),
('ZONE_RESERVE_FOREST_COMP14', 'FOREST', 'Uttarakhand Forest Dept Reserved Compartment 14', 'Uttarakhand Forest Department Working Plan (Chamoli Division)', 'Designated Reserve Forest Compartment — non-forestry land diversion requires Central MoEFCC clearance.', 30.560, 30.590, 79.520, 79.555)
ON CONFLICT (id) DO NOTHING;

-- Initial Seed Decision Log
INSERT INTO decision_log (id, habitation_id, recommendation_id, reviewed_by, decision, notes, reviewed_at)
VALUES
('LOG_INIT_01', 'H001', 'REC_JOSH_01', 'District Magistrate, Chamoli', 'DEFERRED', 'Initial geological survey requested for Sunil-Manohar slope before final relocation gazette notification.', '2026-09-12T09:30:00Z'),
('LOG_INIT_02', 'H002', 'REC_RAINI_01', 'Director, Uttarakhand SDMA', 'ACCEPTED', 'Approved emergency Phase 1 transit shelter setup at Dhak Plateau for 420 residents.', '2026-09-13T14:15:00Z')
ON CONFLICT (id) DO NOTHING;
