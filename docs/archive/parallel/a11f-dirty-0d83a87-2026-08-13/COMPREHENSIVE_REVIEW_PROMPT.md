# Comprehensive Pre-Launch Review Prompt

**Purpose:** Deep-dive review of SignKit before launch  
**For:** AI/LLM reviewer or human expert  
**Date:** November 13, 2025

---

## 📋 HOW TO USE THIS PROMPT

**For AI Review:**
Copy the entire "REVIEW PROMPT" section below and paste it into Claude, GPT-4, or another LLM along with relevant files from the codebase.

**For Human Review:**
Use this as a comprehensive checklist to evaluate all aspects of the product before launch.

---

## 🎯 REVIEW PROMPT FOR AI/LLM

```
You are an expert product reviewer conducting a comprehensive pre-launch audit of SignKit,
a desktop application for signature extraction. Your goal is to identify any issues, gaps,
or improvements needed before the Black Friday launch (15 days away).

Review the following aspects in detail and provide actionable feedback:

## 1. USER EXPERIENCE (UX) REVIEW

### First-Time User Experience
- Analyze the onboarding flow from app launch to first successful signature extraction
- Evaluate the clarity of the license activation process
- Assess the trial mode experience and conversion funnel
- Review error messages and user guidance
- Check for confusing UI elements or unclear workflows

**Questions to Answer:**
1. Can a non-technical user extract their first signature in under 2 minutes?
2. Is the license activation process clear and friction-free?
3. Are error messages helpful and actionable?
4. Does the trial mode effectively demonstrate value?
5. What would cause a user to abandon the app in the first 5 minutes?

### Core Workflow Analysis
- Evaluate the signature extraction workflow (upload → select → process → export)
- Assess the PDF signing workflow
- Review the library management experience
- Analyze keyboard shortcuts and power-user features
- Check for workflow bottlenecks or unnecessary steps

**Questions to Answer:**
1. How many clicks does it take to extract and export a signature?
2. Are there any redundant steps that could be eliminated?
3. Is the PDF signing workflow intuitive?
4. Do keyboard shortcuts cover the most common actions?
5. What would frustrate a power user?

### Visual Design & Consistency
- Review UI consistency across all screens
- Evaluate color scheme and contrast (accessibility)
- Assess icon usage and visual hierarchy
- Check for responsive layout issues
- Review typography and readability

**Questions to Answer:**
1. Is the visual design professional and modern?
2. Are there any accessibility issues (color contrast, font sizes)?
3. Is the UI consistent across all features?
4. Does the design match the $29-39 price point?
5. What visual elements feel amateurish or unpolished?

---

## 2. USER INTERFACE (UI) REVIEW

### Layout & Organization
- Evaluate the main window layout and information architecture
- Review the toolbar and menu organization
- Assess the status bar and feedback mechanisms
- Check for proper use of whitespace
- Analyze the settings/preferences organization

**Questions to Answer:**
1. Is important information easily accessible?
2. Are related features grouped logically?
3. Is there too much or too little information on screen?
4. Do users know where to find specific features?
5. What UI elements are confusing or misplaced?

### Interactive Elements
- Review button states (normal, hover, pressed, disabled)
- Evaluate form inputs and validation
- Assess drag-and-drop functionality
- Check for proper loading states and progress indicators
- Review modal dialogs and their dismissal patterns

**Questions to Answer:**
1. Do all interactive elements provide clear feedback?
2. Are loading states visible and informative?
3. Is drag-and-drop intuitive and reliable?
4. Are form validations helpful and timely?
5. What interactions feel sluggish or unresponsive?

### Responsive Behavior
- Test window resizing behavior
- Evaluate zoom level handling
- Check for proper scrolling behavior
- Assess behavior on different screen sizes
- Review high-DPI/Retina display support

**Questions to Answer:**
1. Does the app handle window resizing gracefully?
2. Are all elements visible at minimum window size?
3. Does the app look good on 4K/Retina displays?
4. Are scroll areas obvious and functional?
5. What breaks at extreme window sizes?

---

## 3. FEATURE COMPLETENESS REVIEW

### Core Features
For each core feature, evaluate:
- **Signature Extraction:** Upload, selection, processing, export
- **PDF Signing:** PDF viewer, signature placement, saving
- **Library Management:** Save, organize, search, reuse signatures
- **License Management:** Activation, validation, trial mode

**Questions to Answer:**
1. Are all advertised features fully implemented?
2. Do features work as users would expect?
3. Are there any half-implemented features?
4. What features feel incomplete or buggy?
5. What critical features are missing?

### Edge Cases & Error Handling
- Test with various file formats and sizes
- Try invalid inputs and corrupted files
- Test network connectivity issues
- Evaluate behavior when disk is full
- Check handling of permission errors

**Questions to Answer:**
1. How does the app handle corrupted or invalid files?
2. What happens when the network is unavailable?
3. Are error messages specific and helpful?
4. Does the app recover gracefully from errors?
5. What edge cases cause crashes or data loss?

### Performance & Responsiveness
- Evaluate processing speed for various image sizes
- Test with large PDF files (100+ pages)
- Check memory usage during extended use
- Assess startup time and shutdown behavior
- Review responsiveness during heavy operations

**Questions to Answer:**
1. Does the app feel fast and responsive?
2. Are there any operations that block the UI?
3. Is memory usage reasonable?
4. Does performance degrade over time?
5. What operations feel slow or laggy?

---

## 4. TECHNICAL QUALITY REVIEW

### Code Quality
- Review code organization and architecture
- Evaluate error handling and logging
- Assess security practices (input validation, data storage)
- Check for code smells and technical debt
- Review dependency management

**Questions to Answer:**
1. Is the codebase well-organized and maintainable?
2. Are there security vulnerabilities?
3. Is error handling comprehensive?
4. Are there obvious performance bottlenecks?
5. What technical debt needs addressing?

### Testing Coverage
- Evaluate unit test coverage
- Review integration test scenarios
- Assess manual testing procedures
- Check for regression test suite
- Evaluate test data and fixtures

**Questions to Answer:**
1. What percentage of code is covered by tests?
2. Are critical paths thoroughly tested?
3. Is there a regression test suite?
4. What areas lack test coverage?
5. How confident are you in the test suite?

### Platform Compatibility
- Test on macOS (Intel and Apple Silicon)
- Test on Windows (10 and 11)
- Test on Linux (Ubuntu, Fedora)
- Evaluate cross-platform consistency
- Check for platform-specific bugs

**Questions to Answer:**
1. Does the app work consistently across platforms?
2. Are there platform-specific bugs?
3. Is the UI native-feeling on each platform?
4. What platform-specific features are missing?
5. Which platform has the best/worst experience?

---

## 5. BUSINESS & MONETIZATION REVIEW

### Pricing Strategy
- Evaluate the $29 launch price vs $39 regular price
- Assess the value proposition at each price point
- Review competitor pricing and positioning
- Analyze the Black Friday discount strategy
- Evaluate the Affinity-style versioning model

**Questions to Answer:**
1. Is $29 the right launch price?
2. Does the product deliver $29-39 of value?
3. How does pricing compare to competitors?
4. Is the Black Friday discount compelling?
5. Is the versioning strategy clear to customers?

### Purchase Flow
- Review the Gumroad product page
- Evaluate the license activation process
- Assess the email delivery and onboarding
- Check for friction points in the purchase flow
- Review refund policy and customer support

**Questions to Answer:**
1. Is the purchase process smooth and trustworthy?
2. Are there any barriers to purchase?
3. Is license activation straightforward?
4. What would cause purchase abandonment?
5. Is the refund policy fair and clear?

### Marketing & Positioning
- Review the landing page copy and design
- Evaluate the value proposition clarity
- Assess the target audience definition
- Review the competitive differentiation
- Analyze the Black Friday marketing strategy

**Questions to Answer:**
1. Is the value proposition clear and compelling?
2. Who is the target customer?
3. How is SignKit differentiated from competitors?
4. Is the landing page conversion-optimized?
5. What marketing messages resonate most?

---

## 6. LEGAL & COMPLIANCE REVIEW

### Privacy & Data Protection
- Review the privacy policy accuracy
- Evaluate data collection and storage practices
- Assess GDPR/CCPA compliance
- Check for unnecessary data collection
- Review third-party data sharing

**Questions to Answer:**
1. Is the privacy policy accurate and complete?
2. Are data collection practices privacy-first?
3. Is the app GDPR/CCPA compliant?
4. What data is collected and why?
5. Are there any privacy red flags?

### Terms & Licensing
- Review the EULA and Terms of Service
- Evaluate the license terms clarity
- Assess the refund policy fairness
- Check for legal compliance
- Review intellectual property protection

**Questions to Answer:**
1. Are the terms clear and fair?
2. Is the license model well-defined?
3. Is the refund policy reasonable?
4. Are there any legal risks?
5. What terms might confuse customers?

### Security & Safety
- Evaluate input validation and sanitization
- Review file handling security
- Assess license validation security
- Check for common vulnerabilities
- Review update mechanism security

**Questions to Answer:**
1. Are there security vulnerabilities?
2. Is user data stored securely?
3. Is the license system secure?
4. Are updates delivered securely?
5. What security risks exist?

---

## 7. DOCUMENTATION REVIEW

### User Documentation
- Review the Quick Start Guide
- Evaluate the User Manual completeness
- Assess the FAQ coverage
- Check for video tutorials
- Review troubleshooting documentation

**Questions to Answer:**
1. Is the documentation clear and comprehensive?
2. Are common questions answered?
3. Is the Quick Start Guide actually quick?
4. What documentation is missing?
5. Would a non-technical user understand it?

### Technical Documentation
- Review the API documentation (if applicable)
- Evaluate the developer setup guide
- Assess the architecture documentation
- Check for deployment documentation
- Review the changelog and release notes

**Questions to Answer:**
1. Is the technical documentation complete?
2. Can a developer set up the project easily?
3. Is the architecture well-documented?
4. Are deployment procedures clear?
5. What technical docs are missing?

---

## 8. LAUNCH READINESS REVIEW

### Pre-Launch Checklist
- Evaluate the 15-day launch timeline
- Review the Black Friday strategy
- Assess the marketing channel coverage
- Check for launch day preparation
- Review the support readiness

**Questions to Answer:**
1. Is 15 days enough time to launch?
2. What tasks are most critical?
3. What could delay the launch?
4. Is the Black Friday strategy sound?
5. What launch risks exist?

### Post-Launch Planning
- Review the support plan
- Evaluate the update roadmap
- Assess the analytics setup
- Check for customer feedback mechanisms
- Review the growth strategy

**Questions to Answer:**
1. Is there a solid support plan?
2. What's the update roadmap for v1.x?
3. How will success be measured?
4. How will customer feedback be collected?
5. What's the growth strategy post-launch?

---

## 9. COMPETITIVE ANALYSIS

### Market Positioning
- Compare features to Adobe Acrobat
- Evaluate vs DocuSign and similar tools
- Assess vs free alternatives (Photoshop, GIMP)
- Review the privacy-first positioning
- Analyze the pricing competitiveness

**Questions to Answer:**
1. What are SignKit's unique advantages?
2. What features do competitors have that SignKit lacks?
3. Is the privacy-first angle compelling?
4. How does pricing compare?
5. What's the strongest competitive threat?

### Target Market
- Evaluate the target customer definition
- Assess the market size and opportunity
- Review the customer pain points addressed
- Analyze the go-to-market strategy
- Evaluate the customer acquisition plan

**Questions to Answer:**
1. Who is the ideal customer?
2. How big is the addressable market?
3. What pain points does SignKit solve?
4. How will customers discover SignKit?
5. What's the customer acquisition cost?

---

## 10. ROADMAP & FUTURE PLANNING

### V1.x Roadmap
- Review the planned v1.x updates
- Evaluate the feature prioritization
- Assess the update frequency plan
- Check for customer feedback integration
- Review the technical debt management

**Questions to Answer:**
1. What features should be in v1.1?
2. How often should updates be released?
3. How will customer feedback shape the roadmap?
4. What technical debt needs addressing?
5. What's the v1.x end-of-life plan?

### V2.0 Planning
- Evaluate the v2.0 feature ideas
- Assess the upgrade pricing strategy
- Review the v1-to-v2 migration plan
- Check for backward compatibility
- Analyze the v2.0 value proposition

**Questions to Answer:**
1. What features justify a v2.0 release?
2. When should v2.0 be released?
3. Is the upgrade pricing fair?
4. How will v1 customers be migrated?
5. What's the v2.0 competitive advantage?

---

## OUTPUT FORMAT

For each section above, provide:

1. **Overall Assessment:** (Excellent / Good / Needs Improvement / Critical Issues)

2. **Key Findings:**
   - List 3-5 most important observations
   - Highlight both strengths and weaknesses

3. **Critical Issues:**
   - Issues that MUST be fixed before launch
   - Ranked by severity and impact

4. **Recommendations:**
   - Specific, actionable improvements
   - Prioritized by impact and effort

5. **Quick Wins:**
   - Easy improvements that can be done in 1-2 days
   - High-impact, low-effort changes

6. **Launch Blockers:**
   - Issues that would prevent a successful launch
   - Must be resolved before Black Friday

7. **Post-Launch Improvements:**
   - Issues that can be addressed after launch
   - Should be in the v1.1 roadmap

---

## FINAL SUMMARY

Provide a comprehensive summary including:

1. **Launch Readiness Score:** X/10
2. **Recommended Launch Date:** [Date] with reasoning
3. **Top 5 Priorities:** Before launch
4. **Top 5 Risks:** And mitigation strategies
5. **Overall Recommendation:** Launch / Delay / Major Changes Needed

---

## CONTEXT FILES TO REVIEW

Please review these files from the codebase:

**Core Application:**
- desktop_app/views/main_window_parts/extraction.py
- desktop_app/views/main_window_parts/pdf.py
- desktop_app/views/license_restriction_dialog.py
- desktop_app/license/storage.py
- desktop_app/processing/extractor.py

**Documentation:**
- docs/PURCHASE_POLICY.md
- docs/PRIVACY_POLICY.md
- docs/TERMS_OF_SERVICE.md
- docs/GUMROAD_COMPLETE_GUIDE.md
- docs/BLACK_FRIDAY_STRATEGY.md
- docs/PACKAGING_AND_VERSIONING_STRATEGY.md

**Landing Page:**
- web/live/index.html
- web/live/README.md

**Specs & Planning:**
- .kiro/specs/SIGNKIT_LAUNCH_FINAL.md
- .kiro/specs/LAUNCH_READINESS.md
- .kiro/specs/pre-launch-review/requirements.md
- .kiro/specs/pre-launch-review/tasks.md

**Build & Distribution:**
- build-tools/SignatureExtractor_macOS.spec
- QUICK_START.md
- DISTRIBUTION_STRATEGY.md

---

Begin your comprehensive review now. Be thorough, critical, and constructive.
The goal is to ensure a successful Black Friday launch in 15 days.
```

