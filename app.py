"""PatraBodh - Multimodal Document Understanding for Rural Government Services.

FastAPI application entry point.
"""

import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from config import STATIC_DIR, MAX_UPLOAD_SIZE_MB, ALLOWED_EXTENSIONS
from engine.inference import InferenceBackend
from engine.vision_pipeline import VisionPipeline
from engine.explainer import DocumentExplainer
from engine.field_extractor import FieldExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize components
app = FastAPI(
    title="PatraBodh 📄🔍",
    description="Multimodal Document Understanding for Rural Government Services",
    version="1.0.0",
)

backend = InferenceBackend()
vision = VisionPipeline()
explainer = DocumentExplainer()
extractor = FieldExtractor()

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main web UI."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(
        content="<h1>PatraBodh</h1><p>Static files not found. Check /static directory.</p>"
    )


@app.get("/api/health")
async def health():
    """Health check endpoint with backend status."""
    backend_status = await backend.health_check()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "backend": backend_status,
    }


@app.post("/api/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Analyze a government document image.

    Accepts an image file upload and returns:
    - Plain-language explanation of the document
    - Structured field extraction
    - Related government scheme information
    """
    # Validate file extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read and validate image
    image_bytes = await file.read()
    is_valid, msg = VisionPipeline.validate_image(image_bytes, MAX_UPLOAD_SIZE_MB)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    # Preprocess image
    processed_bytes, metadata = vision.preprocess(image_bytes)

    # Run analysis
    logger.info(f"Analyzing document: {file.filename} ({metadata['original_size']})")
    analysis_prompt = explainer.get_analysis_prompt()
    raw_response = await backend.analyze_image(
        image_bytes=processed_bytes,
        prompt=analysis_prompt,
        enable_thinking=True,
    )

    # Enrich with scheme info
    enriched_response = explainer.enrich_with_scheme_info(raw_response)

    # Format for display
    formatted = explainer.format_for_display(enriched_response)

    # Also run field extraction
    extraction_prompt = extractor.get_extraction_prompt()
    extraction_response = await backend.analyze_image(
        image_bytes=processed_bytes,
        prompt=extraction_prompt,
        enable_thinking=False,
    )
    extracted_fields = extractor.parse_json_response(extraction_response)
    if extracted_fields:
        extracted_fields = extractor.validate_extracted_fields(extracted_fields)

    return JSONResponse(content={
        "success": True,
        "filename": file.filename,
        "metadata": metadata,
        "analysis": formatted,
        "extracted_fields": extracted_fields,
    })


@app.post("/api/analyze/quick")
async def quick_analyze(file: UploadFile = File(...)):
    """Quick analysis - returns only the plain-language explanation (faster)."""
    image_bytes = await file.read()
    is_valid, msg = VisionPipeline.validate_image(image_bytes, MAX_UPLOAD_SIZE_MB)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    processed_bytes, metadata = vision.preprocess(image_bytes)
    analysis_prompt = explainer.get_analysis_prompt()
    raw_response = await backend.analyze_image(
        image_bytes=processed_bytes,
        prompt=analysis_prompt,
        enable_thinking=True,
    )
    enriched = explainer.enrich_with_scheme_info(raw_response)

    return JSONResponse(content={
        "success": True,
        "explanation": enriched,
    })


if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT

    logger.info(f"Starting PatraBodh on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
