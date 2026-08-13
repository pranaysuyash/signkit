# F-003: Bulk PDF Signing - Deep Research

**Feature ID:** F-003  
**Category:** Core Functionality Enhancements  
**Priority:** HIGH  
**Complexity:** Medium  
**Status:** Research Phase  
**Estimated Effort:** 3-4 weeks  
**Document Created:** April 10, 2026  

---

## Executive Summary

Bulk PDF Signing enables users to apply signatures to multiple PDF documents simultaneously using predefined templates or consistent positioning. This feature is critical for business users who need to sign recurring document types (invoices, contracts, reports) efficiently.

### Key Benefits
- **Process 100+ documents** in minutes instead of hours
- **Consistent positioning** across all documents
- **Template-based workflows** for recurring document types
- **Significant time savings** for business users

### Business Value
- **Enterprise appeal** - Essential for business tier offering
- **Premium pricing justification** ($29 → $49-99 business tier)
- **Competitive differentiation** - Most tools lack this
- **High retention** - Power users become dependent

---

## Market Research

### Target Users

#### Primary: Small Business Owners
- Sign monthly invoices (20-50 documents)
- Sign client contracts regularly
- Need consistent professional appearance
- **Pain point:** "I spend 2 hours every month just signing PDFs"

#### Secondary: Legal/Compliance Teams
- Bulk sign NDAs, agreements
- Standardized document workflows
- Audit trail requirements
- **Pain point:** "Each signature needs to be in exact same position"

#### Tertiary: Administrative Staff
- Process employee paperwork
- Sign internal documents
- Batch approve expense reports
- **Pain point:** "Same signature, same position, 100 times"

### Competitor Analysis

| Product | Bulk Signing | Features | Limitations |
|---------|--------------|----------|-------------|
| **Adobe Acrobat** | Limited | Actions wizard | Complex setup, expensive |
| **DocuSign** | Yes | Templates, bulk send | $25+/user/month, web-only |
| **HelloSign** | Yes | Templates | $15+/month, limited offline |
| **Smallpdf** | No | N/A | Single file only |
| **PDFelement** | Limited | Batch processing | $79/year, UI confusing |
| **SignNow** | Yes | Templates | Subscription model |

### Market Gap
**No desktop app offers:**
- True offline bulk signing
- One-time purchase (no subscription)
- Template-based positioning
- Progress tracking and resume
- Affordable pricing

---

## Technical Specification

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Bulk Signing System                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   Template Creation                                           │
│   ┌──────────────┐     ┌──────────────┐                     │
│   │ Define Pos   │────▶│ Save Pattern │────▶ Templates DB   │
│   │ (Sample PDF) │     │ (JSON/YAML)  │                     │
│   └──────────────┘     └──────────────┘                     │
│          │                                                   │
│          ▼                                                   │
│   Bulk Processing                                            │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│   │ File Queue   │────▶│ Coordinate   │────▶│ PDF Engine   ││
│   │ (Discovery)  │     │ Mapping      │     │ (Signing)    ││
│   └──────────────┘     └──────────────┘     └──────────────┘│
│          │                      │                    │       │
│          ▼                      ▼                    ▼       │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│   │ Progress UI  │◀────│ State Mgmt   │◀────│ Output       ││
│   │ (Real-time)  │     │ (Resume)     │     │ (Export)     ││
│   └──────────────┘     └──────────────┘     └──────────────┘│
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Template System
```python
@dataclass
class SignatureTemplate:
    """Template defining signature position and appearance."""
    
    id: str
    name: str
    description: str
    created_at: datetime
    modified_at: datetime
    
    # Positioning
    position_type: PositionType  # ABSOLUTE, RELATIVE, FIELD_BASED
    
    # For absolute positioning (fixed coordinates)
    absolute_position: Optional[AbsolutePosition]
    
    # For relative positioning (percentages)
    relative_position: Optional[RelativePosition]
    
    # For field-based positioning (find signature field)
    field_name: Optional[str]
    field_search_pattern: Optional[str]
    
    # Signature settings
    signature_id: str  # Reference to vault signature
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    
    # Page settings
    page_numbers: List[int]  # [0] = first page, [-1] = all pages
    page_filter: Optional[str]  # "odd", "even", "last"
    
    # Document matching (auto-apply template)
    doc_patterns: List[str]  # Filename patterns
    page_count_range: Optional[Tuple[int, int]]
    
@dataclass
class AbsolutePosition:
    x: float  # Points (1/72 inch)
    y: float
    width: Optional[float]
    height: Optional[float]
    page_width: float  # Original page dimensions
    page_height: float
    
@dataclass
class RelativePosition:
    x_percent: float  # 0.0 to 1.0 (left to right)
    y_percent: float  # 0.0 to 1.0 (bottom to top)
    width_percent: Optional[float]
    height_percent: Optional[float]
    anchor: AnchorPoint  # TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, etc.

class PositionType(Enum):
    ABSOLUTE = "absolute"  # Fixed PDF coordinates
    RELATIVE = "relative"  # Percentage-based
    FIELD_BASED = "field"  # Find and replace form field
    SMART = "smart"        # AI-based detection (future)
```