---

## 🎯 SPECIFIC REVIEW QUESTIONS

### For UX/UI Reviewers

1. **First Impression:** Open the app for the first time. What's your immediate reaction?
2. **Confusion Points:** Where did you get confused or stuck?
3. **Delight Moments:** What features or interactions felt great?
4. **Frustration Points:** What made you frustrated or annoyed?
5. **Missing Features:** What did you expect to find but couldn't?
6. **Visual Polish:** What looks unfinished or amateurish?
7. **Workflow Efficiency:** How many clicks to complete common tasks?
8. **Error Recovery:** How well does the app handle mistakes?
9. **Accessibility:** Can you use it with keyboard only? Screen reader?
10. **Mobile Feel:** Does it feel like a professional desktop app?

### For Technical Reviewers

1. **Architecture:** Is the code well-organized and maintainable?
2. **Performance:** Are there obvious performance bottlenecks?
3. **Security:** What security vulnerabilities exist?
4. **Error Handling:** How robust is error handling?
5. **Testing:** What's the test coverage? What's missing?
6. **Dependencies:** Are dependencies up-to-date and secure?
7. **Platform Support:** How well does it work across platforms?
8. **Scalability:** Can it handle large files and heavy use?
9. **Code Quality:** What technical debt exists?
10. **Deployment:** How easy is it to build and deploy?

