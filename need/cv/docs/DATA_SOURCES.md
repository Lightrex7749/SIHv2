# Data Sources (v2)

## Purpose
Records external and prepared datasets used by DrishtiSetu.

## Computer Vision Datasets & Models (Member 2)
| Dataset / Model | Organization / Source | Coverage & Details | License | Intended Module |
|---|---|---|---|---|
| **Sen1Floods11** | Cloud to Street / NASA | 4,831 chips across 11 flood events; Sentinel-1 SAR & Sentinel-2 optical | CC BY 4.0 | Computer Vision (Flood Detection) |
| **Landslide4Sense** | Corley et al. / IEEE GRSM | Multi-sensor satellite imagery benchmark for landslide detection | Open Research | Computer Vision (Landslide Scarring) |
| **Prithvi-100M** | IBM / NASA Geospatial | Geospatial Foundation Model fine-tuned on Sen1Floods11 | Apache-2.0 | Computer Vision (Architecture Reference) |

## Data Integrity Rules
- Never present mock data as real data.
- Always include `model_disclosure` with explicit prototype/benchmark statements.
- Never fabricate confidence scores or claim unverified accuracy.