#### 2. Coordinate Mapping System
```python
class CoordinateMapper:
    """Maps template coordinates to different PDF sizes/orientations."""
    
    def map_position(
        self,
        template: SignatureTemplate,
        target_pdf: PdfDocument
    ) -> AbsolutePosition:
        """Convert template position to target PDF coordinates."""
        
        if template.position_type == PositionType.ABSOLUTE:
            return self._map_absolute(template.absolute_position, target_pdf)
        
        elif template.position_type == PositionType.RELATIVE:
            return self._map_relative(template.relative_position, target_pdf)
        
        elif template.position_type == PositionType.FIELD_BASED:
            return self._find_field_position(template.field_name, target_pdf)
    
    def _map_absolute(
        self,
        source: AbsolutePosition,
        target: PdfDocument
    ) -> AbsolutePosition:
        """Map absolute coordinates accounting for page size differences."""
        # Scale factor based on page dimensions
        scale_x = target.page_width / source.page_width
        scale_y = target.page_height / source.page_height
        
        # Use uniform scaling to preserve aspect ratio
        scale = min(scale_x, scale_y)
        
        return AbsolutePosition(
            x=source.x * scale,
            y=source.y * scale,
            width=source.width * scale if source.width else None,
            height=source.height * scale if source.height else None,
            page_width=target.page_width,
            page_height=target.page_height
        )
    
    def _map_relative(
        self,
        source: RelativePosition,
        target: PdfDocument
    ) -> AbsolutePosition:
        """Convert percentage-based to absolute coordinates."""
        x = source.x_percent * target.page_width
        y = source.y_percent * target.page_height
        
        # Adjust for anchor point
        if source.anchor in [AnchorPoint.TOP_RIGHT, AnchorPoint.BOTTOM_RIGHT]:
            # Anchor is right side
            pass
        
        return AbsolutePosition(
            x=x,
            y=y,
            width=source.width_percent * target.page_width if source.width_percent else None,
            height=source.height_percent * target.page_height if source.height_percent else None,
            page_width=target.page_width,
            page_height=target.page_height
        )
```

