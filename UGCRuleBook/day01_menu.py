
while True:

    print("1. About UGCRuleBook")
    print("2. Sample Student Rights Questions You Can Ask")
    print("3. Check some rules")
    print("0. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":
        print("\nUGCRuleBook helps students understand their rights under UGC regulations.")

    elif choice == "2":
        print("1. How. can I get refund from my college?")
        print("2. Can my college keep my original certificates?")
        print("3. How can I report ragging?")

    elif choice == "3":
        topic = input("\nEnter topic (ragging / refund): ")

        if topic == "refund":
            print("Check UGC fee-refund policy.")
        elif topic == "ragging":
            print("Check UGC Anti-Ragging Regulations.")
        else:
            print("Invalid topic. Please try again.")

    elif choice == "0":
        break

    else:
        print("Invalid choice. Please enter a valid option.")
