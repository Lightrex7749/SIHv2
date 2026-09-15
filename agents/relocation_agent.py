"""
DrishtiSetu — Relocation Agent (Member 5)
Identifies and ranks candidate relocation sites while verifying land-use conflicts.
"""

from typing import Dict, Any, List
from relocation.site_selection import RelocationEngine


class RelocationAgent:
    def __init__(self):
        self.engine = RelocationEngine()

    def evaluate(self, habitation_id: str) -> Dict[str, Any]:
        rec = self.engine.recommend_site(habitation_id)
        return rec.model_dump()
