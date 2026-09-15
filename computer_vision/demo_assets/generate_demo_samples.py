"""
Script to generate realistic synthetic satellite patches for DrishtiSetu presentation demos.
Produces 256x256 RGB image pairs (pre and post disaster) for Landslide, Flood, Bridge washout, and Stable terrain.
"""

import os
import numpy as np
import cv2


def generate_assets(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Chamoli Landslide: Pre vs Post
    # Pre: Mountain slope covered in alpine forest (rich greens)
    pre_ls = np.zeros((256, 256, 3), dtype=np.uint8)
    pre_ls[:, :] = [45, 105, 38]  # Forest green
    # Subtle elevation contour lines
    for y in range(20, 240, 30):
        cv2.ellipse(pre_ls, (128, y), (140, 15), 15, 0, 360, (35, 85, 30), 2)

    # Post: Slope failure with bare brown/ochre debris scar
    post_ls = pre_ls.copy()
    pts = np.array([[60, 20], [110, 15], [195, 235], [130, 240]], np.int32)
    cv2.fillPoly(post_ls, [pts], (42, 82, 139))  # BGR brown-tan earthen debris
    # Add rocky texture to the scar
    noise = np.random.randint(-15, 15, (256, 256, 3))
    post_ls = np.clip(post_ls.astype(int) + noise, 0, 255).astype(np.uint8)

    cv2.imwrite(os.path.join(output_dir, "chamoli_landslide_pre.png"), pre_ls)
    cv2.imwrite(os.path.join(output_dir, "chamoli_landslide_post.png"), post_ls)

    # 2. Brahmaputra Flood: Pre vs Post
    # Pre: Agrarian valley with a defined river channel
    pre_fld = np.zeros((256, 256, 3), dtype=np.uint8)
    pre_fld[:, :] = [55, 130, 75]  # Crop green
    # Narrow meandering river channel
    for x in range(256):
        y = int(120 + 20 * np.sin(x / 30.0))
        cv2.circle(pre_fld, (x, y), 8, (160, 95, 30), -1)  # Blue water in BGR

    # Post: Major inundation sheet covering 60% of the plain
    post_fld = pre_fld.copy()
    flood_poly = np.array([[0, 60], [256, 75], [256, 220], [0, 200]], np.int32)
    cv2.fillPoly(post_fld, [flood_poly], (175, 110, 35))  # Deep flood water
    # Submerged silt edges
    cv2.polylines(post_fld, [flood_poly], False, (120, 90, 60), 4)

    cv2.imwrite(os.path.join(output_dir, "brahmaputra_flood_pre.png"), pre_fld)
    cv2.imwrite(os.path.join(output_dir, "brahmaputra_flood_post.png"), post_fld)

    # 3. Wayanad Infrastructure: Bridge Washout
    post_infra = np.zeros((256, 256, 3), dtype=np.uint8)
    post_infra[:, :] = [50, 95, 45]  # Greenery
    # Asphalt road crossing a stream
    cv2.rectangle(post_infra, (0, 115), (256, 140), (105, 105, 105), -1)  # Gray road
    # Stream cutting perpendicular
    cv2.rectangle(post_infra, (100, 0), (155, 256), (145, 90, 40), -1)  # Water
    # Breached bridge gap (scour hole)
    cv2.circle(post_infra, (128, 128), 24, (35, 45, 80), -1)

    cv2.imwrite(os.path.join(output_dir, "bridge_washout_post.png"), post_infra)

    # 4. Safe Plateau: Relocation Candidate
    post_plateau = np.zeros((256, 256, 3), dtype=np.uint8)
    post_plateau[:, :] = [60, 125, 55]  # Uniform stable grassland
    cv2.circle(post_plateau, (128, 128), 90, (65, 135, 60), -1)

    cv2.imwrite(os.path.join(output_dir, "stable_plateau_post.png"), post_plateau)

    print(f"Generated 6 demonstration satellite patches in {output_dir}")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    generate_assets(current_dir)
