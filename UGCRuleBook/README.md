
# UGCRuleBook

## 1. Product
UGCRuleBook is a student-rights information system that helps college students understand their rights under University Grants Commission (UGC) regulations, guidelines, and circulars.

It focuses on fee refunds, original certificate retention, ragging complaints, student grievances, Ombudsperson, and sexual-harassment redressal.

## 2. User
College students, especially first-year students, students withdrawing from admission, and students facing institutional issues.

## 3. Problem
Students often find it difficult to understand their rights because official UGC regulations and notifications are lengthy and written in formal language.

For example, a student who receives a better CAP seat after taking admission at another college may face difficulties getting admission fees and original certificates returned.

## 4. Data Source
1. UGC Student-Centric Regulations:
   https://www.ugc.gov.in/regulations/UGC_Regulations_Student_Centric

2. UGC Regulation PDF:
   https://www.ugc.gov.in/pdfnews/4675881_Regulation.pdf





## How to Run

### 1. Open the project folder

```bash
cd UGCRuleBook
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 4. Install required packages

```bash
python -m pip install -r requirements.txt
```

### 5. Start the FastAPI server

```bash
python -m uvicorn app.main:app --reload
```

### 6. Open the API documentation

Visit:

http://127.0.0.1:8000/docs

### 7. Run the data analysis

```bash
python -m analysis.explore
```

## API Endpoints

- `GET /health` – Check API status.
- `GET /records` – Display records.
- `GET /records/{id}` – Get a record by ID.
- `GET /search?q=...` – Search records using TF-IDF.
- `POST /questions` – Submit a student question and find matching records.