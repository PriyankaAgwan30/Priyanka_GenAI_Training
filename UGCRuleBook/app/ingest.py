
import json
import re
from pathlib import Path
from dataclasses import asdict

from pypdf import PdfReader

from app.models import Record


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"

SOURCE_URL = "https://www.ugc.gov.in/pdfnews/4675881_Regulation.pdf"


def read_pdf_files():

    pdf_text = {}

    for pdf_file in RAW_DIR.glob("*.pdf"):

        try:
            reader = PdfReader(str(pdf_file))

            text = ""

            for page in reader.pages:
                text += (page.extract_text() or "") + " "

            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\bde\s+nial\b", "denial", text, flags=re.IGNORECASE)

            pdf_text[pdf_file.name] = text

            print("Read:", pdf_file.name)

        except Exception as error:
            print("Could not read", pdf_file.name, ":", error)

    return pdf_text


def extract_records(pdf_text):

    text = pdf_text.get("grievance_2023.pdf", "")

    if not text:
        print("2023 grievance PDF text not found.")
        return []

    rules = [
        {
            "title": "False or Misleading Prospectus",
            "pattern": r"publication by the institution of any information in the prospectus, which is false or misleading, and not based on facts;",
            "authority": "Students' Grievance Redressal Committee (SGRC)"
        },
        {
            "title": "Withholding Student Documents",
            "pattern": r"withholding of, or refusal to return, any document.*?does not intend to pursue;",
            "authority": "Students' Grievance Redressal Committee (SGRC)"
        },
        {
            "title": "Excess Fee Demand",
            "pattern": r"demand of money in excess of that specified to be charged in the declared admission policy of the institution;",
            "authority": "Students' Grievance Redressal Committee (SGRC)"
        },
        {
            "title": "Delay or Denial of Fee Refund",
            "pattern": r"delay in, or\s+denial of, the refund of fees due to a student.*?Commission, from time to time;",
            "authority": "Students' Grievance Redressal Committee (SGRC)"
        },
        {
            "title": "Student Grievance Committee",
            "pattern": r"A complaint from an aggrieved student relating to the institution shall be addressed to the Chairperson,\s*Students.{0,2}Grievance Redressal Committee \(SGRC\)\.",
            "authority": "Chairperson, Students' Grievance Redressal Committee (SGRC)"
        },
        {
            "title": "SGRC Complaint Resolution",
            "pattern": r"The SGRC shall send its report with recommendations, if any, to the competent authority.*?15 working days from the date of receipt of the complaint\.",
            "authority": "Students' Grievance Redressal Committee (SGRC)"
        },
        {
            "title": "Appeal to Ombudsperson",
            "pattern": r"Any student aggrieved by the decision of the Students.{0,2}Grievance Redressal Committee may prefer an appeal to the Ombudsperson, within a period of fifteen days from the date of receipt of such decision\.",
            "authority": "University Ombudsperson"
        },
        {
            "title": "Ombudsperson Resolution Timeline",
            "pattern": r"The Ombudsperson shall make all efforts to resolve the grievances within a period of 30 days of receiving the appeal from the aggrieved student",
            "authority": "University Ombudsperson"
        }
    ]

    records = []

    for rule in rules:

        try:
            match = re.search(
                rule["pattern"],
                text,
                re.IGNORECASE
            )

            if not match:
                print("Rule not found:", rule["title"])
                continue

            row = {
                "rule_title": rule["title"],
                "regulation_or_circular": "UGC (Redressal of Grievances of Students) Regulations, 2023",
                "year": 2023,
                "student_right": match.group(0),
                "where_to_complain": rule["authority"],
                "source_url": SOURCE_URL
            }

            record = Record(**row)

            records.append(asdict(record))

            print("Extracted:", rule["title"])

        except Exception as error:
            print("Skipping bad record:", rule["title"], error)

    return records


def save_records(records):

    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=4, ensure_ascii=False)

        print("\nTotal records saved:", len(records))
        print("Saved to:", OUTPUT_FILE)

    except Exception as error:
        print("Error saving records:", error)


def main():

    pdf_text = read_pdf_files()

    records = extract_records(pdf_text)

    save_records(records)


if __name__ == "__main__":
    main()