#### 3. Bulk Processing Engine
```python
class BulkSigningEngine:
    """Engine for processing multiple PDFs with templates."""
    
    def __init__(self, pdf_engine: PdfEngine, vault: NotaryVault):
        self.pdf_engine = pdf_engine
        self.vault = vault
        self.coordinate_mapper = CoordinateMapper()
    
    def create_job(
        self,
        files: List[Path],
        template: SignatureTemplate,
        output_dir: Path,
        settings: BulkSigningSettings
    ) -> BulkJob:
        """Create new bulk signing job."""
        
    def process_job(
        self,
        job_id: str,
        progress_callback: Callable[[int, int, str], None]
    ) -> BulkResult:
        """Process bulk signing job with progress updates."""
        
        job = self._load_job(job_id)
        results = []
        
        for idx, file_path in enumerate(job.files):
            try:
                # Update progress
                progress_callback(idx, len(job.files), file_path.name)
                
                # Load PDF
                pdf = self.pdf_engine.load_pdf(file_path)
                
                # Map coordinates for each page
                for page_num in template.page_numbers:
                    position = self.coordinate_mapper.map_position(
                        template, 
                        pdf.get_page(page_num)
                    )
                    
                    # Get signature from vault
                    signature = self.vault.get_signature(template.signature_id)
                    
                    # Apply signature
                    pdf.add_signature(
                        page=page_num,
                        image=signature,
                        position=position,
                        scale=template.scale
                    )
                
                # Save output
                output_path = self._generate_output_path(
                    file_path, 
                    job.output_dir,
                    job.settings
                )
                pdf.save(output_path)
                
                results.append(BulkFileResult(
                    input_path=file_path,
                    output_path=output_path,
                    status=Status.SUCCESS,
                    pages_signed=len(template.page_numbers)
                ))
                
            except Exception as e:
                results.append(BulkFileResult(
                    input_path=file_path,
                    status=Status.FAILED,
                    error=str(e)
                ))
                
                if not job.settings.continue_on_error:
                    break
        
        return BulkResult(
            job_id=job_id,
            total_files=len(job.files),
            successful=len([r for r in results if r.status == Status.SUCCESS]),
            failed=len([r for r in results if r.status == Status.FAILED]),
            results=results
        )
```

#### 4. Template Editor
```python
class TemplateEditorDialog(QDialog):
    """Dialog for creating and editing signature templates."""
    
    def __init__(self, pdf_engine: PdfEngine, parent=None):
        super().__init__(parent)
        self.pdf_engine = pdf_engine
        self.template = SignatureTemplate()
        self._setup_ui()
    
    def _setup_ui(self):
        """Create template editor interface."""
        # Sample PDF viewer
        self.pdf_viewer = PdfViewer()
        
        # Signature selector
        self.sig_selector = SignatureSelector()
        
        # Position controls
        self.position_tabs = QTabWidget()
        self.position_tabs.addTab(self._create_absolute_tab(), "Absolute")
        self.position_tabs.addTab(self._create_relative_tab(), "Relative")
        self.position_tabs.addTab(self._create_field_tab(), "Form Field")
        
        # Preview area
        self.preview_btn = QPushButton("Preview on Sample")
        
        # Save controls
        self.template_name = QLineEdit()
        self.save_btn = QPushButton("Save Template")
    
    def _create_absolute_tab(self):
        """Create absolute positioning controls."""
        widget = QWidget()
        layout = QFormLayout()
        
        self.abs_x = QDoubleSpinBox()
        self.abs_x.setSuffix(" pt")
        self.abs_x.setRange(0, 10000)
        
        self.abs_y = QDoubleSpinBox()
        self.abs_y.setSuffix(" pt")
        self.abs_y.setRange(0, 10000)
        
        self.abs_width = QDoubleSpinBox()
        self.abs_width.setSuffix(" pt")
        
        self.abs_height = QDoubleSpinBox()
        self.abs_height.setSuffix(" pt")
        
        layout.addRow("X Position:", self.abs_x)
        layout.addRow("Y Position:", self.abs_y)
        layout.addRow("Width:", self.abs_width)
        layout.addRow("Height:", self.abs_height)
        
        # Visual selector button
        self.visual_select_btn = QPushButton("Select Position Visually...")
        self.visual_select_btn.clicked.connect(self._open_visual_selector)
        layout.addRow(self.visual_select_btn)
        
        widget.setLayout(layout)
        return widget
```

---

## User Stories

### Story 1: Monthly Invoice Processing
**As a** small business owner  
**I want to** sign 30 invoices at once  
**So that** I don't spend an hour on repetitive work  

**Workflow:**
1. Select folder of invoices
2. Choose "Invoice Template" (signature at bottom right)
3. Preview on first invoice to confirm
4. Process all 30 invoices
5. Review results summary

