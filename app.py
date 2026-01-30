import os
import io
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from PIL import Image
from pdf2image import convert_from_bytes
from rapidocr import RapidOCR, EngineType, LangDet, LangRec, ModelType, OCRVersion

# Environment variables
MODEL_TYPE = os.getenv("MODEL_TYPE", "mobile").lower()
TEXT_SCORE_THRESHOLD = float(os.getenv("TEXT_SCORE_THRESHOLD", "0.5"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
PORT = int(os.getenv("PORT", "5000"))

MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

app = FastAPI(
    title="Spanish OCR API",
    description="OCR service for Spanish text using RapidOCR with PPOCRv5",
    version="1.0.0"
)

# Initialize OCR engines (lazy loading)
ocr_engines = {}

def get_ocr_engine(model_type: str = "mobile"):
    """Get or create OCR engine for specified model type."""
    if model_type not in ocr_engines:
        model_enum = ModelType.SERVER if model_type == "server" else ModelType.MOBILE
        
        ocr_engines[model_type] = RapidOCR(
            params={
                "Det.engine_type": EngineType.ONNXRUNTIME,
                "Det.lang_type": LangDet.MULTI,
                "Det.model_type": model_enum,
                "Det.ocr_version": OCRVersion.PPOCRV5,
                
                "Rec.engine_type": EngineType.ONNXRUNTIME,
                "Rec.lang_type": LangRec.LATIN,
                "Rec.model_type": model_enum,
                "Rec.ocr_version": OCRVersion.PPOCRV5,
                
                "text_score": TEXT_SCORE_THRESHOLD,
                "use_det": True,
                "use_cls": True,
                "use_rec": True,
            }
        )
    
    return ocr_engines[model_type]


def process_image(image: Image.Image, model_type: str) -> str:
    """Process a single image and return extracted text."""
    engine = get_ocr_engine(model_type)
    result, _ = engine(image)
    
    if not result:
        return ""
    
    # Extract text from results and join with line breaks
    texts = [line[1] for line in result]
    return "\n".join(texts)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "service": "spanish-ocr"}


@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    model_type: Optional[str] = Query("mobile", regex="^(mobile|server)$")
):
    """
    Extract text from image or PDF file.
    
    Args:
        file: Image file (jpg, png, etc.) or PDF file
        model_type: Model size - 'mobile' (faster, smaller) or 'server' (more accurate)
    
    Returns:
        JSON with extracted text concatenated from all pages
    """
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
        )
    
    try:
        # Determine file type
        file_extension = file.filename.lower().split(".")[-1] if file.filename else ""
        
        if file_extension == "pdf":
            # Convert PDF to images
            images = convert_from_bytes(contents)
            
            # Process each page and concatenate text
            all_text = []
            for page_num, image in enumerate(images, 1):
                text = process_image(image, model_type)
                if text:
                    all_text.append(text)
            
            final_text = "\n\n".join(all_text)
        
        else:
            # Process as image
            image = Image.open(io.BytesIO(contents))
            final_text = process_image(image, model_type)
        
        return JSONResponse(content={
            "text": final_text,
            "model_type": model_type,
            "file_name": file.filename
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
