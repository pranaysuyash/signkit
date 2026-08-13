# F-001: Batch Processing - Deep Research

**Feature ID:** F-001  
**Category:** Core Functionality Enhancements  
**Priority:** HIGH  
**Complexity:** Medium  
**Status:** Research Phase  
**Estimated Effort:** 2-3 weeks  
**Document Created:** April 10, 2026  

---

## Executive Summary

Batch Processing allows users to process multiple signature images simultaneously using shared extraction settings. This feature dramatically improves productivity for users who need to digitize multiple signatures from documents like contracts, forms, or scanned paperwork.

### Key Benefits
- **10x productivity improvement** for users processing multiple signatures
- Reduces repetitive threshold/color adjustments
- Enables bulk digitization workflows for businesses
- Builds foundation for bulk PDF signing workflows

### Business Value
- Attracts business/enterprise users
- Justifies higher price point ($29 → $49+ for business tier)
- Differentiates from single-file competitors
- Increases user engagement and retention

---

## Market Research

### Competitor Analysis

| Product | Batch Support | Limitations | User Feedback |
|---------|---------------|-------------|---------------|
| **DocuSign** | Limited | Web-only, subscription model | "Too expensive for small batch work" |
| **Adobe Acrobat** | Yes | Complex UI, subscription required | "Overkill for simple signature extraction" |
| **Smallpdf** | No | Single file only | Users request batch feature frequently |
| **SignNow** | Limited | Web-based only | "Need offline batch processing" |
| **PDFelement** | Yes | Expensive ($79/year) | "Good but too costly" |

### User Pain Points (from reviews & forums)
1. **"I have 50 signed documents to process"** - Manual processing takes hours
2. **"Same threshold settings for each file"** - Repetitive configuration
3. **"No way to queue multiple files"** - Forces sequential workflow
4. **"Need to extract signatures from entire folder"** - Bulk import needed

### Industry Standards
- Batch processing is expected in professional tools
- Drag-and-drop folder support is standard
- Progress indicators are essential for UX
- Cancel/resume capability improves trust

---

## Technical Specification

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Batch Processing Flow                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │ File Scanner │────▶│ Job Queue    │────▶│  Workers     │ │
│  │ (Discovery)  │     │ (Priority)   │     │ (Processing) │ │
│  └──────────────┘     └──────────────┘     └──────────────┘ │
│         │                      │                    │        │
│         ▼                      ▼                    ▼        │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │ Progress UI  │◀────│ State Mgmt   │◀────│ Results      │ │
│  │ (Real-time)  │     │ (Resume)     │     │ (Export)     │ │
│  └──────────────┘     └──────────────┘     └──────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. File Discovery Module
```python
class BatchFileDiscovery:
    """Scans directories and validates batch input files."""
    
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    MAX_BATCH_SIZE = 100  # Files per batch
    MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500MB total
    
    def scan_directory(self, path: Path, recursive: bool = False) -> List[Path]:
        """Discover and validate image files."""
        
    def validate_batch(self, files: List[Path]) -> ValidationResult:
        """Check file count, sizes, and formats."""
        
    def preview_thumbnails(self, files: List[Path]) -> List[Thumbnail]:
        """Generate quick previews for UI."""
```

#### 2. Job Queue System
```python
@dataclass
class BatchJob:
    """Represents a single processing job."""
    id: str
    file_path: Path
    status: JobStatus  # PENDING, PROCESSING, COMPLETED, FAILED
    priority: int
    settings: ProcessingSettings
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[ProcessingResult]
    error: Optional[str]

class BatchJobQueue:
    """Manages job queue with priority and resume support."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.jobs: Dict[str, BatchJob] = {}
        self.queue: PriorityQueue = PriorityQueue()
        
    def enqueue(self, job: BatchJob) -> None:
        """Add job to queue with priority."""
        
    def process_queue(self, callback: Callable) -> None:
        """Process jobs with progress callback."""
        
    def pause(self) -> None:
        """Pause processing (resumeable)."""
        
    def cancel(self, job_id: str) -> None:
        """Cancel specific job."""
        
    def export_state(self) -> dict:
        """Export for resume capability."""
```

