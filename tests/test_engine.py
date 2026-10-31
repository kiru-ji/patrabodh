"""Unit tests for PatraBodh engine components."""

import json
import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.field_extractor import FieldExtractor
from engine.explainer import DocumentExplainer
from engine.vision_pipeline import VisionPipeline


class TestFieldExtractor:
    """Tests for structured field extraction."""

    def test_parse_json_fenced(self):
        response = '''Here are the fields:
```json
{
  "document_type": "Aadhaar Enrollment",
  "language": "hi",
  "title": "आधार नामांकन फॉर्म",
  "fields": [
    {"name": "पूरा नाम", "value": "", "required": true},
    {"name": "जन्म तिथि", "value": "", "required": true}
  ]
}
```'''
        result = FieldExtractor.parse_json_response(response)
        assert result is not None
        assert result["document_type"] == "Aadhaar Enrollment"
        assert len(result["fields"]) == 2

    def test_parse_json_raw(self):
        response = '{"document_type": "PAN", "language": "en", "fields": []}'
        result = FieldExtractor.parse_json_response(response)
        assert result is not None
        assert result["document_type"] == "PAN"

    def test_parse_json_invalid(self):
        result = FieldExtractor.parse_json_response("No JSON here at all")
        assert result is None

    def test_validate_extracted_fields(self):
        data = {
            "document_type": "Test",
            "language": "en",
            "fields": [{"name": "Name", "value": "Test", "required": True}],
            "deadlines": ["2026-12-31"],
        }
        validated = FieldExtractor.validate_extracted_fields(data)
        assert validated["document_type"] == "Test"
        assert len(validated["fields"]) == 1
        assert validated["confidence"] == "high"


class TestDocumentExplainer:
    """Tests for explanation enrichment."""

    def test_load_schemes(self):
        explainer = DocumentExplainer()
        assert len(explainer.schemes) > 0

    def test_enrich_with_aadhaar(self):
        explainer = DocumentExplainer()
        text = "This is an Aadhaar enrollment form for UIDAI registration."
        enriched = explainer.enrich_with_scheme_info(text)
        assert "Aadhaar" in enriched
        assert "UIDAI" in enriched

    def test_format_for_display(self):
        explainer = DocumentExplainer()
        raw = "## 📄 Document Type\nAadhaar Form\n\n## 📝 About\nThis is for identity."
        formatted = explainer.format_for_display(raw)
        assert formatted["has_structured_output"] is True
        assert "📄 Document Type" in formatted["sections"]


class TestVisionPipeline:
    """Tests for image preprocessing."""

    def test_validate_valid_image(self):
        # Create a minimal valid JPEG
        from PIL import Image
        import io
        img = Image.new("RGB", (100, 100), color="white")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        is_valid, msg = VisionPipeline.validate_image(buf.getvalue())
        assert is_valid

    def test_validate_too_large(self):
        fake_bytes = b"x" * (11 * 1024 * 1024)  # 11MB
        is_valid, msg = VisionPipeline.validate_image(fake_bytes, max_size_mb=10)
        assert not is_valid
        assert "too large" in msg.lower()

    def test_preprocess(self):
        from PIL import Image
        import io
        img = Image.new("RGB", (2000, 1500), color="white")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")

        pipeline = VisionPipeline(token_budget=560)
        processed_bytes, metadata = pipeline.preprocess(buf.getvalue())

        assert metadata["original_size"] == (2000, 1500)
        assert metadata["token_budget"] == 560
        assert len(processed_bytes) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
