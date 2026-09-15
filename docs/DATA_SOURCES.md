# Data Sources (v2)

## Purpose

This document records all external and prepared datasets used by DrishtiSetu. **This file must be filled in with actual sources before the final presentation — it may not remain a category list.**

For every dataset record:

* Dataset name
* Organization/source
* URL
* Geographic coverage
* Variables
* File format
* Date/version
* License/usage restrictions
* Preprocessing performed
* Intended module

---

## Recommended Real Sources (use these as your starting point — verify access/license before final submission)

| Category | Dataset | Organization | Notes |
|---|---|---|---|
| Rainfall | Gridded rainfall data | India Meteorological Department (IMD) | Daily/monthly gridded rainfall, public research use |
| Elevation / Slope | CartoDEM / Bhoonidhi, or SRTM DEM | ISRO / USGS | Derive slope via GeoPandas/rasterio from DEM |
| Landslide susceptibility | Landslide Susceptibility Zonation | Geological Survey of India (GSI) | State-level susceptibility maps, some published as reports/atlases |
| Flood extent / forecasting | Flood forecasting data | Central Water Commission (CWC) | Station-level flood forecast data |
| Flood/coastal imagery | Bhuvan flood/coastal layers | ISRO Bhuvan | WMS layers usable as basemap overlays |
| Coastal erosion | Shoreline change data | National Centre for Coastal Research (NCCR) | Shoreline change atlases by state |
| Population | Census of India 2011 (or SECC) | Registrar General of India | Village/town-level population, publicly downloadable |
| Population (gridded alt.) | WorldPop gridded population | WorldPop.org | Useful if village-level census data is hard to match to coordinates |
| Roads / buildings / water bodies | OpenStreetMap extract | OSM / Overpass API | Free, needs light cleaning |
| Administrative boundaries | State/district boundaries | Survey of India / Bhuvan | For consistent admin-unit joins |
| Forest cover / eco-sensitive zones | Forest Cover / ESZ layers | Forest Survey of India (FSI) / MoEFCC | Used for the land-use conflict check |
| Disaster management guidance (RAG) | NDMA Guidelines, National Disaster Management Plan | NDMA | Public PDFs, ideal RAG corpus |
| R&R policy | State/national Rehabilitation & Resettlement guidelines | State SDMA / MoRD | Grounds relocation reasoning in real policy |

**Minimum bar for the hackathon submission:** pick ONE pilot district, download real extracts for at least rainfall, elevation/slope, population, and admin boundaries for that district, and seed the demo database with them. Everything outside the pilot district can remain clearly labeled synthetic.

---

## Data Categories (original structure retained)

### Hazard Data
Rainfall, flood extent, landslide susceptibility, elevation, slope, coastal erosion, historical disaster events.

### Population/Vulnerability Data
Population, population density, demographic vulnerability indicators, accessibility, infrastructure availability.

### Geospatial Data
Roads, buildings, rivers, settlements, hospitals, schools, water sources, administrative boundaries, **forest cover/eco-sensitive zones (new — required for land-use conflict check)**.

### Disaster Management Documents (RAG)
Preferred sources: government authorities (NDMA, state SDMAs), disaster-management organizations, official guidelines, research institutions, peer-reviewed publications, international organizations (UNDRR, etc.).

---

## Scoring Methodology (NEW — required, referenced by API_CONTRACT.md §3A)

Document here:

1. The exact weights (`w1..w4`, `v1..v3`, `α/β/γ`) used in the hazard/vulnerability/overall formula (see ARCHITECTURE.md §9D).
2. Their source — either a cited real framework (e.g., NDMA Hazard Vulnerability Risk Assessment methodology, INFORM Risk Index structure) or your own documented AHP pairwise-comparison process.
3. Version history if weights change during development (`formula_version` field in `risk_assessments` table must match).

Never leave this section blank — an unexplained score is the single most common reason judges distrust an ML-scored hackathon system.

---

## Cost Benchmark (NEW — supports `estimated_cost` field)

Document the per-capita resettlement cost benchmark used (e.g., a published R&R policy compensation rate, or a clearly labeled illustrative estimate) and cite its source. If no reliable benchmark is available, mark `estimated_cost` as `null` and state this limitation openly rather than inventing a number.

---

## Data Integrity Rules

Never present:

* Mock data as real data
* Estimated values as official values
* Synthetic values as government statistics

Clearly label synthetic/demo data (recommended convention: `source = 'SYNTHETIC_DEMO'` on any seeded row that isn't from a real dataset).

All important data sources must be documented before being used in the final presentation.
