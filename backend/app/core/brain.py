"""Core intelligence engine — the brain of Jarvis."""

from __future__ import annotations

from typing import Any

from app.core.confidence import ConfidenceScorer
from app.core.context import ContextManager
from app.core.entity import EntityExtractor
from app.core.intent import Intent, IntentCategory, IntentDetector
from app.core.llm import OllamaLLM
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.core.brain")

SYSTEM_PROMPT = """You are Jarvis, an advanced AI personal assistant running locally.
You are helpful, concise, and proactive. You can control the user's computer,
manage tasks, answer questions, and automate workflows.
When the user gives a command, respond with a clear action plan.
When asked a question, provide a direct, accurate answer.
Support both English and Hindi.
Always be respectful and professional."""


class Brain:
    """Central intelligence engine that processes input and decides actions."""

    def __init__(self) -> None:
        self.intent_detector = IntentDetector()
        self.entity_extractor = EntityExtractor()
        self.confidence_scorer = ConfidenceScorer()
        self.context = ContextManager()
        self.llm = OllamaLLM()

    async def process(self, user_input: str) -> dict[str, Any]:
        """Process user input and return structured response."""
        logger.info(f"Processing input: {user_input[:100]}")

        self.context.add_turn("user", user_input)

        # Check for pending confirmation
        pending = self.context.get_pending_confirmation()
        if pending:
            return await self._handle_confirmation(user_input, pending)

        # Detect intent
        intent = self.intent_detector.detect(user_input)
        entities = self.entity_extractor.extract(user_input)

        # Score confidence
        score = self.confidence_scorer.score_intent(
            user_input,
            matched_pattern=(intent.confidence >= 0.8),
            entity_count=len(entities),
        )

        logger.info(f"Intent: {intent.category.value}/{intent.action} (conf={score.score})")

        # Use LLM for low-confidence intents or conversations
        if self.confidence_scorer.should_use_llm(score) or intent.category in (
            IntentCategory.QUESTION,
            IntentCategory.CONVERSATION,
            IntentCategory.CODE,
            IntentCategory.TRANSLATION,
        ):
            llm_response = await self._get_llm_response(user_input, intent)
            result = {
                "type": "response",
                "intent": intent.category.value,
                "action": intent.action,
                "response": llm_response,
                "confidence": score.score,
                "entities": {e.entity_type: e.value for e in entities},
            }
        else:
            result = {
                "type": "command",
                "intent": intent.category.value,
                "action": intent.action,
                "confidence": score.score,
                "entities": intent.entities,
                "requires_confirmation": intent.requires_confirmation,
                "raw_input": user_input,
            }

        # Handle confirmation requirement
        if intent.requires_confirmation:
            self.context.set_pending_confirmation(
                intent.action,
                f"Execute {intent.action} on {intent.entities.get('target', 'system')}?",
            )
            result["response"] = (
                f"Are you sure you want to {intent.action}? "
                f"Please confirm with 'yes' or 'no'."
            )
            result["type"] = "confirmation_required"

        self.context.add_turn(
            "assistant",
            result.get("response", f"Executing: {intent.action}"),
            intent=intent.category.value,
        )

        return result

    async def _get_llm_response(self, user_input: str, intent: Intent) -> str:
        """Get a response from the LLM with conversation context."""
        if not await self.llm.is_available():
            return self._rule_based_fallback(user_input, intent)

        messages = self.context.to_llm_messages(SYSTEM_PROMPT)
        response = await self.llm.chat(messages)
        return response or self._rule_based_fallback(user_input, intent)

    async def _handle_confirmation(
        self, user_input: str, pending: dict[str, str]
    ) -> dict[str, Any]:
        """Handle a yes/no confirmation response."""
        affirmative = user_input.strip().lower() in (
            "yes", "y", "confirm", "ok", "sure", "do it", "haan", "ha",
        )
        if affirmative:
            return {
                "type": "command",
                "intent": "system_control",
                "action": pending["action"],
                "confirmed": True,
                "response": f"Confirmed. Executing {pending['action']}...",
            }
        return {
            "type": "response",
            "intent": "cancelled",
            "action": "none",
            "response": f"Cancelled: {pending['action']}.",
        }

    def _rule_based_fallback(self, text: str, intent: Intent) -> str:
        """Provide a rule-based response when LLM is unavailable."""
        lower = text.lower()

        greetings = ("hello", "hi", "hey", "good morning", "good evening", "namaste")
        if any(lower.startswith(g) for g in greetings):
            return "Hello! I'm Jarvis, your AI assistant. How can I help you today?"

        if lower in ("time", "what time is it", "what's the time"):
            import datetime
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."

        if lower in ("date", "what's the date", "what date is it"):
            import datetime
            return f"Today's date is {datetime.datetime.now().strftime('%B %d, %Y')}."

        return (
            "I understand you said: '{}'. The Ollama LLM is currently unavailable "
            "for a detailed response. Please ensure Ollama is running.".format(
                text[:100]
            )
        )

    async def close(self) -> None:
        """Clean up resources."""
        await self.llm.close()
