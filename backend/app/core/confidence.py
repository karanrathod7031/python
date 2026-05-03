"""Confidence scoring for intent detection results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConfidenceScore:
    """Confidence assessment for a detected intent."""

    score: float
    method: str  # "rule", "llm", "hybrid"
    reasoning: str = ""

    @property
    def is_high(self) -> bool:
        return self.score >= 0.8

    @property
    def is_medium(self) -> bool:
        return 0.5 <= self.score < 0.8

    @property
    def is_low(self) -> bool:
        return self.score < 0.5


class ConfidenceScorer:
    """Score confidence of intent detection and entity extraction."""

    def score_intent(
        self,
        text: str,
        matched_pattern: bool,
        entity_count: int,
    ) -> ConfidenceScore:
        """Calculate confidence score for an intent detection."""
        base_score = 0.9 if matched_pattern else 0.4

        if entity_count > 0:
            base_score = min(1.0, base_score + 0.05 * entity_count)

        word_count = len(text.split())
        if word_count < 2:
            base_score *= 0.8
        elif word_count > 15:
            base_score *= 0.9

        return ConfidenceScore(
            score=round(base_score, 3),
            method="rule" if matched_pattern else "llm",
            reasoning=f"pattern={'yes' if matched_pattern else 'no'}, entities={entity_count}",
        )

    def should_use_llm(self, score: ConfidenceScore) -> bool:
        """Determine whether to escalate to LLM for better understanding."""
        return score.is_low or score.is_medium
