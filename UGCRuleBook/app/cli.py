
from app.records import load_records, search, count_by, get_by_id


records = load_records()

while True:
    print("\nUGCRuleBook")
    print("1. Display all records")
    print("2. Search records")
    print("3. Count records")
    print("4. Get record by number")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        for record in records:
            print("\n", record)

    elif choice == "2":
        keyword = input("Enter keyword: ")
        results = search(records, keyword)

        for record in results:
            print("\n", record)

        print("Total results:", len(results))

    elif choice == "3":
        counts = count_by(records, "regulation_or_circular")

        for category, total in counts.items():
            print(category, ":", total)

    elif choice == "4":
        number = int(input("Enter record number (1-20): "))
        record = get_by_id(records, number)

        if record:
            print(record)
        else:
            print("Record not found")

    elif choice == "0":
        print("Thank you for using UGCRuleBook!")
        break

    else:
        print("Invalid choice")
