"""Plain-language explanation generator for government documents."""

import json
import logging
from typing import Optional

from config import DOCUMENT_ANALYSIS_PROMPT, KNOWLEDGE_DIR

logger = logging.getLogger(__name__)


class DocumentExplainer:
    """Generates plain-language explanations from Gemma 4 vision output."""

    def __init__(self):
        self.schemes = self._load_schemes()
        self.doc_types = self._load_document_types()
        logger.info(f"Loaded {len(self.schemes)} schemes, {len(self.doc_types)} document types")

    def _load_schemes(self) -> list:
        """Load government scheme knowledge base."""
        schemes_path = KNOWLEDGE_DIR / "schemes.json"
        if schemes_path.exists():
            with open(schemes_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _load_document_types(self) -> dict:
        """Load known document type templates."""
        types_path = KNOWLEDGE_DIR / "document_types.json"
        if types_path.exists():
            with open(types_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_analysis_prompt(self, language_hint: Optional[str] = None) -> str:
        """Get the analysis prompt, optionally customized for language."""
        prompt = DOCUMENT_ANALYSIS_PROMPT
        if language_hint:
            prompt += f"\n\nNote: This document appears to be primarily in {language_hint}. Respond accordingly."
        return prompt

    def enrich_with_scheme_info(self, analysis_text: str) -> str:
        """Enrich analysis with relevant scheme information from knowledge base."""
        enriched = analysis_text

        # Match document content against known schemes
        for scheme in self.schemes:
            keywords = scheme.get("keywords", [])
            if any(kw.lower() in analysis_text.lower() for kw in keywords):
                scheme_info = (
                    f"\n\n---\n🏛️ **Related Scheme: {scheme['name']}**\n"
                    f"{scheme['description']}\n"
                    f"Eligibility: {scheme.get('eligibility', 'See official guidelines')}\n"
                    f"Benefits: {scheme.get('benefits', 'See official guidelines')}\n"
                    f"Apply at: {scheme.get('apply_url', 'Visit nearest CSC/Common Service Centre')}"
                )
                enriched += scheme_info
                break

        return enriched

    def format_for_display(self, raw_response: str) -> dict:
        """Parse raw model response into structured display format."""
        sections = {}
        current_section = None
        current_content = []

        for line in raw_response.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## "):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = stripped[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return {
            "raw": raw_response,
            "sections": sections,
            "has_structured_output": len(sections) > 0,
        }