### For Business Reviewers

1. **Value Proposition:** Is it clear what problem this solves?
2. **Pricing:** Is $29-39 the right price point?
3. **Target Market:** Who is this for? Is it clear?
4. **Competitive Advantage:** Why choose this over alternatives?
5. **Purchase Flow:** Is buying easy and trustworthy?
6. **Marketing:** Will the Black Friday strategy work?
7. **Support:** Is the support plan adequate?
8. **Roadmap:** Is the v1.x/v2.0 strategy sound?
9. **Monetization:** Is the business model sustainable?
10. **Growth:** How will this grow post-launch?

### For Legal/Compliance Reviewers

1. **Privacy Policy:** Is it accurate and complete?
2. **Terms of Service:** Are they fair and enforceable?
3. **GDPR/CCPA:** Is the app compliant?
4. **Data Collection:** What data is collected? Why?
5. **Security:** Are there security vulnerabilities?
6. **Refund Policy:** Is it fair and clear?
7. **License Terms:** Are they well-defined?
8. **Intellectual Property:** Is IP properly protected?
9. **Third-Party:** Are third-party terms followed?
10. **Liability:** Are liability limits appropriate?

---

## 📊 REVIEW SCORING RUBRIC

### Overall Launch Readiness (0-10 scale)

**10 - Perfect:** Ready to launch immediately, no issues  
**9 - Excellent:** Minor polish needed, launch-ready  
**8 - Very Good:** Few small issues, can launch with minor fixes  
**7 - Good:** Some issues, 1-2 days of work needed  
**6 - Acceptable:** Multiple issues, 3-5 days of work needed  
**5 - Needs Work:** Significant issues, 1-2 weeks needed  
**4 - Major Issues:** Critical problems, 2-4 weeks needed  
**3 - Serious Problems:** Fundamental issues, 1-2 months needed  
**2 - Not Ready:** Major rework required, 3+ months  
**1 - Start Over:** Fundamental flaws, consider pivot

