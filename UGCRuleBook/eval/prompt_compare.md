# Prompt Comparison – UGCRuleBook

## Objective

Compare two system prompt versions using the same 10 student questions. The purpose is to check which prompt gives clearer, more relevant, and evidence-based answers.

## Prompt Version A – Basic Prompt

You are UGCRuleBook. Answer student questions about UGC rules using the available records. Give simple answers and mention relevant rules.

## Prompt Version B – Strict Evidence-Based Prompt

You are UGCRuleBook, an assistant that helps college students understand their rights under UGC regulations and guidelines.

- Use only information explicitly supported by the available records.
- Use simple and clear language.
- Mention the relevant rule and regulation when available.
- Do not invent rules, deadlines, contact details, or complaint procedures.
- Do not make unsupported legal conclusions.
- If information is missing, clearly say that it is not available in the current UGCRuleBook records.
- Explain where the student can complain only when the records provide that information.

## Evaluation Questions

| No. | Student Question | Version A | Version B | Better Version |
|---|---|---|---|---|
| 1 | Can I get a fee refund if I withdraw after getting a better CAP seat? | To evaluate | To evaluate | To evaluate |
| 2 | Can my college keep my original certificates after admission cancellation? | To evaluate | To evaluate | To evaluate |
| 3 | What should I do if I face ragging in college? | To evaluate | To evaluate | To evaluate |
| 4 | What can I do if my college charges fees not mentioned in its admission policy? | To evaluate | To evaluate | To evaluate |
| 5 | Can I appeal to the Ombudsperson if I am not satisfied with the SGRC decision? | To evaluate | To evaluate | To evaluate |
| 6 | What is the contact number, email, and office location of my college's Internal Complaints Committee? | To evaluate | To evaluate | To evaluate |
| 7 | How much time is allowed to process a grievance about delayed fee refund? | To evaluate | To evaluate | To evaluate |
| 8 | What can I do if my college publishes a false or misleading prospectus? | To evaluate | To evaluate | To evaluate |
| 9 | Within how many working days should the SGRC submit its report and recommendations? | To evaluate | To evaluate | To evaluate |
| 10 | What is the timeline for the Ombudsperson to resolve a student grievance? | To evaluate | To evaluate | To evaluate |

## Evaluation Criteria

1. Accuracy – Does the answer match the available records?
2. Relevance – Does it answer the student's actual question?
3. Clarity – Is the answer easy to understand?
4. Evidence – Does it mention the relevant rule or regulation?
5. Hallucination control – Does it avoid inventing missing information?

## Initial Observation

Version A uses basic instructions and may provide general answers without clearly handling missing information.

Version B includes stricter evidence-based instructions. It is designed to reduce unsupported claims and clearly identify information that is missing from the records.

## Conclusion

Version B is the preferred prompt design because it emphasizes accuracy, evidence, and transparency when answering student-rights questions.

**Note:** The question-by-question evaluation results must be filled after testing both versions with the same records and questions. The initial observation above describes the prompt designs, not completed test results.