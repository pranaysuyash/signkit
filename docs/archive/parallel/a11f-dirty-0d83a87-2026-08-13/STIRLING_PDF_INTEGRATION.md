# Stirling-PDF Integration Plan

## Overview

Integration strategy for Stirling-PDF into our signature extraction platform to enable comprehensive PDF manipulation capabilities.

## Architecture

### Option A: Microservice (Recommended for MVP)

```
┌─────────────────┐
│  Desktop App    │
│   (PySide6)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Backend│
│   (Port 8001)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Stirling│ │   Your Core  │
│   PDF   │ │  Signature   │
│ (Docker)│ │  Processing  │
│Port 8080│ │              │
└─────────┘ └──────────────┘
```

### Docker Setup

**docker-compose.yml** (new file at repo root):

```yaml
version: '3.8'

services:
  stirling-pdf:
    image: frooodle/s-pdf:latest
    container_name: stirling-pdf
    ports:
      - '8080:8080'
    volumes:
      - ./stirling-data/configs:/configs
      - ./stirling-data/customFiles:/customFiles
      - ./stirling-data/logs:/logs
    environment:
      - DOCKER_ENABLE_SECURITY=false # Enable in production
      - INSTALL_BOOK_AND_ADVANCED_HTML_OPS=false
      - LANGS=en_US
    restart: unless-stopped
    networks:
      - pdf-network

  backend:
    build: ./backend
    container_name: signature-backend
    ports:
      - '8001:8001'
    depends_on:
      - stirling-pdf
    environment:
      - STIRLING_PDF_URL=http://stirling-pdf:8080
    networks:
      - pdf-network

networks:
  pdf-network:
    driver: bridge
```

## API Client Implementation

**backend/app/services/stirling_client.py** (new file):

