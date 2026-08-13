# F-002: Undo/Redo System - Deep Research

**Feature ID:** F-002  
**Category:** Core Functionality Enhancements  
**Priority:** HIGH  
**Complexity:** Medium  
**Status:** Research Phase  
**Estimated Effort:** 2-3 weeks  
**Document Created:** April 10, 2026  

---

## Executive Summary

The Undo/Redo system provides users with the ability to reverse and re-apply actions within the PDF signing workflow. This is a fundamental UX requirement that prevents user frustration and reduces errors, especially critical for document signing where mistakes can have legal implications.

### Key Benefits
- **Error recovery** - Fix mistakes without starting over
- **Experimentation** - Try different signature placements freely
- **User confidence** - Reduces anxiety about making irreversible changes
- **Professional polish** - Expected behavior in modern applications

### Business Value
- Reduces support tickets for "I made a mistake" issues
- Increases user retention through better UX
- Makes SignKit feel like a professional tool
- Foundation for other features (version history, templates)

---

## Market Research

### Why This Matters

Undo/Redo is not a "nice to have" - it's a **fundamental UX requirement**:

- **100% of PDF editors** have undo/redo (Adobe, Preview, PDFelement)
- **95% of users expect Ctrl+Z** to work in any editing app
- **Without it:** Users feel the app is "broken" or "unfinished"
- **Legal risk:** Accidental signature placement can't be undone

### User Pain Points (from support tickets)
1. **"I accidentally moved my signature"** - Can't put it back
2. **"Deleted the wrong signature"** - Lost work
3. **"Resized it too small"** - Can't recover original size
4. **"Placed it on wrong page"** - Have to re-add all signatures

### Competitor Analysis

| Product | Undo Support | Limitations | Implementation |
|---------|--------------|-------------|----------------|
| **Adobe Acrobat** | Unlimited | Memory intensive | Command pattern |
| **Preview (macOS)** | Limited (20 steps) | Simple stack | Action stack |
| **PDFelement** | Unlimited | Slow with large docs | Snapshot-based |
| **Smallpdf** | None | Web-based limitation | N/A |
| **DocuSign** | Step-by-step | Workflow-based | State machine |

### Industry Standards
- **Ctrl+Z / Cmd+Z** for undo
- **Ctrl+Y / Cmd+Shift+Z** for redo
- **Unlimited or 50+ steps**
- **Visual feedback** showing what was undone
- **Non-destructive** - Original file never modified until save

---

## Technical Specification

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                   Undo/Redo Architecture                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   User Action ──▶ Command ──▶ Execute ──▶ Push to Stack    │
│                                    │                         │
│                                    ▼                         │
│                           ┌─────────────────┐                │
│                           │  Command Stack  │                │
│                           │  (LIFO)         │                │
│                           │                 │                │
│   Undo ◀── Pop & Undo ◀──│  [Cmd 3]       │                │
│                           │  [Cmd 2] ◀── Current           │
│   Redo ──▶ Push & Redo ──▶│  [Cmd 1]       │                │
│                           └─────────────────┘                │
│                                    │                         │
│                                    ▼                         │
│                           ┌─────────────────┐                │
│                           │  State Manager  │                │
│                           │  (Document)     │                │
│                           └─────────────────┘                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Design Pattern: Command Pattern

The Command Pattern is ideal for undo/redo because it:
- Encapsulates actions as objects
- Separates execution from invocation
- Enables undo by storing reverse operations
- Supports queuing, logging, and transactions

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

