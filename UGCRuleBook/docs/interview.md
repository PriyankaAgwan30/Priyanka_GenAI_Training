# UGCRuleBook Interview Preparation

## 60-second pitch

UGCRuleBook is a document-grounded student-rights assistant for college
students. It retrieves UGC regulations and related source documents, answers
questions in plain language, and returns page or section citations. The backend
is FastAPI, documents are embedded and indexed in ChromaDB, and responses use
Google Gemini with a fallback to retrieved source excerpts when the provider is
unavailable. Streamlit provides the demo UI, and Docker Compose supports local
and deployed operation. My key engineering contribution was making the system
evidence-based: it validates queries, rejects unsupported requests, preserves
source citations, logs latency and token usage, and returns a clear provider
error or grounded fallback instead of inventing an answer.

## Likely interview questions

### 1. Why did you build UGCRuleBook?

Students often need to understand fee refunds, certificate withholding,
ragging complaints, and grievance procedures, but the relevant regulations are
long and difficult to navigate. The project makes those public documents easier
to search while keeping official sources visible.

### 2. What problem does the RAG pipeline solve?

It narrows a student's question to relevant document chunks before generation,
which reduces reliance on the language model's general knowledge and lets the
answer include specific citations.

### 3. How does retrieval work?

The raw PDFs and HTML are extracted and chunked. Sentence Transformer
embeddings represent each chunk, ChromaDB indexes those embeddings, and semantic
search retrieves the closest chunks for a query.

### 4. What happens when the Gemini provider fails?

The system has bounded timeouts and provider retries. A temporary provider
error returns a clear 503 response. The document-grounded path can also fall
back to retrieved excerpts and citations instead of returning an empty answer.

### 5. How do you prevent unsupported answers?

The system uses strict evidence prompts, relevance thresholds, source
citations, and domain-specific unsupported-response handling. Missing
college-specific data is identified instead of guessed.

### 6. How did you measure quality?

The evaluation set covers 15 answerable or unsupported questions. It compares
chunk size, overlap, and top-K settings using keyword coverage, retrieval hit
rate, and unsupported-question rejection. The automated suite verifies API,
RAG, vectorstore, record, tool, and LLM behavior.

### 7. What was the hardest bug or engineering problem?

Overlapping and time-bound rules were the hardest problem. Refund cut-offs
change by academic year, a circular may say that policy continues until revised,
and AICTE or state bodies may also regulate engineering colleges. The bot must
identify the relevant academic year and regulator or state, then state which
policy and source it used rather than silently applying one nationwide default.
The implementation therefore avoids claiming that a single result determines a
regulator or cut-off; it asks users to confirm institution and policy details
and shows the official source used.

### 8. How do you handle security and prompt injection?

The API validates question length and tests demonstrate that instructions asking
it to reveal prompts or ignore prior instructions do not bypass retrieval.
Environment secrets are supplied through environment variables and are not
stored in source code.

### 9. How did you improve performance and reliability?

I used lazy loading for expensive AI components, response caching, bounded
LLM retries and timeouts, latency and token logging, and Docker images that
include a prebuilt ChromaDB index.

### 10. What would you improve next?

I would add richer metadata for academic year, institution type, state,
regulator, effective date, revision date, and superseded rules. I would also
add regulator-aware policy selection, document freshness checks, stronger
answer citations, and a live answer-quality evaluation with human review.

## Demo Day story

One failure I fixed was provider and deployment reliability. Gemini provider
errors could previously become unclear server failures, and the deployment
configuration could lose the API URL. I added bounded provider retries, typed
fallback behavior, explicit 502/503 responses, and a deployed API URL
configuration for the UI. I measured this by running 39 automated tests,
the Ruff lint check, the retrieval evaluation, and an HTTP health check against
the live Render service.
