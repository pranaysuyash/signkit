# Auto-Detection & ML Training for Signature Extraction

## Current Approach (Manual Selection)

Users manually draw rectangle around signature → threshold/color adjust → extract

**Problem**: Tedious for batch processing, requires user input for each signature

---

## Goal: Automatic Signature Detection

**Detect signatures automatically** with minimal/no user input

---

## Approach 1: Traditional CV (Computer Vision)

### 1.1 Contour-Based Detection

**How it works:**

1. Convert to grayscale
2. Apply threshold (Otsu's or adaptive)
3. Find contours (cv2.findContours)
4. Filter contours by:
   - Area (signatures are usually 100-10,000 px²)
   - Aspect ratio (1:3 to 3:1 typically)
   - Position (bottom 1/3 of document)
   - Solidity (signature strokes vs printed text)

**Pros:**

- ✅ No training needed
- ✅ Fast (milliseconds)
- ✅ Works on any device
- ✅ Small code footprint

**Cons:**

- ❌ Brittle - fails with complex backgrounds
- ❌ Many false positives (printed text, logos, stamps)
- ❌ Needs manual tuning per document type

### Implementation (OpenCV)

```python
import cv2
import numpy as np

def detect_signature_contours(image_path):
    """Detect signatures using contour analysis."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    signature_candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)

        # Filter by heuristics
        if (100 < area < 10000 and           # Reasonable size
            0.3 < aspect_ratio < 3.0 and      # Not too thin/wide
            y > img.shape[0] * 0.5):          # Bottom half

            signature_candidates.append((x, y, w, h, area))

    # Return largest candidate (likely signature)
    if signature_candidates:
        return max(signature_candidates, key=lambda x: x[4])[:4]
    return None
```

**When to use:** Quick prototype, simple documents (contracts, forms)

---

### 1.2 OCR + Negative Space Detection

**How it works:**

1. Run OCR (Tesseract) to detect text regions
2. Identify "negative spaces" (areas without text)
3. Signatures are often in negative spaces near text like "Signature:", "Sign here:"

**Pros:**

- ✅ More robust than pure contours
- ✅ Can locate signature fields (e.g., "Sign here:")
- ✅ Combines with OCR for text extraction

**Cons:**

- ❌ Requires Tesseract (40MB dependency)
- ❌ Slower (1-2 seconds per page)
- ❌ Still brittle with handwritten documents

### Implementation

```python
import pytesseract
from PIL import Image

def detect_signature_ocr(image_path):
    """Detect signatures using OCR and keyword search."""
    img = Image.open(image_path)

    # Run OCR
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    # Find signature-related keywords
    keywords = ["signature", "sign here", "signed", "date"]
    signature_regions = []

    for i, text in enumerate(ocr_data['text']):
        if any(kw in text.lower() for kw in keywords):
            x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                         ocr_data['width'][i], ocr_data['height'][i])

            # Look for empty space below text (likely signature area)
            signature_regions.append((x, y + h + 10, w, h * 2))

    return signature_regions
```

**When to use:** Documents with "Signature:" labels, forms

---

## Approach 2: Machine Learning (Deep Learning)

### 2.1 Object Detection (YOLO / Faster R-CNN)

**How it works:**

1. Collect dataset of documents with labeled signatures
2. Train object detection model (YOLOv8, Faster R-CNN)
3. Model outputs bounding boxes around signatures

**Pros:**

- ✅ Very accurate (90-95%+ with good training data)
- ✅ Handles complex backgrounds
- ✅ Works on diverse document types
- ✅ Fast inference (50-100ms on GPU, 500ms on CPU)

**Cons:**

- ❌ Requires labeled training data (500-1000+ images)
- ❌ Large model size (50-200MB)
- ❌ Needs GPU for reasonable speed (or quantized CPU version)
- ❌ Training infrastructure required

### Dataset Needed

**Minimum viable dataset:**

- 500 documents with signatures
- Bounding box annotations (x, y, w, h for each signature)
- Diverse types: contracts, forms, receipts, letters

**Tools for annotation:**

- LabelImg (https://github.com/heartexlabs/labelImg)
- Roboflow (https://roboflow.com/) - cloud-based, has free tier
- CVAT (https://cvat.org/) - open source

### Training with YOLOv8

```python
from ultralytics import YOLO

# 1. Prepare dataset in YOLO format
# dataset/
#   train/
#     images/
#     labels/  (YOLO format: class x_center y_center width height)
#   val/
#     images/
#     labels/

# 2. Train
model = YOLO('yolov8n.pt')  # Start with pre-trained nano model
model.train(
    data='signature_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    device='mps',  # Or 'cuda' or 'cpu'
)

# 3. Inference
results = model.predict('document.jpg')
for box in results[0].boxes:
    x1, y1, x2, y2 = box.xyxy[0]  # Bounding box
    conf = box.conf[0]              # Confidence score
    print(f"Signature at ({x1},{y1},{x2},{y2}) - confidence: {conf}")
```

**When to use:** Serious production app, willing to invest in training

---

### 2.2 Segmentation (U-Net / Mask R-CNN)

**How it works:**

1. Pixel-level segmentation (not just bounding box)
2. Model outputs exact signature pixels (mask)
3. Better than bbox for extracting signature with transparency

**Pros:**

- ✅ Pixel-perfect extraction (no manual cropping)
- ✅ Handles overlapping elements
- ✅ Best quality output

**Cons:**

- ❌ Harder to train (needs pixel-level annotations)
- ❌ Slower inference
- ❌ Larger model size (100-300MB)

**When to use:** Premium feature, when bbox detection isn't accurate enough

---

## Approach 3: Foundation Models (Transformer-Based)

### 3.1 Vision Transformers (ViT, DINO)

**Pre-trained models** for general computer vision tasks

**Example: DINO (Facebook Research)**

- Self-supervised learning (no labels needed)
- Can detect "objects of interest" without training
- Could potentially detect signatures as salient regions

**Pros:**

- ✅ May work out-of-the-box with zero training
- ✅ State-of-the-art accuracy

**Cons:**

- ❌ Very large models (200MB+)
- ❌ Slow inference (1-5 seconds)
- ❌ Requires advanced ML knowledge

**When to use:** Research project, not production (yet)

---

### 3.2 Document AI APIs (Cloud Services)

**Use existing APIs** from Google, AWS, Azure

**Google Document AI:**

```python
from google.cloud import documentai_v1 as documentai

client = documentai.DocumentProcessorServiceClient()
processor_name = f"projects/{project_id}/locations/us/processors/{processor_id}"

# Process document
request = documentai.ProcessRequest(
    name=processor_name,
    raw_document=documentai.RawDocument(content=image_bytes, mime_type='image/jpeg')
)
result = client.process_document(request=request)

# Extract signature fields
for entity in result.document.entities:
    if entity.type_ == "signature":
        print(f"Signature found: {entity.mention_text}")
```

**Pros:**

- ✅ No training needed
- ✅ Very accurate (trained on millions of documents)
- ✅ Handles many document types

**Cons:**

- ❌ Costs money ($1.50-3.50 per 1000 pages)
- ❌ Requires internet connection
- ❌ Privacy concerns (uploads to cloud)
- ❌ Conflicts with "privacy-first" positioning

**When to use:** Enterprise tier, customers willing to pay for cloud processing

---

## Recommended Approach for You (Solo Dev)

### Phase 1: Traditional CV Prototype (Do This First)

**Implementation:**

1. Add "Auto-Detect" button to UI
2. Use contour-based detection (OpenCV only, no new deps)
3. Show all candidates, let user pick correct one
4. Good enough for 60-70% of simple documents

**Effort:** 1-2 days  
**Cost:** $0 (no new infrastructure)

```python
# In desktop_app/utils/auto_detect.py
def auto_detect_signatures(image_path):
    """Simple contour-based detection."""
    # ... contour code from above ...
    return [(x, y, w, h, confidence), ...]  # Multiple candidates
```

---

### Phase 2: Collect Training Data (While Users Use App)

**User feedback loop:**

1. When users manually select signatures, log anonymized data:
   - Document type (contract, form, etc.)
   - Signature bounding box
   - Image characteristics
2. After 500-1000 sessions, you have a dataset!
3. Use for training ML model

**Privacy:** Ask permission, anonymize, or store locally only

---

### Phase 3: Train Custom Model (6-12 Months Later)

**Once you have dataset:**

1. Annotate 500+ documents
2. Train YOLOv8 model (2-4 hours on MacBook with MPS)
3. Deploy as optional 50MB model download
4. Falls back to traditional CV if model not installed

**Effort:** 1-2 weeks  
**Cost:** $0 (train locally on MacBook M-series)

---

### Phase 4: Fine-Tune with User Data (Ongoing)

**Continuous improvement:**

- Users correct auto-detections → add to training set
- Retrain model monthly
- Accuracy improves over time

---

## Model Hosting Options

### Option A: Bundle with App (Best for Privacy)

- Include model.pt file in app (~50MB)
- Load locally with PyTorch or ONNX
- No internet required, zero privacy concerns

### Option B: On-Demand Download

- App downloads model on first use
- Stores in ~/.signature_extractor/models/
- Reduces initial app size

### Option C: Cloud API (For Enterprise Tier)

- Your own API endpoint
- Customers with API key can use
- Charge per API call ($0.01-0.05 per detection)

---

## Training Infrastructure (Solo Dev)

### Minimal Setup

**Hardware:**

- Your MacBook Pro (M1/M2/M3 with MPS)
- Training time: 2-4 hours for 100 epochs

**Software:**

```bash
pip install ultralytics torch torchvision
```

**Dataset:**

- Start with 100 annotated images (weekend project)
- Expand to 500 over time as users contribute

**Cost:** $0 (use your Mac)

### If You Need More Power

**Cloud GPU (Optional):**

- Google Colab Pro ($10/month) - V100 GPU
- Lambda Labs ($0.50/hour) - A100 GPU
- Paperspace ($8/month) - P4000 GPU

**When to use:** Training large models (>100 epochs, >1000 images)

---

## Realistic Timeline

### Week 1-2: Traditional CV Prototype

- [x] Implement contour detection
- [x] Add "Auto-Detect" button
- [x] Test on sample documents
- [x] Ship to early users

### Month 1-3: Collect Feedback

- [ ] Log user selections (with permission)
- [ ] Build dataset of 100+ documents
- [ ] Evaluate accuracy of contour detection

### Month 4-6: Train First Model

- [ ] Annotate 500 documents (use Roboflow)
- [ ] Train YOLOv8 nano model
- [ ] A/B test: CV vs ML detection
- [ ] Ship ML model as beta feature

### Month 6+: Iterate

- [ ] Collect more training data
- [ ] Retrain monthly
- [ ] Add segmentation for pixel-perfect extraction
- [ ] Consider fine-tuning with user corrections

---

## Recommended Tech Stack

### For Prototype (Phase 1):

```
OpenCV (already have)
NumPy (already have)
```

### For ML Model (Phase 3):

```
ultralytics (YOLOv8) - pip install ultralytics
torch + torchvision - pip install torch torchvision
onnxruntime (for faster inference) - pip install onnxruntime
```

### For Training:

```
labelImg or Roboflow - annotation
ultralytics - training
tensorboard - monitoring
```

---

## Next Steps

**Want me to implement Phase 1 (contour detection) now?**

I can add:

1. `desktop_app/utils/auto_detect.py` - Contour-based detection
2. "🔍 Auto-Detect" button in main window
3. Shows all candidates, user picks best one
4. ~200 lines of code, no new dependencies

**Or research more first?** Happy to dive deeper into any approach!
