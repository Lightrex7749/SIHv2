# Integration Guide (v2)

## Integration Order
1. Stage 1: Frontend + Backend skeleton (Member 6)
2. Stage 2: Mock habitation data (Member 3)
3. Stage 3: Mock risk engine + /risk/explain (Member 1)
4. Stage 4: Mock relocation recommendation (Member 5)
5. Stage 5: GIS map layers (Member 3)
6. Stage 6: Real ML risk engine (Member 1)
7. Stage 7: Real CV module with model_disclosure (Member 2 - Current Module)
8. Stage 8: RAG retrieval (Member 4)
9. Stage 9: Agentic decision layer (Member 5)
10. Stage 10: End-to-end testing + decision_log (All)

## Member 2 Module Status
The Computer Vision module is fully built and tested:
- Endpoint: `POST /api/v1/vision/analyze`
- Router: `from computer_vision.router import vision_router`
- Schemas & Contract: 100% compliant with API Contract v2.
