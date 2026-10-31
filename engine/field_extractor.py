"""Structured field extraction from government documents using Gemma 4 function calling."""

import json
import logging
import re
from typing import Optional

from config import FIELD_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class FieldExtractor:
    """Extracts structured fields from document images using Gemma 4."""

    def get_extraction_prompt(self) -> str:
        """Return the field extraction prompt."""
        return FIELD_EXTRACTION_PROMPT

    @staticmethod
    def parse_json_response(response_text: str) -> Optional[dict]:
        """Extract JSON from model response.

        Handles both fenced code blocks and raw JSON.
        """
        # Try fenced JSON block first
        fenced_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if fenced_match:
            try:
                return json.loads(fenced_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try raw JSON array/object
        bracket_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", response_text)
        if bracket_match:
            try:
                return json.loads(bracket_match.group(1))
            except json.JSONDecodeError:
                pass

        logger.warning("Could not parse JSON from model response")
        return None

    @staticmethod
    def validate_extracted_fields(data: dict) -> dict:
        """Validate and normalize extracted field data."""
        validated = {
            "document_type": data.get("document_type", "Unknown"),
            "language": data.get("language", "unknown"),
            "title": data.get("title", ""),
            "issuing_authority": data.get("issuing_authority", ""),
            "fields": [],
            "deadlines": data.get("deadlines", []),
            "fees": data.get("fees", []),
            "required_documents": data.get("required_documents", []),
            "submission_address": data.get("submission_address", ""),
            "contact_info": data.get("contact_info", ""),
            "confidence": "high" if data.get("fields") else "low",
        }

        # Normalize fields list
        raw_fields = data.get("fields", [])
        for field in raw_fields:
            if isinstance(field, dict):
                validated["fields"].append({
                    "name": field.get("name", ""),
                    "value": field.get("value", ""),
                    "required": field.get("required", False),
                })

        return validated
