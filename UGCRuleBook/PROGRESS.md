# UGCRuleBook – Final Progress

Status: **Complete**

## Day 14 – Interview story and portfolio polish

- [x] Added the 60-second project pitch and 10 interview answers.
- [x] Documented overlapping and time-bound rules as the hardest problem.
- [x] Added regulator, academic-year, policy-source, and uncertainty guidance.
- [x] Updated the README with architecture, setup, deployment, limitations,
  final validation, and live demo information.
- [x] Closed the unresolved prompt-comparison placeholders.
- [x] Prepared the live URL, README, failure story, and measured evidence.

## Day 15 – Final test and Demo Day

- [x] Pytest suite executed: 39 tests passed.
- [x] Ruff lint executed: all checks passed.
- [x] Retrieval evaluation executed against `eval/eval_set.json`.
- [x] Live API health endpoint verified with HTTP 200.
- [x] Demo rehearsal script completed twice.
- [x] Q&A answers rehearsed.
- [x] Final README and interview documentation completed.

## Final evidence

| Check | Result |
|---|---|
| Automated tests | 39 passed |
| Lint | All checks passed |
| Retrieval evaluation | A - Baseline; 92.86% keyword coverage |
| Retrieval hit rate | 100.00% |
| Unsupported rejection | 100.00% |
| Live health endpoint | HTTP 200 |
| Live API | https://ugcrulebook-api.onrender.com |
| Health route | https://ugcrulebook-api.onrender.com/health |

## Demo rehearsal log

### Rehearsal 1

- **Duration:** 5 minutes
- **Status:** Complete
- **Covered:** Architecture, live health check, sample fee-refund question,
  source citations, provider fallback, and limitations.

### Rehearsal 2

- **Duration:** 5 minutes
- **Status:** Complete
- **Covered:** Citation verification, unsupported-information behavior,
  deployment setup, one measured failure, and the hardest engineering problem.

## Demo flow

1. Open the live API health endpoint.
2. Open the demo README and architecture.
3. Ask a fee-refund or grievance question.
4. Point out the retrieved source, page, or section citation.
5. Show the explicit limitation around academic year and regulator.
6. Explain the provider fallback and bounded retry behavior.
7. Give the hardest-problem story in 60 seconds.
