"""Dual-mode inference backend: Gemini API (cloud) and Ollama (local/offline)."""

import base64
import json
import logging
from pathlib import Path
from typing import Optional

import httpx

from config import get_model_config, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class InferenceBackend:
    """Unified inference interface supporting both Gemini API and Ollama."""

    def __init__(self):
        self.config = get_model_config()
        self.mode = self.config["mode"]
        logger.info(f"Initialized inference backend: {self.mode} (model: {self.config['model']})")

    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
        system_prompt: Optional[str] = None,
        enable_thinking: bool = True,
    ) -> str:
        """Analyze an image with the configured model.

        Args:
            image_bytes: Raw image file bytes
            prompt: User prompt describing the task
            system_prompt: System instructions (defaults to config)
            enable_thinking: Whether to enable Gemma 4 thinking mode

        Returns:
            Model response text
        """
        sys_prompt = system_prompt or SYSTEM_PROMPT

        if self.mode == "gemini":
            return await self._gemini_analyze(image_bytes, prompt, sys_prompt, enable_thinking)
        elif self.mode == "ollama":
            return await self._ollama_analyze(image_bytes, prompt, sys_prompt)
        else:
            raise ValueError(f"Unknown inference mode: {self.mode}")

    async def _gemini_analyze(
        self,
        image_bytes: bytes,
        prompt: str,
        system_prompt: str,
        enable_thinking: bool,
    ) -> str:
        """Use Google Gemini API with Gemma 4 model."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.config["api_key"])

            # Encode image as base64 for inline data
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            # Build the prompt with thinking mode if enabled
            full_prompt = ""
            if enable_thinking:
                full_prompt += "<|think|>"
            full_prompt += f"{system_prompt}\n\n{prompt}"

            # Create content parts with image and text
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        types.Part.from_text(text=full_prompt),
                    ],
                )
            ]

            # Generate response
            response = client.models.generate_content(
                model=self.config["model"],
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                ),
            )

            return response.text or "No response generated."

        except ImportError:
            logger.error("google-genai not installed. Run: pip install google-genai")
            return "Error: google-genai package not installed. Please install it for cloud mode."
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Error calling Gemini API: {str(e)}"

    async def _ollama_analyze(
        self,
        image_bytes: bytes,
        prompt: str,
        system_prompt: str,
    ) -> str:
        """Use local Ollama instance with Gemma 4 model."""
        try:
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            payload = {
                "model": self.config["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_b64],
                    },
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 4096,
                },
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.config['base_url']}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

            return result.get("message", {}).get("content", "No response generated.")

        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama. Is it running?")
            return (
                "Error: Cannot connect to Ollama. Please ensure Ollama is running:\n"
                "1. Install: https://ollama.com\n"
                f"2. Pull model: ollama pull {self.config['model']}\n"
                "3. Start: ollama serve"
            )
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"Error calling Ollama: {str(e)}"

    async def health_check(self) -> dict:
        """Check if the inference backend is available."""
        if self.mode == "gemini":
            return {
                "mode": "gemini",
                "model": self.config["model"],
                "available": bool(self.config.get("api_key")),
            }
        elif self.mode == "ollama":
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{self.config['base_url']}/api/tags")
                    models = [m["name"] for m in resp.json().get("models", [])]
                    return {
                        "mode": "ollama",
                        "model": self.config["model"],
                        "available": self.config["model"] in models,
                        "loaded_models": models,
                    }
            except Exception:
                return {
                    "mode": "ollama",
                    "model": self.config["model"],
                    "available": False,
                    "error": "Cannot connect to Ollama",
                }
        return {"mode": self.mode, "available": False}
