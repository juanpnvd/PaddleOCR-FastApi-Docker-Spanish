"""
Quick test script to verify the OCR setup works locally.
This tests the RapidOCR library initialization without running the full API.
"""

try:
    from rapidocr import RapidOCR, EngineType, LangDet, LangRec, ModelType, OCRVersion
    print("✓ Import successful: rapidocr library")
    
    # Test engine initialization (same config as app.py)
    engine = RapidOCR(
        params={
            "Det.engine_type": EngineType.ONNXRUNTIME,
            "Det.lang_type": LangDet.MULTI,
            "Det.model_type": ModelType.MOBILE,
            "Det.ocr_version": OCRVersion.PPOCRV5,
            
            "Rec.engine_type": EngineType.ONNXRUNTIME,
            "Rec.lang_type": LangRec.LATIN,
            "Rec.model_type": ModelType.MOBILE,
            "Rec.ocr_version": OCRVersion.PPOCRV5,
            
            "text_score": 0.5,
            "use_det": True,
            "use_cls": True,
            "use_rec": True,
        }
    )
    print("✓ RapidOCR engine initialized successfully")
    print("✓ Configuration: PPOCRv5 Mobile + ONNX Runtime + Latin (Spanish)")
    print("\n✅ Everything is ready for deployment!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Run: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Initialization error: {e}")