#### 3. Worker Pool
```python
class BatchWorkerPool:
    """Multi-threaded processing workers."""
    
    def __init__(self, extractor: SignatureExtractor, num_workers: int = 4):
        self.extractor = extractor
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.futures: Dict[str, Future] = {}
        
    def submit_job(self, job: BatchJob) -> Future:
        """Submit job to worker pool."""
        
    def process_single(self, job: BatchJob) -> ProcessingResult:
        """Process individual file."""
        # 1. Load image
        # 2. Apply shared settings
        # 3. Run extraction
        # 4. Apply quality checks
        # 5. Save result
        
    def cancel_all(self) -> None:
        """Cancel all pending and running jobs."""
```

#### 4. Settings Management
```python
@dataclass
class BatchProcessingSettings:
    """Shared settings applied to all files in batch."""
    
    # Extraction parameters
    threshold: int = 128
    color: str = "#000000"
    auto_clean: bool = False
    use_ai_detection: bool = True
    
    # Output settings
    output_format: OutputFormat = OutputFormat.PNG
    output_prefix: str = "signature_"
    output_suffix: str = "{timestamp}"
    preserve_filenames: bool = True
    
    # Quality settings
    min_quality_score: int = 50
    reject_low_quality: bool = False
    
    # Organization
    create_subfolders: bool = False
    organize_by_date: bool = False
    
    # Naming patterns
    def generate_filename(self, original: Path, index: int) -> str:
        """Generate output filename based on pattern."""
```

### Data Flow

```python
# User initiates batch processing
def start_batch_process(input_paths: List[Path], settings: BatchProcessingSettings):
    
    # 1. Discovery Phase
    files = file_discovery.scan_batch(input_paths)
    if not files.valid:
        show_validation_errors(files.errors)
        return
    
    # 2. Preview Phase
    thumbnails = generate_thumbnails(files.paths)
    show_preview_dialog(thumbnails, settings)
    
    # 3. Queue Phase
    jobs = create_jobs(files.paths, settings)
    job_queue.enqueue_batch(jobs)
    
    # 4. Processing Phase
    show_progress_dialog(job_queue)
    worker_pool.process_queue(
        on_progress=update_ui,
        on_complete=handle_completion,
        on_error=handle_error
    )
    
    # 5. Results Phase
    show_results_summary(completed_jobs)
    export_results(completed_jobs, settings.output_directory)
```

---

## User Stories

### Story 1: Business Administrator
**As a** business administrator processing employee documents  
**I want to** process 50 signed forms at once  
**So that** I can extract all signatures in one operation  

**Acceptance Criteria:**
- Can select entire folder of images
- Can preview all files before processing
- Can apply same threshold/color to all
- Can export all signatures with sequential naming
- Processing completes within 5 minutes

### Story 2: Legal Professional
**As a** legal professional digitizing case files  
**I want to** queue multiple signature extractions  
**So that** I can continue working while batch processes  

**Acceptance Criteria:**
- Background processing doesn't block UI
- Can pause and resume batch
- Progress shown in system tray
- Results saved automatically

### Story 3: Quality Assurance
**As a** QA manager reviewing signatures  
**I want to** reject low-quality extractions automatically  
**So that** only good signatures are kept  

**Acceptance Criteria:**
- Quality threshold setting (0-100)
- Low-quality signatures flagged
- Option to re-process with different settings
- Quality report generated

---

## Implementation Plan

### Phase 1: Foundation (Week 1)
- [ ] Create batch processing module structure
- [ ] Implement file discovery and validation
- [ ] Design settings management system
- [ ] Create database schema for batch jobs
- [ ] Unit tests for discovery module

**Deliverable:** Batch discovery working, can scan folders

### Phase 2: Core Processing (Week 2)
- [ ] Implement job queue with priority
- [ ] Create worker pool with thread management
- [ ] Integrate with existing SignatureExtractor
- [ ] Add progress tracking and reporting
- [ ] Implement pause/resume functionality
- [ ] Error handling and recovery

**Deliverable:** Can process multiple files sequentially

### Phase 3: UI/UX (Week 2-3)
- [ ] Design batch dialog interface
- [ ] Create file list with thumbnails
- [ ] Implement settings panel
- [ ] Build progress dialog with real-time updates
- [ ] Add results summary view
- [ ] Export options dialog

