"""Vision pipeline for document image preprocessing and analysis."""

import io
import logging
from typing import Tuple

from PIL import Image, ImageOps, ImageFilter

from config import TOKEN_BUDGET

logger = logging.getLogger(__name__)


class VisionPipeline:
    """Handles image preprocessing optimized for Gemma 4 document OCR."""

    # Optimal dimensions per token budget (from Gemma 4 docs)
    BUDGET_DIMENSIONS = {
        70: (336, 336),
        140: (448, 448),
        280: (672, 672),
        560: (896, 896),
        1120: (1344, 1344),
    }

    def __init__(self, token_budget: int = TOKEN_BUDGET):
        self.token_budget = token_budget
        self.target_size = self.BUDGET_DIMENSIONS.get(token_budget, (896, 896))
        logger.info(f"VisionPipeline initialized: token_budget={token_budget}, target_size={self.target_size}")

    def preprocess(self, image_bytes: bytes) -> Tuple[bytes, dict]:
        """Preprocess image for optimal document OCR.

        Steps:
        1. Auto-orient based on EXIF
        2. Convert to RGB
        3. Enhance contrast for better OCR
        4. Resize maintaining aspect ratio within token budget
        5. Sharpen for text clarity

        Returns:
            Tuple of (processed image bytes, metadata dict)
        """
        metadata = {
            "original_size": None,
            "processed_size": None,
            "token_budget": self.token_budget,
            "format": "JPEG",
        }

        # Open and auto-orient
        image = Image.open(io.BytesIO(image_bytes))
        metadata["original_size"] = image.size
        image = ImageOps.exif_transpose(image) or image

        # Convert to RGB (handles RGBA, palette, etc.)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Enhance contrast for better text readability
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)

        # Sharpen for text clarity
        image = image.filter(ImageFilter.SHARPEN)

        # Resize maintaining aspect ratio within target dimensions
        max_w, max_h = self.target_size
        ratio = min(max_w / image.width, max_h / image.height)
        if ratio < 1.0:
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        metadata["processed_size"] = image.size

        # Save as JPEG with high quality
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=95, optimize=True)
        processed_bytes = output.getvalue()

        logger.info(
            f"Preprocessed: {metadata['original_size']} → {metadata['processed_size']} "
            f"(budget={self.token_budget})"
        )

        return processed_bytes, metadata

    @staticmethod
    def validate_image(image_bytes: bytes, max_size_mb: int = 10) -> Tuple[bool, str]:
        """Validate that uploaded file is a valid image within size limits."""
        if len(image_bytes) > max_size_mb * 1024 * 1024:
            return False, f"Image too large. Maximum size is {max_size_mb}MB."

        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            return True, "Valid image"
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
