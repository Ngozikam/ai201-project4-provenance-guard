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


### POST /submit

**Purpose**

Accept submitted text for attribution analysis.

**Accepts**

- Creator ID
- Submitted text

**Returns**

- Content ID
- Attribution result
- Confidence score
- Transparency label

---

### POST /appeal

**Purpose**

Allow the creator to contest a previous classification.

**Accepts**

- Content ID
- Creator's appeal explanation

**Returns**

- Updated submission status
- Confirmation that the appeal was received

---

### GET /log

**Purpose**

Retrieve the structured audit log.

**Returns**

- Attribution decisions
- Confidence scores
- Detection signals used
- Appeal records (if any)

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

---

# Milestone 2: System Specification

## 6. Detection Signals

### Signal 1 – Groq LLM Classification

**Purpose**

This signal analyzes the semantic meaning, logical flow, tone, and overall writing style of the submitted text.

**Output**

The output of the Groq classifier will be converted into a normalized confidence score between 0.0 and 1.0 for use by the confidence scoring component., where:

- 0.0 indicates strong evidence of human-written content.
- 1.0 indicates strong evidence of AI-generated content.

**Why this signal is used**

The LLM evaluates semantic relationships and writing style that cannot be measured using simple statistical features.

---

### Signal 2 – Stylometric Heuristics

**Purpose**

This signal measures structural writing characteristics using pure Python.

The heuristics include:

- Sentence length variance
- Type-token ratio (vocabulary diversity)
- Punctuation density
- Average sentence complexity

**Output**

The stylometric analyzer also produces a normalized score between **0.0 and 1.0**.

- Lower values indicate more human-like writing patterns.
- Higher values indicate more AI-like structural patterns.

**Why this signal is used**

Unlike the LLM, this signal measures measurable statistical characteristics rather than semantic meaning.

---

### Combining the Signals

Both signals contribute to the final confidence score.

Proposed weighting:

- Groq LLM: **70%**
- Stylometric Heuristics: **30%**

Combined confidence score:

Final Score = (0.70 × Groq Score) + (0.30 × Stylometric Score)

This weighted approach gives greater importance to semantic analysis while still incorporating measurable structural characteristics.

---

## 7. Uncertainty Representation

The confidence score represents how certain the system is about its attribution decision.

Confidence ranges:

| Confidence Score | Classification |
|-----------------|----------------|
| 0.85 – 1.00 | High-confidence AI |
| 0.60 – 0.84 | Uncertain |
| 0.00 – 0.59 | High-confidence Human |

The system intentionally uses a broad uncertainty range because false positives are more harmful than false negatives on a creative platform.

For example:

A confidence score of **0.60** means the system does not have enough evidence to confidently classify the content as either AI-generated or human-written. Instead of making a strong claim, the transparency label informs readers that the result is uncertain.

---

## 8. Transparency Label Design

### High-confidence AI

> **Likely AI-Generated**
>
> This content appears likely to have been generated using artificial intelligence.
>
> Confidence: High
>
> This assessment was produced automatically and may not always be correct.

---

### High-confidence Human

> **Likely Human-Written**
>
> This content appears likely to have been written by a human author.
>
> Confidence: High
>
> This assessment was produced automatically and may not always be correct.

---

### Uncertain

> **Uncertain Attribution**
>
> The system could not confidently determine whether this content was written by a human or generated using artificial intelligence.
>
> Confidence: Moderate
>
> Additional review may be required.

---

## 9. Appeals Workflow

Only the original creator may submit an appeal.

The appeal must include:

- Content ID
- Creator explanation
- Submission timestamp

When an appeal is received:

1. The content status changes from **classified** to **under_review**.
2. The creator's explanation is stored.
3. The appeal is recorded in the audit log.
4. The original attribution result is preserved for traceability.

When a human reviewer opens the appeal queue, they should be able to see:

- Original submitted text
- Groq confidence score
- Stylometric confidence score
- Final confidence score
- Transparency label
- Creator explanation
- Current review status
- Timestamp

---

## 10. Anticipated Edge Cases

### Edge Case 1

A poem containing repeated words and intentionally simple vocabulary.

Because poetry often uses repetition and minimal punctuation, the stylometric heuristics may incorrectly classify the poem as AI-generated.

---

### Edge Case 2

A carefully edited academic essay written by a human.

Highly polished academic writing may resemble AI-generated writing, causing the LLM classifier to assign a higher AI confidence score.

---

### Edge Case 3

Very short submissions.

Short text provides insufficient information for both semantic and stylometric analysis, making reliable attribution difficult.

---

## 11. Architecture

The Provenance Guard system accepts text submissions through the Flask API. Submitted content flows through two independent detection signals before being combined into a confidence score. The resulting transparency label is presented to the creator while every decision is stored in the structured JSON audit log.

Creators who disagree with the decision may submit an appeal through the appeal endpoint. The system updates the submission status, records the appeal, and preserves both the original classification and the appeal information for future review.

## Submission Flow

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

---


---

## 12. AI Tool Plan

### Milestone 3 – Submission Endpoint and First Detection Signal

During Milestone 3, I will use an AI coding assistant to help implement the Flask application based on the architecture and detection signal specifications developed in this planning document.

The AI tool will receive the following sections as context:

* Detection Signals
* Architecture

The implementation for this milestone will include:

- Flask application skeleton
- POST /submit endpoint
- Groq LLM classification function

After generating the code, I will verify that:

* The Flask application starts successfully.
* The `/submit` endpoint accepts text submissions.
* The Groq classifier executes correctly on several sample inputs.
* The endpoint returns a confidence score for each submission.

---

### Milestone 4 – Second Detection Signal and Confidence Scoring

During Milestone 4, I will use the AI tool to implement the second detection signal and combine both signals into a single confidence score.

I will provide the AI tool with the following sections:

* Detection Signals
* Uncertainty Representation
* Architecture

I will ask the AI tool to generate:

* The stylometric heuristic analyzer
* The confidence scoring logic
* The signal-combination algorithm

After implementation, I will verify that:

* Human-written and AI-generated samples receive different confidence scores.
* The confidence score changes meaningfully across different writing styles.
* The uncertainty range behaves as designed.

---

### Milestone 5 – Production Layer

During Milestone 5, I will use an AI coding assistant to implement the production features of Provenance Guard.

To provide sufficient context, I will use the following sections from this planning document:

* Transparency Labels
* Appeals Workflow
* Architecture

Based on these specifications, I will use the AI tool to assist with implementing:

* The transparency label generation logic
* The `POST /appeal` endpoint
* Structured JSON audit logging

After implementation, I will test the system to ensure that:

* All three transparency label variants are displayed correctly.
* Submitting an appeal updates the content status to **under_review**.
* Every attribution decision and appeal is recorded in the structured JSON audit log.
