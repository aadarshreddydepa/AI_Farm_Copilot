# backend/app/services/response_service.py
import logging
from typing import List, Dict
from ..services.language_service import LanguageProcessor  # adjust import path if needed

logger = logging.getLogger(__name__)

class ResponseService:
    def __init__(self, language_processor: LanguageProcessor):
        self.lang_proc = language_processor

    def assemble(self, query: str, ranked_results: List[Dict], user_lang: str) -> Dict:
        """
        Build a user-facing response:
          - short_answer (one-liner)
          - detailed (top N results compiled)
          - meta (sources)
        Then translate to user's language and return both en + translated.
        """
        if not ranked_results:
            fallback = "I'm sorry — I couldn't find a clear answer. Try rephrasing or ask about something else."
            translated = self.lang_proc.translate_to_language(fallback, user_lang)
            return {"answer_en": fallback, "answer_local": translated, "sources": []}

        top = ranked_results[0]
        short_answer_en = top["title"] or (top["body"][:200] + "...")
        # build detailed: compile top results with source credits
        detailed_parts = []
        for r in ranked_results:
            detailed_parts.append(f"Source: {r['source']} (score: {r['score']})\n{r['title']}\n{r['body']}\n")
        detailed_en = "\n\n".join(detailed_parts)

        # Optionally post-process / shorten the detailed text
        # Translate back to user language
        try:
            short_local = self.lang_proc.translate_to_language(short_answer_en, user_lang)
            detailed_local = self.lang_proc.translate_to_language(detailed_en, user_lang)
        except Exception as e:
            logger.warning(f"Translation back to user language failed: {e}")
            short_local, detailed_local = short_answer_en, detailed_en

        sources = [{"source": r["source"], "type": r["type"], "score": r["score"]} for r in ranked_results]

        return {
            "answer_en": short_answer_en,
            "answer_local": short_local,
            "detailed_en": detailed_en,
            "detailed_local": detailed_local,
            "sources": sources
        }
