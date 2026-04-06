import logging

logger = logging.getLogger(__name__)


class AIProcessor:
    """可替换为真实 LLM 服务。"""

    async def analyze(self, text: str) -> dict:
        intent = "order_query" if "order" in text.lower() else "general"
        draft = "Dear customer, we have received your message and will process it shortly."
        result = {
            "intent": intent,
            "language": "en",
            "confidence": 0.86,
            "summary": text[:200],
            "entities": {"order_no": self._extract_order_no(text)},
            "draft_reply": draft,
            "structured_data": {
                "intent": intent,
                "order_no": self._extract_order_no(text),
                "priority": "NORMAL",
            },
        }
        logger.info("AI analyzed email intent=%s", intent)
        return result

    @staticmethod
    def _extract_order_no(text: str) -> str | None:
        for token in text.replace("#", " #").split():
            if token.startswith("#") and len(token) > 3:
                return token.strip(" ,.;")
        return None
