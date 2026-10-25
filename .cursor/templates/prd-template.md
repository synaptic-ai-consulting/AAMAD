# AAMAD PRD Generation Template

## Context & Instructions
Generate a comprehensive Product Requirements Document (PRD) for the product.
Base decisions on the provided Deep Research / MRD findings when present, or on a system description / elicitation notes when MRD was skipped.
Do not prescribe an agent roster or an application pattern. Point architecture at the SAD Pattern Decision.
Ensure the PRD is production-ready for MVP scope and addresses real needs identified in the inputs.
The selected runtime (`AAMAD_TARGET_RUNTIME`) constrains Phase 2 implementation conventions; do not hardcode a single runtime framework as the product definition.

## Input Requirements

**Deep Research Report / MRD**: [PASTE OR REFERENCE `project-context/1.define/mrd.md` — or mark N/A if skipped]  
**System Description** (optional): [REFERENCE `project-context/1.define/system-description.md` IF PRESENT]  
**System Concept**: [INSERT THE PRODUCT DESCRIPTION — not a presumed multi-agent crew]  
**Selected Runtime**: [crewai | claude-agent-sdk | cursor-sdk]

## PRD Structure — Generate All Sections Below

### 1. Executive Summary

**Problem Statement** (Research-backed when MRD exists):

* Specific customer or operator problem  
* Quantified impact and pain points  
* Target market or user population scope (N/A with rationale if internal tool)

**Solution Overview** (Evidence-based):

* Product approach and unique value proposition  
* Key differentiators vs alternatives  
* Expected business or operational outcomes and success metrics

**Strategic Rationale**:

* Why this product is the right response to the problem  
* Business case / ROI or operational value  
* Market timing and competitive positioning (or N/A for internal tools)

### 2. Market Context & User Analysis

**Target Market / Users** (From Research or System Description):

* Primary user personas with detailed characteristics  
* Market segment size and growth projections (or N/A)  
* Geographic focus and expansion opportunities (or N/A)

**User Needs Analysis**:

* Critical pain points and unmet needs  
* User journey mapping and interaction patterns  
* Adoption barriers and success factors

**Competitive Landscape** (optional when MRD skipped):

* Direct and indirect competitors or alternative workflows  
* Feature gaps and differentiation opportunities  
* Pricing benchmarks when relevant

### 3. Technical Requirements & Architecture

Do not prescribe an application pattern or a roster of runtime agents here. `@system.arch` records Work Ownership and Pattern Decision in `sad.md`. This section states constraints the architecture must satisfy.

**Discovery constraints** (from system description when present):

* Must do / must not / must cost / must prove rows, each tagged requirement or assumption  
* Feasibility notes for the architect (do not issue the pattern verdict)

**Runtime constraints** (aligned with Selected Runtime):

* Tool and integration boundaries the product must honor  
* Identity, data-minimization, and logging obligations  
* Adapter-specific controls to consider after the SAD pattern is chosen (e.g. `max_iter`, hooks, `allowed_tools`)

**Integration Requirements**:

* Required APIs and external services  
* Database and storage specifications (MVP vs deferred)  
* Authentication and security requirements  
* Performance and scalability targets

**Infrastructure Specifications**:

* Cloud / hosting requirements for MVP  
* Compute and memory specifications  
* Network and security architecture  
* Monitoring and logging requirements

### 4. Functional Requirements

**Core Features** (Priority P0):

* [Feature 1]: User story format with acceptance criteria  
* [Feature 2]: Technical specifications and constraints  
* [Feature 3]: Integration requirements and dependencies

**Enhanced Features** (Priority P1):

* Deferred unless justified for MVP

**Future Features** (Priority P2):

* Explicit Future Work list

### 5. Non-Functional Requirements

**Performance Requirements**:

* Response time targets  
* Throughput and concurrency specifications  
* Availability and uptime requirements

**Security & Compliance**:

* Data protection and privacy requirements  
* Access control and authentication specifications  
* Regulatory compliance needs when applicable

**Scalability & Reliability**:

* Scaling triggers (MVP: document deferred approach)  
* Fault tolerance and recovery procedures

### 6. User Experience Design

**Interface Requirements**:

* User interaction patterns  
* Web / mobile platform specifications  
* Accessibility and usability standards

**Human–system interaction**:

* Communication patterns for the primary surface  
* Feedback and error handling approaches  
* Transparency and explainability features

### 7. Success Metrics & KPIs

**Business / Operational Metrics**:

* Targets aligned with problem statement

**Technical Metrics**:

* System performance and reliability targets  
* Task effectiveness and accuracy rates  
* Cost efficiency and resource utilization

**User Experience Metrics**:

* Satisfaction, task completion, time-to-value

### 8. Implementation Strategy

**Development Phases**:

* Phase 1 (Define): MRD (optional), PRD, SAD  
* Phase 2 (Build): Setup → FE/BE → Integration → QA  
* Phase 3 (Deliver): Deploy configs and runbook

**Resource Requirements** and **Risk Mitigation**: document realistically for MVP

### 9. Launch & Go-to-Market Strategy

Optional for internal tools — if skipped, state N/A under Assumptions.

## Quality Assurance Checklist

- [ ] Requirements traceable to MRD, system description, or recorded Assumptions  
- [ ] Technical specifications feasible with the selected runtime adapter  
- [ ] Success metrics aligned with stated objectives  
- [ ] MVP vs Future Work boundaries explicit  
- [ ] Market sections marked N/A when MRD was intentionally skipped

## Sources

- MRD / system-description / stakeholder inputs used

## Assumptions

- Gaps filled by inference; MRD-skip rationale when applicable

## Open Questions

- Unresolved items for architect or stakeholder resolution

## Audit

- Timestamp, persona id (`product-mgr`), action (`create-prd` or `create-context`), resolved `AAMAD_TARGET_RUNTIME`