**Acceptance Criteria:**
- Can select folder of PDFs
- Templates remember exact position
- Batch completes in under 5 minutes
- Failed files listed with errors

### Story 2: Contract Template
**As a** legal professional  
**I want to** save signature positions for contracts  
**So that** all my contracts look consistent  

**Workflow:**
1. Open sample contract
2. Place signature on signature line
3. Save as "Standard Contract Template"
4. Apply template to future contracts

**Acceptance Criteria:**
- Templates persist across sessions
- Can create multiple templates
- Can edit existing templates
- Template applies to different page sizes

### Story 3: Error Recovery
**As an** administrative assistant  
**I want to** pause and resume bulk signing  
**So that** I don't lose progress if interrupted  

**Acceptance Criteria:**
- Can pause during processing
- Resume from where left off
- Progress saved automatically
- Can cancel remaining files

---

## Implementation Plan

### Phase 1: Template Foundation (Week 1)
- [ ] Design template data structures
- [ ] Create coordinate mapping system
- [ ] Implement absolute positioning
- [ ] Template storage (JSON/SQLite)
- [ ] Basic template CRUD operations

**Deliverable:** Can save and load templates

### Phase 2: Core Engine (Week 2)
- [ ] Refactor PDF engine for batch operations
- [ ] Implement bulk processing loop
- [ ] Progress tracking and reporting
- [ ] Error handling and recovery
- [ ] Coordinate transformation logic

**Deliverable:** Can process multiple PDFs

### Phase 3: Template Editor (Week 2-3)
- [ ] Visual template editor dialog
- [ ] Position selection tools
- [ ] Preview functionality
- [ ] Template management UI
- [ ] Import/export templates

**Deliverable:** User-friendly template creation

### Phase 4: Batch UI (Week 3)
- [ ] File/folder selection dialog
- [ ] Template chooser
- [ ] Progress dialog with details
- [ ] Results summary view
- [ ] Export/retry failed files

**Deliverable:** Complete user workflow

### Phase 5: Advanced Features (Week 4)
- [ ] Relative positioning
- [ ] Field-based positioning
- [ ] Auto-template matching
- [ ] Conditional logic (e.g., page count)
- [ ] Performance optimizations

**Deliverable:** Advanced template capabilities

### Phase 6: Testing & Polish (Week 4-5)
- [ ] Test with 100+ file batches
- [ ] Edge case handling
- [ ] Performance profiling
- [ ] Documentation
- [ ] User acceptance testing

**Deliverable:** Production-ready feature

---

## Testing Strategy

### Test Scenarios
1. **Single template, multiple files**
2. **Different page sizes** (A4, Letter, Legal)
3. **Different orientations** (portrait, landscape)
4. **Large batches** (100+ files)
5. **Mixed success/failure**
6. **Resume interrupted batch**

### Performance Targets
- Process 50 files in <3 minutes
- Memory usage <200MB for 100 files
- Template creation <30 seconds

---

## Success Metrics

### User Adoption
- **Target:** 60% of business users use bulk signing
- **Measurement:** Feature usage analytics
- **Success:** >50% adoption

### Time Savings
- **Target:** 90% time reduction vs manual signing
- **Measurement:** User surveys
- **Success:** Users report significant time savings

### Template Usage
- **Target:** Average 3 templates per power user
- **Measurement:** Template creation stats
- **Success:** Templates actively used

---

## Business Model Impact

### Pricing Strategy
**Current:** $29 one-time  
**Proposed Tiers:**
- **Basic ($29):** Single-file signing only
- **Professional ($49):** Bulk signing (up to 10 files)
- **Business ($99):** Unlimited bulk + templates

### Revenue Projection
- 20% of users upgrade to Professional
- 10% of users upgrade to Business
- **Estimated revenue increase:** +40%

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Complex template UI | High | Iterative design, user testing |
| Coordinate errors | High | Preview mode, validation |
| Performance issues | Medium | Streaming, lazy loading |
| File corruption | High | Backup originals, validation |

---

**Document Status:** Complete  
**Next Review:** May 10, 2026