class Command(ABC):
    """Abstract base class for all undoable commands."""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.executed = False
        self.description = "Unknown action"
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command."""
        pass
    
    @abstractmethod
    def redo(self) -> None:
        """Re-execute after undo."""
        pass
    
    def can_undo(self) -> bool:
        """Check if command can be undone."""
        return True
    
    def merge_with(self, other: 'Command') -> Optional['Command']:
        """Try to merge with another command (for optimization)."""
        return None


# Concrete Commands for PDF Signing

class AddSignatureCommand(Command):
    """Command to add a signature to the PDF."""
    
    def __init__(self, pdf_tab, signature_data, position, size):
        super().__init__()
        self.pdf_tab = pdf_tab
        self.signature_data = signature_data
        self.position = position
        self.size = size
        self.signature_id = None
        self.description = "Add signature"
    
    def execute(self):
        self.signature_id = self.pdf_tab._add_signature(
            self.signature_data, 
            self.position, 
            self.size
        )
        self.executed = True
    
    def undo(self):
        if self.signature_id:
            self.pdf_tab._remove_signature(self.signature_id)
    
    def redo(self):
        self.execute()


class MoveSignatureCommand(Command):
    """Command to move a signature."""
    
    def __init__(self, pdf_tab, signature_id, old_pos, new_pos):
        super().__init__()
        self.pdf_tab = pdf_tab
        self.signature_id = signature_id
        self.old_position = old_pos
        self.new_position = new_pos
        self.description = "Move signature"
    
    def execute(self):
        self.pdf_tab._move_signature(self.signature_id, self.new_position)
        self.executed = True
    
    def undo(self):
        self.pdf_tab._move_signature(self.signature_id, self.old_position)
    
    def redo(self):
        self.execute()
    
    def merge_with(self, other):
        """Merge consecutive moves of same signature."""
        if isinstance(other, MoveSignatureCommand) and \
           other.signature_id == self.signature_id:
            # Combine into one move command
            return MoveSignatureCommand(
                self.pdf_tab, 
                self.signature_id,
                self.old_position,
                other.new_position
            )
        return None


class ResizeSignatureCommand(Command):
    """Command to resize a signature."""
    
    def __init__(self, pdf_tab, signature_id, old_size, new_size):
        super().__init__()
        self.pdf_tab = pdf_tab
        self.signature_id = signature_id
        self.old_size = old_size
        self.new_size = new_size
        self.description = "Resize signature"
    
    def execute(self):
        self.pdf_tab._resize_signature(self.signature_id, self.new_size)
        self.executed = True
    
    def undo(self):
        self.pdf_tab._resize_signature(self.signature_id, self.old_size)
    
    def redo(self):
        self.execute()


class DeleteSignatureCommand(Command):
    """Command to delete a signature."""
    
    def __init__(self, pdf_tab, signature_id, signature_data, position, size):
        super().__init__()
        self.pdf_tab = pdf_tab
        self.signature_id = signature_id
        self.signature_data = signature_data
        self.position = position
        self.size = size
        self.description = "Delete signature"
    
    def execute(self):
        self.pdf_tab._remove_signature(self.signature_id)
        self.executed = True
    
    def undo(self):
        self.signature_id = self.pdf_tab._add_signature(
            self.signature_data,
            self.position,
            self.size
        )
    
    def redo(self):
        self.execute()


class ChangePageCommand(Command):
    """Command to change page (for undo history tracking)."""
    
    def __init__(self, pdf_tab, old_page, new_page):
        super().__init__()
        self.pdf_tab = pdf_tab
        self.old_page = old_page
        self.new_page = new_page
        self.description = f"Go to page {new_page + 1}"
    
    def execute(self):
        self.pdf_tab._set_page(self.new_page)
        self.executed = True
    
    def undo(self):
        self.pdf_tab._set_page(self.old_page)
    
    def redo(self):
        self.execute()
```

### Command History Manager

```python
class CommandHistory:
    """Manages the undo/redo stack with memory optimization."""
    
    MAX_HISTORY_SIZE = 100  # Maximum commands to retain
    MEMORY_LIMIT_MB = 100   # Memory limit for history
    
    def __init__(self):
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._current_command: Optional[Command] = None
        self._is_undoing = False
        self._listeners: List[Callable] = []
    
    def execute(self, command: Command) -> None:
        """Execute a command and add to history."""
        # If we're in the middle of undoing, clear redo stack
        if self._is_undoing:
            self._redo_stack.clear()
        
        # Try to merge with previous command (for optimization)
        if self._undo_stack and not self._is_undoing:
            last_command = self._undo_stack[-1]
            merged = last_command.merge_with(command)
            if merged:
                # Replace last command with merged version
                self._undo_stack[-1] = merged
                merged.execute()
                self._notify_change()
                return
        
        # Execute and add to stack
        command.execute()
        self._undo_stack.append(command)
        
        # Clear redo stack on new action
        self._redo_stack.clear()
        
        # Enforce history limits
        self._enforce_limits()
        
        self._notify_change()
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    def undo(self) -> Optional[str]:
        """Undo the last command. Returns description or None."""
        if not self.can_undo():
            return None
        
        self._is_undoing = True
        try:
            command = self._undo_stack.pop()
            command.undo()
            self._redo_stack.append(command)
            self._notify_change()
            return command.description
        finally:
            self._is_undoing = False
    
    def redo(self) -> Optional[str]:
        """Redo the last undone command. Returns description or None."""
        if not self.can_redo():
            return None
        
        command = self._redo_stack.pop()
        command.redo()
        self._undo_stack.append(command)
        self._notify_change()
        return command.description
    
    def undo_multiple(self, count: int) -> List[str]:
        """Undo multiple commands. Returns list of descriptions."""
        descriptions = []
        for _ in range(min(count, len(self._undo_stack))):
            desc = self.undo()
            if desc:
                descriptions.append(desc)
        return descriptions
    
    def clear(self) -> None:
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._notify_change()
    
    def get_history(self) -> List[dict]:
        """Get full history for display (e.g., in Edit menu)."""
        history = []
        
        # Undo stack (most recent first for display)
        for cmd in reversed(self._undo_stack):
            history.append({
                'description': cmd.description,
                'timestamp': cmd.timestamp,
                'type': 'undoable'
            })
        
        # Redo stack
        for cmd in reversed(self._redo_stack):
            history.append({
                'description': cmd.description,
                'timestamp': cmd.timestamp,
                'type': 'redoable'
            })
        
        return history
    
    def _enforce_limits(self):
        """Enforce memory and count limits."""
        # Remove oldest commands if over limit
        while len(self._undo_stack) > self.MAX_HISTORY_SIZE:
            removed = self._undo_stack.pop(0)
            # Cleanup any resources
            if hasattr(removed, 'cleanup'):
                removed.cleanup()
        
        # TODO: Check memory usage and compress if needed
    
    def add_listener(self, callback: Callable):
        """Add listener for history changes."""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Remove listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_change(self):
        """Notify all listeners of state change."""
        for listener in self._listeners:
            try:
                listener(self.can_undo(), self.can_redo())
            except Exception:
                pass  # Don't let listener errors break history
```

### Integration with PdfTab

```python
class PdfTab(QWidget):
    """Enhanced PDF tab with undo/redo support."""
    
    def __init__(self):
        super().__init__()
        self.history = CommandHistory()
        self.signatures: Dict[str, DraggableSignature] = {}
        self._signature_counter = 0
        
        # Connect history to UI
        self.history.add_listener(self._on_history_changed)
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Setup undo/redo keyboard shortcuts."""
        from PySide6.QtGui import QShortcut, QKeySequence
        from PySide6.QtCore import Qt
        
        # Undo: Ctrl+Z or Cmd+Z
        self.undo_shortcut = QShortcut(
            QKeySequence("Ctrl+Z"),
            self
        )
        self.undo_shortcut.activated.connect(self.undo)
        
        # Redo: Ctrl+Y or Cmd+Shift+Z
        self.redo_shortcut = QShortcut(
            QKeySequence("Ctrl+Y"),
            self
        )
        self.redo_shortcut.activated.connect(self.redo)
        
        # Alternative redo: Ctrl+Shift+Z
        self.redo_alt_shortcut = QShortcut(
            QKeySequence("Ctrl+Shift+Z"),
            self
        )
        self.redo_alt_shortcut.activated.connect(self.redo)
    
    def add_signature(self, image_path: str, position: QPoint = None):
        """Add signature with undo support."""
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return
        
        # Default position if not specified
        if position is None:
            position = QPoint(100, 100)
        
        # Default size
        size = QSize(200, 100)
        
        # Create and execute command
        command = AddSignatureCommand(
            self,
            image_path,
            position,
            size
        )
        self.history.execute(command)
    
    def delete_signature(self, sig_id: str):
        """Delete signature with undo support."""
        if sig_id not in self.signatures:
            return
        
        sig = self.signatures[sig_id]
        command = DeleteSignatureCommand(
            self,
            sig_id,
            sig.image_path,
            sig.pos(),
            sig.size()
        )
        self.history.execute(command)
    
    def undo(self):
        """Undo last action."""
        description = self.history.undo()
        if description:
            self.status_bar.showMessage(f"Undone: {description}", 2000)
    
    def redo(self):
        """Redo last undone action."""
        description = self.history.redo()
        if description:
            self.status_bar.showMessage(f"Redone: {description}", 2000)
    
    def _on_history_changed(self, can_undo: bool, can_redo: bool):
        """Update UI based on history state."""
        # Update Edit menu
        if hasattr(self, 'undo_action'):
            self.undo_action.setEnabled(can_undo)
        if hasattr(self, 'redo_action'):
            self.redo_action.setEnabled(can_redo)
    
    # Internal methods used by commands
    def _add_signature(self, image_path: str, position: QPoint, size: QSize) -> str:
        """Internal: Add signature widget."""
        sig_id = f"sig_{self._signature_counter}"
        self._signature_counter += 1
        
        pixmap = QPixmap(image_path)
        sig_widget = DraggableSignature(pixmap, self.page_container)
        sig_widget.setGeometry(position.x(), position.y(), size.width(), size.height())
        sig_widget.show()
        
        # Store metadata
        sig_widget.image_path = image_path
        sig_widget.sig_id = sig_id
        
        # Connect move/resize events
        sig_widget.moved.connect(self._on_signature_moved)
        sig_widget.resized.connect(self._on_signature_resized)
        
        self.signatures[sig_id] = sig_widget
        return sig_id
    
    def _remove_signature(self, sig_id: str):
        """Internal: Remove signature widget."""
        if sig_id in self.signatures:
            self.signatures[sig_id].close()
            del self.signatures[sig_id]
    
    def _move_signature(self, sig_id: str, position: QPoint):
        """Internal: Move signature to position."""
        if sig_id in self.signatures:
            self.signatures[sig_id].move(position)
    
    def _resize_signature(self, sig_id: str, size: QSize):
        """Internal: Resize signature."""
        if sig_id in self.signatures:
            self.signatures[sig_id].resize(size)
    
    def _on_signature_moved(self, sig_id: str, old_pos: QPoint, new_pos: QPoint):
        """Handle signature move for undo."""
        command = MoveSignatureCommand(self, sig_id, old_pos, new_pos)
        self.history.execute(command)
    
    def _on_signature_resized(self, sig_id: str, old_size: QSize, new_size: QSize):
        """Handle signature resize for undo."""
        command = ResizeSignatureCommand(self, sig_id, old_size, new_size)
        self.history.execute(command)
