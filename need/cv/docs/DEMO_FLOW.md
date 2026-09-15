# Demonstration Flow (v2)

## Step 4: Computer Vision Demonstration
During the live presentation:
1. Present the satellite before/after patch comparison (e.g. Chamoli Landslide or Brahmaputra Flood).
2. Trigger `POST /api/v1/vision/analyze`:
   ```bash
   curl -X POST http://localhost:8000/api/v1/vision/analyze \
     -H "Content-Type: application/json" \
     -d '{"image_url": "computer_vision/demo_assets/chamoli_landslide_post.png", "latitude": 30.552, "longitude": 79.566, "pre_image_url": "computer_vision/demo_assets/chamoli_landslide_pre.png"}'
   ```
3. Highlight the mandatory `model_disclosure` statement proving transparency and academic grounding on public benchmark datasets (Sen1Floods11 / Landslide4Sense).