### Category Scoring (0-10 scale)

Score each category:

- User Experience (UX)
- User Interface (UI)
- Feature Completeness
- Technical Quality
- Business & Monetization
- Legal & Compliance
- Documentation
- Launch Readiness
- Competitive Position
- Roadmap & Planning

**Average Score = Overall Launch Readiness**

---

## 🚀 EXPECTED OUTCOMES

After completing this review, you should have:

1. **Clear Launch Decision:** Launch on Black Friday or delay?
2. **Prioritized Task List:** What must be done before launch?
3. **Risk Assessment:** What could go wrong? How to mitigate?
4. **Quick Wins List:** Easy improvements for immediate impact
5. **Post-Launch Roadmap:** What to fix/improve after launch?
6. **Confidence Level:** How confident are you in the launch?

---

## 💡 TIPS FOR REVIEWERS

**Be Honest:**

- Don't sugarcoat issues
- Be specific about problems
- Provide actionable feedback

**Be Constructive:**

- Suggest solutions, not just problems
- Prioritize by impact and effort
- Focus on launch-critical issues

**Be Thorough:**

- Test edge cases
- Try to break things
- Think like a customer

**Be Realistic:**

- Consider the 15-day timeline
- Distinguish must-fix from nice-to-have
- Balance perfection with shipping

---

**This review prompt is designed to uncover every issue, gap, and opportunity before launch. Use it to ensure SignKit is truly ready for Black Friday success.**
