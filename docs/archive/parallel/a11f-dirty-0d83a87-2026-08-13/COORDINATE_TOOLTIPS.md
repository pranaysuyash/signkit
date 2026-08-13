# Coordinate Tooltips Feature

## Overview

The signature library now displays comprehensive information about each signature as tooltips when you hover over them. This feature provides detailed metadata about signatures in both the **Extraction tab** and the **PDF Signing tab**.

## What Information Is Displayed

### For ALL Signatures (Always Available)

Every signature in the library shows at minimum:

```
File: signature_20251031_143022.png
Modified: 2025-10-31 14:30
Image Size: 497 × 158 px
Mode: RGBA
File Size: 12.3 KB
```

**Fields:**

- **File**: The filename of the signature image
- **Modified**: When the signature was last saved/modified
- **Image Size**: Actual pixel dimensions of the saved signature image
- **Mode**: Image color mode (RGBA for transparency, RGB for opaque)
- **File Size**: Size on disk (B, KB, or MB)

### For Signatures with Extraction Metadata (Additional Info)

If a signature was extracted and saved with metadata, you'll also see:

```
Extraction Info:
  Selection: (150, 200) → (450, 350)
  Selection Size: 300 × 150 px
  Source Image: 1200 × 800 px
  Color: #0000ff
  Threshold: 128
  Session: bc4e90b8-5f67-48b4...
```

**Additional Fields:**

- **Selection**: The coordinates in the source image where this signature was selected
  - Format: `(x1, y1) → (x2, y2)` where (x1, y1) is top-left and (x2, y2) is bottom-right
- **Selection Size**: Width and height of the selection in source pixels
- **Source Image**: Dimensions of the original document/image it was extracted from
- **Color**: The hex color code used for extraction/recoloring
- **Threshold**: The background removal threshold value (0-255)
- **Session**: Backend session ID (truncated for readability)

## How It Works

### 1. Saving with Metadata

When you click **"Save to Library"** in the Extraction tab:

1. The current signature PNG is saved to `~/.signature_extractor/signatures/`
2. A JSON sidecar file is automatically created with the same name:
   ```
   signature_20251031_143022.png
   signature_20251031_143022.json  ← metadata
   ```
3. The JSON contains extraction parameters:
   ```json
   {
     "session_id": "bc4e90b8-5f67-48b4-b7b6-b6f9f47e6337",
     "selection": {
       "x1": 150,
       "y1": 200,
       "x2": 450,
       "y2": 350
     },
     "threshold": 128,
     "color": "#0000ff",
     "image_size": {
       "width": 1200,
       "height": 800
     }
   }
   ```

### 2. Loading with Tooltips

When the library list is refreshed (automatically or via "🔄 Refresh" button):

1. **For each signature image**, the system:

   - Loads the PNG file
   - Opens it with PIL to read actual dimensions and color mode
   - Calculates file size
   - Checks for a matching `.json` sidecar file
   - If found, loads extraction metadata

2. **Tooltip is generated** combining:

   - Always: File info, image dimensions, file size
   - If available: Extraction coordinates and parameters

3. **Displayed in both tabs**:
   - **Extraction tab**: "My Signatures" library list
   - **PDF Signing tab**: "Signature Library" list

## Use Cases

### 1. Quality Control

Hover to verify extraction parameters before using a signature:

- Check if selection was precise
- Verify color and threshold settings
- Confirm image dimensions match expectations

### 2. Reprocessing Decisions

Use coordinate info to decide if re-extraction is needed:

- If selection was too tight/loose, extract again
- If threshold was too aggressive, adjust and re-save

### 3. Troubleshooting

Debug placement issues by checking:

- Image mode (RGBA vs RGB) for transparency issues
- File size for quality concerns
- Source dimensions for scaling context

### 4. Organization

Identify signatures by their extraction context:

- Which document they came from (via source size)
- When they were created (modified date)
- What settings produced the best results

## Technical Details

### Storage Location

```
~/.signature_extractor/
└── signatures/
    ├── signature_20251031_143022.png      ← Image file
    ├── signature_20251031_143022.json     ← Metadata (optional)
    ├── signature_20251031_150134.png
    └── signature_20251031_150134.json
```

### Metadata Schema

```json
{
  "session_id": "string (UUID)",
  "selection": {
    "x1": "int (left)",
    "y1": "int (top)",
    "x2": "int (right)",
    "y2": "int (bottom)"
  },
  "threshold": "int (0-255)",
  "color": "string (hex #RRGGBB)",
  "image_size": {
    "width": "int (pixels)",
    "height": "int (pixels)"
  }
}
```

### Coordinate System

- **Selection coordinates**: Top-left origin (Qt/PIL convention)
  - (0, 0) is top-left corner of source image
  - x increases rightward, y increases downward
- **All values in pixels** of the original source image
- Independent of display zoom/scaling

### Backwards Compatibility

- **Old signatures without JSON**: Still work perfectly
  - Show file info and image dimensions (loaded from PNG)
  - Just missing extraction metadata section
- **Manual additions**: Any PNG added to the folder manually will appear
  - System will read dimensions from the file
  - No extraction metadata shown (none exists)

## Implementation Files

| File                               | Purpose                                          |
| ---------------------------------- | ------------------------------------------------ |
| `desktop_app/library/storage.py`   | Metadata save/load, tooltip generation           |
| `desktop_app/views/main_window.py` | Save with metadata, apply tooltips to list items |

### Key Functions

**`save_png_to_library(png_bytes, metadata=None)`**

- Saves PNG and optional JSON sidecar
- Called from "Save to Library" action

**`LibraryItem.tooltip_text`**

- Property that generates tooltip text
- Combines file info + metadata if available

**`list_items(limit=50)`**

- Lists library items with loaded metadata
- Automatically finds and reads JSON sidecars

## Example Tooltip Output

### With Full Metadata:

```
File: signature_20251031_143022.png
Modified: 2025-10-31 14:30
Image Size: 497 × 158 px
Mode: RGBA
File Size: 12.3 KB

Extraction Info:
  Selection: (150, 200) → (450, 350)
  Selection Size: 300 × 150 px
  Source Image: 1200 × 800 px
  Color: #0000ff
  Threshold: 128
  Session: bc4e90b8-5f67-48b4...
```

### Without Metadata:

```
File: old_signature.png
Modified: 2025-10-15 09:45
Image Size: 320 × 120 px
Mode: RGB
File Size: 8.7 KB
```

## Future Enhancements

Potential additions to tooltips:

- **Preview thumbnail** in tooltip (Qt supports rich tooltips)
- **Usage count** (how many times signature was used)
- **Associated documents** (PDFs where this signature appears)
- **Quality score** (based on resolution, clarity)
- **Tags/categories** for organization
- **Edit history** (if signature was modified)

## Related Documentation

- **Coordinate Mapping**: `docs/COORDINATE_MAPPING.md`
- **Library Management**: `docs/TODO.md` (Library behavior section)
- **PDF Signing**: `docs/PDF_FEATURE_IMPLEMENTATION.md`
- **Extraction Flow**: `docs/desktop-frontend/pyqt-spec.md`
