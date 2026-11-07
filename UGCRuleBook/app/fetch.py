
import requests
import os

documents = [
    {
        "name": "grievance_2023.pdf",
        "url": "https://www.ugc.gov.in/pdfnews/4675881_Regulation.pdf"
    },
    {
        "name": "grievance_2019.pdf",
        "url": "https://www.ugc.gov.in/pdfnews/2813028_SG-Regulations-2019.pdf"
    },
    {
        "name": "ragging_2013.pdf",
        "url": "https://www.ugc.gov.in/pdfnews/8091137_gazette-antiragging-Second-Amendment.pdf"
    },
    {
        "name": "student_regulations.html",
        "url": "https://www.ugc.gov.in/regulations/UGC_Regulations_Student_Centric"
    }
]

os.makedirs("data/raw", exist_ok=True)

for document in documents:
    try:
        print("Downloading:", document["name"])

        response = requests.get(document["url"], timeout=30)
        response.raise_for_status()

        file_path = "data/raw/" + document["name"]

        with open(file_path, "wb") as file:
            file.write(response.content)

        print("Downloaded successfully!")

    except requests.exceptions.RequestException as error:
        print("Download failed:", error)

print("Download process completed.")