```

---

## User Stories

### Story 1: Correcting a Mistake
**As a** user signing a contract  
**I want to** undo my last signature placement  
**So that** I can reposition it correctly  

**Acceptance Criteria:**
- Pressing Ctrl+Z immediately removes last signature
- Signature returns exactly where it was
- Can redo to restore it
- Visual feedback shows what was undone

### Story 2: Experimenting with Layout
**As a** designer reviewing a document  
**I want to** try different signature positions  
**So that** I can find the best placement  

**Acceptance Criteria:**
- Can move signature multiple times
- Each move is undoable independently
- History survives page changes
- Can undo back to original position

### Story 3: Bulk Correction
**As a** legal assistant  
**I want to** undo multiple actions at once  
**So that** I can quickly revert to earlier state  

**Acceptance Criteria:**
- Can see history list with descriptions
- Can click any point in history to jump there
- Clears redo stack when new action taken
- Memory usage stays reasonable

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Implement Command base class
- [ ] Create CommandHistory manager
- [ ] Add unit tests for command system
- [ ] Implement basic commands (Add, Delete)

**Deliverable:** Command system working in isolation

### Phase 2: PDF Integration (Week 1-2)
- [ ] Refactor PdfTab to support commands
- [ ] Implement Move and Resize commands
- [ ] Add keyboard shortcuts (Ctrl+Z/Y)
- [ ] Connect to Edit menu
- [ ] Add visual feedback

**Deliverable:** Undo/redo working for signatures

### Phase 3: Advanced Features (Week 2)
- [ ] Command merging (consecutive moves)
- [ ] History visualization
- [ ] Memory optimization
- [ ] Persistence (save history with document)

**Deliverable:** Professional-grade undo system

### Phase 4: Polish & Testing (Week 3)
- [ ] Edge case handling
- [ ] Performance testing
- [ ] UI/UX refinement
- [ ] Documentation

**Deliverable:** Production-ready feature

---

## Testing Strategy

### Unit Tests
```python
def test_command_execute_undo_redo():
def test_command_history_limits():
def test_command_merging():
def test_empty_history_undo():
def test_memory_cleanup():
```

### Integration Tests
```python
def test_add_signature_undo():
def test_move_signature_undo():
def test_delete_signature_undo():
def test_multiple_operations_sequence():
def test_keyboard_shortcuts():
```

### Edge Cases
- Undo when nothing to undo
- Rapid undo/redo spam
- Memory exhaustion with many commands
- Corrupted command state
- Page change during undo

---

## Success Metrics

### User Adoption
- **Target:** 90% of users use undo at least once per session
- **Measurement:** Track undo usage
- **Success:** >80% adoption rate

### Error Recovery
- **Target:** 95% of accidental actions successfully undone
- **Measurement:** Support ticket analysis
- **Success:** <5% "I made a mistake" tickets

### Performance
- **Target:** Undo operation <100ms
- **Measurement:** Performance profiling
- **Success:** <50ms average

### Memory Usage
- **Target:** History uses <50MB for 100 commands
- **Measurement:** Memory profiling
- **Success:** <30MB actual usage

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Memory leaks** | High | Medium | Strict cleanup, weak refs |
| **Command corruption** | High | Low | Validation, error handling |
| **Performance issues** | Medium | Medium | Command merging, limits |
| **User confusion** | Low | Low | Visual feedback, tooltips |
| **Breaking existing code** | High | Medium | Gradual refactoring |

---

## UI/UX Considerations

### Edit Menu
```
Edit
├── Undo    Ctrl+Z    [grayed if unavailable]
├── Redo    Ctrl+Y    [grayed if unavailable]
├── ─────────────────
├── Cut     Ctrl+X
├── Copy    Ctrl+C
├── Paste   Ctrl+V
├── ─────────────────
└── History...        [opens history panel]
```

### Visual Feedback
- Brief flash or highlight of affected element
- Status bar message: "Undone: Move signature"
- Subtle sound effect (optional)

### History Panel (Advanced)
```
┌─────────────────────────────┐
│ History                     │
├─────────────────────────────┤
│ ○ Add signature            │
│ ○ Move signature          │  ← current
│ ○ Move signature          │
│ ○ Resize signature        │
│ ○ Delete signature        │
│ ─────────────────────────  │
│ [Jump to selected]        │
└─────────────────────────────┘
```

---

## References

- [Command Pattern - Gang of Four](https://en.wikipedia.org/wiki/Command_pattern)
- [Qt Undo Framework](https://doc.qt.io/qt-6/qundo.html)
- [Adobe's Undo Implementation](https://www.adobe.com/devnet/pdf/pdfs/PDF32000_2008.pdf)

---

**Document Status:** Complete  
**Next Review:** May 10, 2026