```python
"""Client for Stirling-PDF API integration."""
import os
import requests
from typing import BinaryIO, Optional
import logging

logger = logging.getLogger(__name__)


class StirlingPDFClient:
    """Wrapper for Stirling-PDF API endpoints."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "STIRLING_PDF_URL",
            "http://localhost:8080"
        )
        self.timeout = 120  # 2 minutes for heavy operations

    def merge_pdfs(
        self,
        files: list[tuple[str, BinaryIO]],
        sort_type: str = "orderProvided"
    ) -> bytes:
        """
        Merge multiple PDFs into one.

        Args:
            files: List of (filename, file_object) tuples
            sort_type: "orderProvided" | "byFileName" | "byDateModified"

        Returns:
            Merged PDF as bytes
        """
        url = f"{self.base_url}/api/v1/merge-pdfs"

        files_data = [
            ("fileInput", (name, f, "application/pdf"))
            for name, f in files
        ]

        try:
            response = requests.post(
                url,
                files=files_data,
                data={"sortType": sort_type},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Stirling-PDF merge failed: {e}")
            raise

    def split_pdf(
        self,
        pdf_file: BinaryIO,
        split_type: str = "DIVIDE",
        pages: Optional[str] = None
    ) -> list[bytes]:
        """
        Split PDF by pages or intervals.

        Args:
            pdf_file: PDF file object
            split_type: "DIVIDE" | "REMOVE_FIRST" | "REMOVE_LAST" | "CUSTOM"
            pages: For CUSTOM, comma-separated page ranges (e.g., "1-3,5,7-10")

        Returns:
            List of PDF bytes (one per split)
        """
        url = f"{self.base_url}/api/v1/split-pages"

        files = {"fileInput": ("input.pdf", pdf_file, "application/pdf")}
        data = {"splitType": split_type}

        if pages and split_type == "CUSTOM":
            data["pages"] = pages

        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            # Stirling returns a zip for multiple outputs
            return [response.content]  # Simplified; handle zip extraction
        except requests.RequestException as e:
            logger.error(f"Stirling-PDF split failed: {e}")
            raise

    def rotate_pdf(
        self,
        pdf_file: BinaryIO,
        angle: int = 90,
        page_list: Optional[str] = None
    ) -> bytes:
        """
        Rotate PDF pages.

        Args:
            pdf_file: PDF file object
            angle: Rotation angle (90, 180, 270, -90)
            page_list: "all" or comma-separated pages (e.g., "1,3,5")

        Returns:
            Rotated PDF as bytes
        """
        url = f"{self.base_url}/api/v1/rotate-pdf"

        files = {"fileInput": ("input.pdf", pdf_file, "application/pdf")}
        data = {
            "angle": angle,
            "pageList": page_list or "all"
        }

        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Stirling-PDF rotate failed: {e}")
            raise

    def compress_pdf(
        self,
        pdf_file: BinaryIO,
        optimize_level: int = 2,
        expected_output_size: Optional[str] = None
    ) -> bytes:
        """
        Compress PDF file.

        Args:
            pdf_file: PDF file object
            optimize_level: 0-3 (higher = more compression)
            expected_output_size: Target size like "1MB" (optional)

        Returns:
            Compressed PDF as bytes
        """
        url = f"{self.base_url}/api/v1/compress-pdf"

        files = {"fileInput": ("input.pdf", pdf_file, "application/pdf")}
        data = {"optimizeLevel": optimize_level}

        if expected_output_size:
            data["expectedOutputSize"] = expected_output_size

        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Stirling-PDF compress failed: {e}")
            raise

    def ocr_pdf(
        self,
        pdf_file: BinaryIO,
        languages: list[str] = None,
        sidecar: bool = False
    ) -> bytes:
        """
        Apply OCR to scanned PDF.

        Args:
            pdf_file: PDF file object
            languages: List of language codes (e.g., ["eng", "deu"])
            sidecar: If True, create searchable PDF with text layer

        Returns:
            OCR'd PDF as bytes
        """
        url = f"{self.base_url}/api/v1/ocr-pdf"

        files = {"fileInput": ("input.pdf", pdf_file, "application/pdf")}
        data = {
            "languages": ",".join(languages or ["eng"]),
            "sidecar": str(sidecar).lower(),
            "ocrType": "skip-text"  # Don't re-OCR text PDFs
        }

        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=300  # OCR can be slow
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Stirling-PDF OCR failed: {e}")
            raise

    def add_watermark(
        self,
        pdf_file: BinaryIO,
        watermark_text: str,
        font_size: int = 30,
        opacity: float = 0.5,
        rotation: int = 45,
        position: str = "center"
    ) -> bytes:
        """
        Add text watermark to PDF.

        Args:
            pdf_file: PDF file object
            watermark_text: Text to display
            font_size: Font size in points
            opacity: 0.0-1.0
            rotation: Angle in degrees
            position: "center" | "top" | "bottom"

        Returns:
            Watermarked PDF as bytes
        """
        url = f"{self.base_url}/api/v1/add-watermark"

        files = {"fileInput": ("input.pdf", pdf_file, "application/pdf")}
        data = {
            "watermarkText": watermark_text,
            "fontSize": font_size,
            "opacity": opacity,
            "rotation": rotation,
            "position": position,
            "watermarkType": "text"
        }

        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Stirling-PDF watermark failed: {e}")
            raise

    def flatten_pdf(self, pdf_file: BinaryIO) -> bytes:
        """
        Flatten PDF (remove interactive elements, make static).

        Args:
            pdf_file: PDF file object

        Returns:
            Flattened PDF as bytes
        """
        url = f"{self.base_url}/api/v1/flatten"

        files = {"fileInput": ("input.pdf", pdf_file, "application/pdf")}

        try:
            response = requests.post(
                url,
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Stirling-PDF flatten failed: {e}")
            raise

    def sanitize_pdf(self, pdf_file: BinaryIO) -> bytes:
        """
        Sanitize PDF (remove metadata, scripts, attachments).

        Args:
            pdf_file: PDF file object

        Returns:
            Sanitized PDF as bytes
        """
        url = f"{self.base_url}/api/v1/sanitize-pdf"

        files = {"fileInput": ("input.pdf", pdf_file, "application/pdf")}

        try:
            response = requests.post(
                url,
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Stirling-PDF sanitize failed: {e}")
            raise

    def health_check(self) -> bool:
        """Check if Stirling-PDF service is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/info/status",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
```

## FastAPI Router Integration

**backend/app/routers/pdf_operations.py** (new file):

