# Signature Extractor Desktop App: Apple-Native UI/UX Improvement Plan

This document outlines actionable recommendations to make the Signature Extractor app feel truly native and delightful on macOS, with a focus on UI, design, workflow, and user experience.

## Latest progress (February 2025)

- Introduced a unified macOS toolbar with quick actions (Open, Export, Save, Help), context-aware handlers per tab, and title-bar integration for document tabbing.
- Wrapped file and color pickers so the desktop app consistently presents native macOS sheets.
- Applied accent-aware styling tweaks: blurred/vibrant extraction panel, cleaner focus rings, and document proxy updates when opening or clearing images.

## 1. Adopt macOS-Native Window Chrome and Toolbar

- Use native window chrome and toolbar (QMacToolBar, PyObjC, or custom QSS)
- Add a toolbar for common actions (Open, Save, Export, Undo, Redo)
- Support window tabbing and document proxy icon

## 2. Replace Generic Controls with macOS-Style Controls

- Use system accent color and vibrancy for panels (QPalette, NSVisualEffectView)
- Replace generic buttons/sliders with macOS-style (Qt macOS style, custom QSS, or PyObjC)
- Use SF Symbols for icons

## 3. Use Native Dialogs for File/Color/Message

- Use QFileDialog with native option or PyObjC for NSOpenPanel/NSColorPanel/NSAlert
- Ensure dialogs support drag-and-drop, sidebar, and recent items

## 4. Refine Menu Bar and Shortcuts

- Add About, Preferences, and standard macOS shortcuts
- Group actions by context (File, Edit, View, Help)
- Use QMenuBar, QMenu, and PyObjC for NSMenu integration

## 5. Add Onboarding Overlay or First-Run Walkthrough

- Show a welcome overlay or wizard for first-time users
- Highlight key controls and workflow steps

## 6. Make Selection/Threshold Controls More Discoverable

- Add inline tips, animated hints, or always-visible preview
- Use QToolTip, QLabel hints, or QPropertyAnimation

## 7. Show Preview/Result Panes in Disabled State Until Selection

- Keep panes visible but disabled until a selection is made
- Use setEnabled(False) and visual cues

## 8. Add Undo/Redo for Selection, Threshold, and Library Actions

- Use QUndoStack and QUndoCommand for undo/redo support
- Add toolbar/menu actions and shortcuts

## 9. Add Progress Spinners for Uploads/Processing

- Use QProgressDialog or QProgressBar for long operations
- Show progress in status bar or overlay

## 10. Enhance Library with Thumbnails, Drag-to-Reorder, Search/Filter

- Use QListWidget with custom delegates for thumbnails
- Implement drag-and-drop and search/filter

## 11. Support Drag-and-Drop from Finder and System Clipboard

- Implement dragEnterEvent/dropEvent for images and PDFs
- Use NSPasteboard via PyObjC for system integration

## 12. Add Quick Look for Signatures and PDFs

- Use PyObjC to call QLPreviewPanel for previewing files

## 13. Improve Accessibility

- Use Qt accessibility APIs and test with VoiceOver
- Support high-contrast mode and keyboard navigation

## 14. Use System Accent Color and Vibrancy for Panels

- Use QPalette and NSVisualEffectView for native look

## 15. Add Touch Bar and Trackpad Gesture Support

- Use PyObjC to access NSTouchBar APIs
- Add trackpad gestures for zoom, pan, and rotate

---

# Prioritization: What to Do First

**1. Adopt macOS-Native Window Chrome and Toolbar**

- This immediately improves the app's look and feel, making it feel at home on macOS.
- Sets the foundation for other native integrations (toolbar, About, Preferences, etc.).

**2. Replace Generic Controls with macOS-Style Controls**

- Upgrading controls and icons to match macOS conventions will have a big impact on perceived quality and usability.
- Makes the app visually consistent and delightful for Mac users.

These two items will provide the most visible and foundational improvements, making all subsequent enhancements more effective and easier to integrate.
