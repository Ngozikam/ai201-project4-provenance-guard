# Provenance Guard

## Milestone 1: System Architecture

### 1. Architecture Narrative

A creator submits a piece of text, such as a poem, blog post, or short story excerpt, through the **POST /submit** endpoint. The Flask API receives the request, validates the submitted content, and forwards the text to two independent detection signals.

The first detection signal is the Groq LLM classifier, which analyzes the semantic meaning and overall writing style of the submitted text. The second detection signal is a stylometric heuristic analyzer implemented in pure Python, which measures structural writing characteristics.

The outputs from both detection signals are sent to the confidence scoring component. This component combines the information from both signals into a single confidence score. The confidence score is then passed to the transparency label generator, which produces the label displayed to the user.

The attribution result, confidence score, transparency label, and related information are recorded in the audit log. Finally, the Flask API returns the attribution result, confidence score, and transparency label to the creator.

If the creator disagrees with the classification, an appeal can be submitted through the **POST /appeal** endpoint. The appeal updates the content status to **under review**, records the appeal in the audit log, and returns a confirmation response to the creator.

---

## 2. System Components

### Flask API

The Flask API serves as the main entry point for the system. It receives client requests, validates user input, coordinates the detection pipeline, and returns structured JSON responses.

---

### Submission Endpoint (POST /submit)

The submission endpoint accepts text-based content for attribution analysis. It forwards the submitted text into the detection pipeline and returns the final attribution result, confidence score, and transparency label.

---

### Detection Signal 1 – Groq LLM Classification

**Property measured**

The Groq LLM measures the semantic coherence and overall writing style of the submitted text.

**Why this property differs**

Large language models can recognize writing patterns commonly found in AI-generated content, including consistent tone, repetitive phrasing, and highly structured writing.

**Blind spot**

This signal may incorrectly classify highly polished human writing, carefully edited text, or writing produced by non-native English speakers because these styles may resemble AI-generated writing.

---

### Detection Signal 2 – Stylometric Heuristics

**Property measured**

The stylometric analyzer measures structural writing characteristics such as sentence length variation, vocabulary diversity, punctuation density, and average sentence complexity.

**Why this property differs**

Human writing generally contains greater stylistic variation, while AI-generated writing often exhibits more uniform structural patterns.

**Blind spot**

This signal may not perform well on very short text, poetry, highly edited documents, or writing styles that naturally use repetitive structures.

---

### Confidence Scoring Component

The confidence scoring component combines information from both detection signals into a single confidence score that reflects the certainty of the attribution decision.

---

### Transparency Label Generator

The transparency label generator converts the attribution result and confidence score into plain-language information that can be understood by non-technical users.

---

### Audit Logger

The audit logger records every attribution decision, confidence score, signals used, and any subsequent appeals. This provides traceability and accountability for every classification made by the system.

---

### Appeal Endpoint (POST /appeal)

The appeal endpoint allows a creator to contest a classification decision. It records the creator's reasoning, updates the submission status to **under review**, and stores the appeal in the audit log.

---

### Rate Limiter

The rate limiter protects the submission endpoint by limiting how frequently requests can be made. This helps prevent abuse and improves system reliability.

---

## 3. False Positive Scenario

A false positive occurs when a piece of human-written content is incorrectly classified as AI-generated.

When this happens, the confidence score should accurately reflect any uncertainty in the classification. Rather than presenting an overly confident conclusion, the transparency label should communicate that the result is uncertain whenever appropriate.

The creator can submit an appeal explaining why the content should be reconsidered. The appeal changes the submission status to **under review** and records the appeal in the audit log for future review.

---

## 4. API Surface

The system will provide the following API endpoints:

* **POST /submit** – Accept submitted text for attribution analysis.
* **POST /appeal** – Accept a creator's appeal for a previous classification.
* **GET /log** – Retrieve the structured audit log.

---

## 5. System Flow Diagram

### Submission Flow

```text
Creator
   │
   │ Raw Text
   ▼
POST /submit
   │
   │ Validated Text
   ▼
Flask API
   │
   ├───────────────┐
   │               │
   ▼               ▼
Groq LLM     Stylometric Heuristics
(Semantic)      (Structural)
   │               │
   │ Signal Result │ Signal Result
   └───────┬───────┘
           │
           ▼
Confidence Scoring
           │
           │ Combined Confidence
           ▼
Transparency Label
           │
           │ Attribution Result
           ▼
Audit Log
           │
           │ Stored Decision
           ▼
API Response
```

### Appeal Flow

```text
Creator
   │
   │ Appeal Reason
   ▼
POST /appeal
   │
   │ Appeal Request
   ▼
Flask API
   │
   │ Status Update
   ▼
Under Review
   │
   │ Appeal Record
   ▼
Audit Log
   │
   │ Confirmation
   ▼
API Response
```

