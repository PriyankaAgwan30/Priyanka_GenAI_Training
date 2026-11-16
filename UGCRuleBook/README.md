# UGCRuleBook – UGC Student Rights Assistant

## 1. Product

UGCRuleBook is a student-rights information system that helps college students understand their rights under University Grants Commission (UGC) regulations, guidelines, and circulars.

Students can ask questions in simple language and get answers based on official UGC documents.

The project focuses on topics such as:
- Fee refunds after admission withdrawal
- Return of original certificates
- Ragging complaints
- Student grievance redressal
- Ombudsperson
- Sexual-harassment redressal

The main goal is to make important student-rights information easier to find and understand.

## 2. Target Users

UGCRuleBook is designed for:
- College students, especially first-year students
- Students who want to withdraw their admission
- Students facing problems with college fees or original certificates
- Students who want to understand how to submit a complaint against their institution

## 3. Problem Statement

Many students do not know their rights because official UGC regulations and notifications are lengthy and written in formal language.

Finding the correct information in these documents can take time and can be confusing.

For example, a student may get a better CAP seat after taking admission at another college. In such a situation, the student may face difficulties getting the admission fees refunded or original certificates returned.

UGCRuleBook aims to make this information easier to access by allowing students to ask questions and receive answers based on official documents.

## 4. Data Sources

The project uses UGC regulations and official documents as its information sources.

1. **UGC Student-Centric Regulations**

   https://www.ugc.gov.in/regulations/UGC_Regulations_Student_Centric

2. **UGC Regulation PDF**

   https://www.ugc.gov.in/pdfnews/4675881_Regulation.pdf

The project also uses relevant documents related to student grievances, ragging, and other student-rights topics.

## 5. Technologies Used

- **Python:** Main programming language
- **FastAPI:** Building API endpoints
- **Sentence Transformers:** Converting text into numerical embeddings
- **ChromaDB:** Storing document embeddings and retrieving relevant information
- **Google Gemini API:** Generating answers from retrieved information
- **PyPDF:** Extracting text from PDF documents
- **BeautifulSoup:** Extracting text from HTML documents

## 6. How the Project Works

UGCRuleBook uses Retrieval-Augmented Generation (RAG).

The working process is:

1. Load UGC PDF and HTML documents.
2. Extract and clean the text from these documents.
3. Divide the text into smaller parts called chunks.
4. Generate embeddings using the Sentence Transformers model.
5. Store the chunks and embeddings in ChromaDB.
6. When a student asks a question, retrieve the most relevant chunks.
7. Send the retrieved information to Google Gemini to generate an answer.
8. Return the answer along with source citations.

The system uses retrieved document information to answer questions. If the available documents do not contain enough information to answer a question, it responds with **"I don't know"** instead of making up an answer.

## 7. Project Structure

```text
UGCRuleBook/
│
├── app/
│   ├── chunking.py
│   ├── embed.py
│   ├── vectorstore.py
│   ├── llm.py
│   ├── rag.py
│   └── main.py
│
├── data/
│   ├── raw/
│   └── chroma_db/
│
├── eval/
│   ├── eval_set.json
│   ├── run_eval.py
│   ├── prompt_compare.md
│   └── search_results.md
│
├── analysis/
│   └── explore.py
│
├── requirements.txt
└── README.md
```

## 8. API Endpoints

The project provides API endpoints through FastAPI.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check whether the API is running |
| GET | `/records` | Display available student-rights records |
| GET | `/records/{id}` | Get a record using its ID |
| GET | `/search?q=...` | Search records using TF-IDF |
| POST | `/questions` | Submit a student question and find matching records |
| POST | `/ask` | Ask a question and receive a RAG-based answer with citations |

### Example: POST /ask

Request:

```json
{
  "question": "Can a college withhold original certificates to force fee payment?"
}
```

The response contains:
- The student's question
- An answer generated using retrieved UGC information
- Citations showing the source documents and relevant pages

## 9. Day 8 – RAG Evaluation

To check how well the system retrieves relevant information, two configurations were tested using the same set of 15 questions.

The configurations used different chunk sizes, overlaps, and Top-K values.

### Configuration Comparison

| Evaluation Metric | A - Baseline | B - Alternative |
|---|---:|---:|
| Chunk Size | 800 | 500 |
| Chunk Overlap | 150 | 100 |
| Top-K | 5 | 3 |
| Total Chunks | 161 | 261 |
| Keyword Coverage | 95.24% | 83.33% |
| Retrieval Hit Rate | 100% | 100% |
| Unsupported Question Rejection | 100% | 100% |

### Selected Configuration: A - Baseline

The baseline configuration performed better in the evaluation.

Selected settings:

- Chunk Size: 800
- Chunk Overlap: 150
- Top-K: 5

It achieved 95.24% keyword coverage while maintaining a 100% retrieval hit rate and 100% rejection rate for the unsupported question.

Therefore, Configuration A was selected for the project.

### Evaluation Dataset

- Total questions: 15
- Answerable questions: 14
- Unsupported questions: 1

The unsupported question checks whether the system correctly responds with "I don't know" when the answer is not available in the documents.

*Note: These results are from a keyword-based retrieval evaluation. They measure retrieval performance and unsupported-question handling, not the factual accuracy of every generated answer.*

## 10. How to Run the Project

### Step 1: Open the project folder

```bash
cd UGCRuleBook
```

### Step 2: Create a virtual environment

```bash
python3.12 -m venv myenv
```

### Step 3: Activate the virtual environment

```bash
source myenv/bin/activate
```

### Step 4: Install required packages

```bash
python -m pip install -r requirements.txt
```

### Step 5: Configure the Gemini API

Create a `.env` file in the project folder and add your Gemini configuration:

```text
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own API key. Do not upload the `.env` file or share your API key publicly.

### Step 6: Start the FastAPI server

```bash
python -m uvicorn app.main:app --reload
```

### Step 7: Open the API documentation

Visit:

http://127.0.0.1:8000/docs

You can test the available API endpoints from the Swagger UI.

### Step 8: Run the data analysis

```bash
python -m analysis.explore
```

### Step 9: Run the RAG evaluation

```bash
PYTHONPATH=. python -u eval/run_eval.py
```

This runs both configurations and displays their evaluation results.

## 11. Project Goal

The goal of UGCRuleBook is to help students understand their rights without having to read lengthy official documents on their own.

By combining document retrieval and language generation, the project provides a simpler way to find information about UGC regulations and student-related issues.

The answers are based on available source documents, with citations to help students refer to the original information.