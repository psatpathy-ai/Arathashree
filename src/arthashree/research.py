from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


@dataclass
class ResearchHypothesis:
    hypothesis_id: str
    title: str
    universe: str
    frequency: str
    features: list[str] = field(default_factory=list)
    entry_logic: str = ""
    exit_logic: str = ""
    risk_model: str = ""
    cost_model: str = ""
    created_by: str = "research_agent"
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunCard:
    run_id: str
    hypothesis_id: str
    config: dict[str, Any] = field(default_factory=dict)
    dataset_manifest: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    report_path: str | None = None