**Deliverable:** Full UI for batch processing workflow

### Phase 4: Advanced Features (Week 3)
- [ ] Parallel processing optimization
- [ ] Resume capability from saved state
- [ ] Quality-based auto-rejection
- [ ] Naming pattern customization
- [ ] Performance optimizations

**Deliverable:** Production-ready batch processing

### Phase 5: Testing & Polish (Week 4)
- [ ] Load testing with 100+ files
- [ ] Edge case handling
- [ ] Performance profiling
- [ ] Documentation
- [ ] User acceptance testing

**Deliverable:** Released feature

---

## Testing Strategy

### Unit Tests
```python
# File discovery tests
def test_scan_directory_recursive():
def test_validate_batch_size_limits():
def test_filter_unsupported_formats():

# Job queue tests
def test_priority_queue_ordering():
def test_pause_resume_functionality():
def test_cancel_running_job():

# Worker tests
def test_process_single_file():
def test_handle_corrupted_image():
def test_memory_cleanup():
```

### Integration Tests
```python
def test_end_to_end_batch_workflow():
def test_resume_interrupted_batch():
def test_concurrent_batch_operations():
def test_error_recovery():
```

### Performance Tests
- Process 100 files (various sizes)
- Memory usage profiling
- CPU utilization optimization
- Disk I/O optimization

### Edge Cases
- Empty folders
- Corrupted images mixed with valid
- Very large images (50MB+)
- Network drives (if applicable)
- Unicode filenames
- Deeply nested directories

---

## Success Metrics

### User Adoption
- **Target:** 40% of users try batch processing within 3 months
- **Measurement:** Track batch operation usage
- **Success:** >60% of power users adopt feature

### Performance
- **Target:** Process 10 files/minute on average hardware
- **Measurement:** Benchmark processing speed
- **Success:** <6 seconds per file average

### Quality
- **Target:** <2% error rate on valid images
- **Measurement:** Track failed extractions
- **Success:** 98%+ success rate

### User Satisfaction
- **Target:** 4.5/5 rating for batch feature
- **Measurement:** In-app feedback + support tickets
- **Success:** Feature mentioned positively in reviews

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Memory exhaustion** | High | Medium | Limit concurrent workers, stream processing |
| **UI freezing** | High | Low | Use background threads, async UI updates |
| **Data loss on crash** | Medium | Low | Auto-save progress every 30 seconds |
| **Slow performance** | Medium | High | Optimize with preview caching, lazy loading |
| **User confusion** | Low | Medium | Clear progress indicators, help tooltips |
| **File system errors** | Medium | Low | Robust error handling, permission checks |

---

## API Design

### Public Interface
```python
class BatchProcessor:
    """Main interface for batch processing operations."""
    
    def __init__(self, extractor: SignatureExtractor):
        self.extractor = extractor
        self.queue = BatchJobQueue()
        self.workers = BatchWorkerPool(extractor)
    
    def create_batch(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Union[str, Path],
        settings: Optional[BatchProcessingSettings] = None
    ) -> BatchJob:
        """Create new batch job."""
    
    def start_batch(self, batch_id: str) -> None:
        """Start processing batch."""
    
    def pause_batch(self, batch_id: str) -> None:
        """Pause active batch."""
    
    def resume_batch(self, batch_id: str) -> None:
        """Resume paused batch."""
    
    def cancel_batch(self, batch_id: str) -> None:
        """Cancel batch and cleanup."""
    
    def get_progress(self, batch_id: str) -> BatchProgress:
        """Get current progress information."""
    
    def list_batches(self) -> List[BatchJob]:
        """List all batches (active and historical)."""
```

### Events
```python
class BatchProcessorSignals(QObject):
    """Qt signals for UI integration."""
    
    progress_updated = Signal(str, int, int)  # batch_id, completed, total
    job_completed = Signal(str, str)  # batch_id, job_id
    job_failed = Signal(str, str, str)  # batch_id, job_id, error
    batch_completed = Signal(str)  # batch_id
    batch_failed = Signal(str, str)  # batch_id, error
```

---

## UI/UX Design