```python
"""PDF operations router using Stirling-PDF."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from io import BytesIO
from typing import Optional

from backend.app.services.stirling_client import StirlingPDFClient
from backend.app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["PDF Operations"])

stirling_client = StirlingPDFClient()


@router.get("/health")
async def check_pdf_service():
    """Check if PDF processing service is available."""
    if stirling_client.health_check():
        return {"status": "healthy", "service": "stirling-pdf"}
    raise HTTPException(status_code=503, detail="PDF service unavailable")


@router.post("/merge")
async def merge_pdfs(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Merge multiple PDFs into one."""
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 files required"
        )

    try:
        file_objects = [
            (f.filename, BytesIO(await f.read()))
            for f in files
        ]

        merged_pdf = stirling_client.merge_pdfs(file_objects)

        return StreamingResponse(
            BytesIO(merged_pdf),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=merged.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rotate")
async def rotate_pdf(
    file: UploadFile = File(...),
    angle: int = Form(90),
    pages: Optional[str] = Form("all"),
    db: Session = Depends(get_db)
):
    """Rotate PDF pages."""
    if angle not in [90, 180, 270, -90]:
        raise HTTPException(
            status_code=400,
            detail="Angle must be 90, 180, 270, or -90"
        )

    try:
        pdf_bytes = await file.read()
        rotated_pdf = stirling_client.rotate_pdf(
            BytesIO(pdf_bytes),
            angle=angle,
            page_list=pages
        )

        return StreamingResponse(
            BytesIO(rotated_pdf),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=rotated_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compress")
async def compress_pdf(
    file: UploadFile = File(...),
    optimize_level: int = Form(2),
    db: Session = Depends(get_db)
):
    """Compress PDF file."""
    try:
        pdf_bytes = await file.read()
        compressed_pdf = stirling_client.compress_pdf(
            BytesIO(pdf_bytes),
            optimize_level=optimize_level
        )

        return StreamingResponse(
            BytesIO(compressed_pdf),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Integration into Main App

**backend/app/main.py** (add to existing):

```python
from backend.app.routers import pdf_operations

# Add this with other router includes
app.include_router(
    pdf_operations.router,
    prefix="/pdf",
    tags=["PDF Operations"]
)
```

## Desktop App Integration

**desktop_app/api/pdf_client.py** (new file):

```python
"""PDF operations client for desktop app."""
from typing import Optional
import requests
from desktop_app.api.client import ApiClient


class PDFOperationsClient:
    """Client for PDF manipulation operations."""

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        self.base_url = api_client.base_url

    def rotate_pdf(
        self,
        filepath: str,
        angle: int = 90,
        pages: str = "all"
    ) -> bytes:
        """Rotate PDF pages."""
        url = f"{self.base_url}/pdf/rotate"

        with open(filepath, "rb") as f:
            files = {"file": (filepath, f, "application/pdf")}
            data = {"angle": angle, "pages": pages}

            resp = requests.post(
                url,
                files=files,
                data=data,
                headers=self.api_client._headers(),
                timeout=120
            )

        resp.raise_for_status()
        return resp.content

    def compress_pdf(self, filepath: str, optimize_level: int = 2) -> bytes:
        """Compress PDF file."""
        url = f"{self.base_url}/pdf/compress"

        with open(filepath, "rb") as f:
            files = {"file": (filepath, f, "application/pdf")}
            data = {"optimize_level": optimize_level}

            resp = requests.post(
                url,
                files=files,
                data=data,
                headers=self.api_client._headers(),
                timeout=120
            )

        resp.raise_for_status()
        return resp.content
```

## Phase 1 Implementation Checklist

- [ ] Add `docker-compose.yml` to repo root
- [ ] Create `backend/app/services/stirling_client.py`
- [ ] Create `backend/app/routers/pdf_operations.py`
- [ ] Add PDF router to `backend/app/main.py`
- [ ] Test Stirling-PDF container locally
- [ ] Create `desktop_app/api/pdf_client.py`
- [ ] Add UI buttons for merge/rotate/compress in desktop app
- [ ] Document API endpoints
- [ ] Add error handling and logging
- [ ] Write integration tests

## Security Considerations

1. **Network Isolation**: Keep Stirling-PDF in internal Docker network
2. **File Validation**: Validate PDF files before sending to Stirling
3. **Resource Limits**: Set memory/CPU limits in docker-compose
4. **Timeouts**: Implement proper timeouts for all operations
5. **Authentication**: Enable Stirling security in production
6. **Audit Logging**: Log all PDF operations with user context

## Performance Notes

- Stirling-PDF runs on JVM (heavier than Python but optimized for PDFs)
- For high-volume: Consider scaling with multiple Stirling containers
- Cache frequently used operations (e.g., compressed versions)
- Async processing via Celery for operations >10s

## Future Enhancements

- [ ] Pipeline API for chaining operations (merge → compress → watermark)
- [ ] Batch processing UI in desktop app
- [ ] Custom operation presets per user
- [ ] Integration with cloud storage (S3, Drive, Dropbox)
- [ ] WebSocket progress updates for long operations