### Batch Dialog Layout
```
┌──────────────────────────────────────────────────────────────┐
│ Batch Processing                                 [?] [✕]    │
├──────────────────────────────────────────────────────────────┤
│ Settings:                                                    │
│ ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐   │
│ │ Threshold: 128   │  │ Color: #000000   │  │ Auto ✓   │   │
│ └──────────────────┘  └──────────────────┘  └──────────┘   │
├──────────────────────────────────────────────────────────────┤
│ Files to Process (47):                                       │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ [📄] contract_001.jpg    ✓ Preview    Status: Ready    │  │
│ │ [📄] contract_002.jpg    ✓ Preview    Status: Ready    │  │
│ │ [📄] contract_003.jpg    ✓ Preview    Status: Ready    │  │
│ │     ... 44 more files                                  │  │
│ └─────────────────────────────────────────────────────────┘  │
│ [+ Add Files]  [+ Add Folder]  [🗑 Clear All]               │
├──────────────────────────────────────────────────────────────┤
│ Output: /Users/.../signatures  [Browse...]                   │
│ Naming: {original}_{timestamp}.png  [Customize...]          │
├──────────────────────────────────────────────────────────────┤
│ Quality: Skip signatures with score < 50  [?]                │
│ Create subfolders by date: [ ]                               │
├──────────────────────────────────────────────────────────────┤
│                      [Start Batch Processing]                │
└──────────────────────────────────────────────────────────────┘
```

### Progress Dialog
```
┌──────────────────────────────────────────────────────────────┐
│ Processing Batch...                              [⏸] [✕]    │
├──────────────────────────────────────────────────────────────┤
│ ████████████████░░░░░░░░  34/47 files (72%)                  │
│                                                              │
│ Current: contract_034.jpg                                    │
│ Status: Extracting signature...                              │
│                                                              │
│ Completed: 33 ✓                                              │
│ Failed: 1 ✗                                                  │
│ Remaining: 13                                                │
│                                                              │
│ Time elapsed: 2:34  |  Est. remaining: 0:56                  │
│                                                              │
│ [View Details]  [Cancel Remaining]                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Database Schema

```sql
-- Batch jobs table
CREATE TABLE batch_jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,  -- PENDING, RUNNING, PAUSED, COMPLETED, FAILED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_files INTEGER,
    completed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    settings_json TEXT,  -- JSON serialized BatchProcessingSettings
    output_directory TEXT,
    error_message TEXT
);

-- Individual file jobs
CREATE TABLE batch_job_files (
    id TEXT PRIMARY KEY,
    batch_id TEXT REFERENCES batch_jobs(id),
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    status TEXT NOT NULL,  -- PENDING, PROCESSING, COMPLETED, FAILED
    result_path TEXT,
    quality_score INTEGER,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## References

### Technical References
- [Python ThreadPoolExecutor Documentation](https://docs.python.org/3/library/concurrent.futures.html)
- [Qt Concurrent Programming Guide](https://doc.qt.io/qt-6/qtconcurrent-index.html)
- [OpenCV Batch Processing Patterns](https://docs.opencv.org/)

### User Research
- [G2 Crowd PDF Software Reviews](https://www.g2.com/categories/pdf-editor)
- [Reddit r/pdf discussions on batch processing](https://reddit.com/r/pdf)
- [SignKit User Feedback Survey Q1 2026]

### Similar Implementations
- Adobe Lightroom batch export
- HandBrake batch transcoding
- ImageMagick batch processing

---

## Decision Log

| Date | Decision | Rationale | Alternatives Rejected |
|------|----------|-----------|----------------------|
| 2026-04-10 | Use ThreadPoolExecutor | Simple, built-in, works with existing code | ProcessPool (overhead), Asyncio (complexity) |
| 2026-04-10 | Max 4 concurrent workers | Balance between speed and resource usage | 2 (too slow), 8 (too much RAM) |
| 2026-04-10 | SQLite for job persistence | Simple, no external dependencies | PostgreSQL (overkill), JSON file (unreliable) |

---

## Open Questions

1. Should we support processing PDFs directly (extract signatures from PDF pages)?
2. Do users need different settings per file type (photo vs scanned)?
3. Should batch processing be available via command line for automation?
4. Do we need cloud integration for batch jobs (process on server)?

---

**Document Status:** Complete  
**Next Review:** May 10, 2026  
**Owner:** Development Team  
**Stakeholders:** Product, UX, Engineering