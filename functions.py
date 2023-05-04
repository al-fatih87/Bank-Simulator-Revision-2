import DatabaseConnection
import random
import locale

# We connect into the Customers table in the bank database
trigger = DatabaseConnection.sql.connect(host=DatabaseConnection.host, user=DatabaseConnection.user,
                                         password=DatabaseConnection.password, database="Customers")
trigger_handle = trigger.cursor()


# ==============Creating bank account=====================


def create_account():  # Function to create bank account
    full_name = input("Enter Full Name: \n")
    phone_number = input("Enter Phone Number: \n")
    account_number = random.randint(1234567890, 9999999999)
    account_balance = 1000

    acc_field = "INSERT INTO customers (Phone, Name, Account_Number, Balance) VALUES (%s, %s, %s, %s)"
    acc_details = (str(phone_number), str(full_name), str(account_number), str(account_balance))  # convert to string
    try:
        trigger_handle.execute(acc_field, acc_details)
        trigger.commit()
        print(trigger_handle.rowcount, "Process completed!")
        print("===============================================")
        print("Congratulations! Your account was successfully created.")
        print(f"Your account number is: {account_number} \n"
              f"And your account name is: {full_name} \n"
              f"Thanks for choosing XBZ Bank.")
    except Exception as ex:
        print("Account creation failed")
        print(ex)
    print("===============================================\n")
    print("What would you like to do next? \n")
    ussd_dail()


# ==============Cash Deposit=====================


def cash_deposit():
    cus_input = input("Enter account Number: \n")
    deposit = input("Enter deposit amount: \n")
    deposit_amount = float(deposit)
    # we select account balance from the user input
    try:
        acc_balance = "SELECT Balance FROM Customers WHERE Account_Number = %s"
        bal_value = (str(cus_input),)  # convert the input to string
        trigger_handle.execute(acc_balance, bal_value)
        acc_bal_tpl = trigger_handle.fetchone()
        acc_bal = acc_bal_tpl[0]
    except Exception as ex:
        print("Failed to carry out operation")
        print(ex)
    # We convert the string tuple to float/int for calculation
    old_bal = float(acc_bal)
    new_bal = old_bal + deposit_amount

    # We update record on database
    try:
        acc_balance = "UPDATE Customers SET Balance = %s WHERE Account_Number = %s"
        bal_value = (str(new_bal), str(cus_input))  # convert the input to string
        trigger_handle.execute(acc_balance, bal_value)
        trigger.commit()
    except Exception as ex:
        print("Failed to carry out operation")
        print(ex)
    print("Cash deposit successful! Account balance has been updated.")
    print("===============================================\n")
    print("What would you like to do next? \n")
    ussd_dail()


# ==============Account Balance=====================


locale.setlocale(locale.LC_MONETARY, 'en_NG')  # We set up local currency (Nigerian Naira)


def account_bal_retrieval():
    cus_input = input("Enter account Number: \n")
    # we select account balance from the user input
    try:
        acc_balance = "SELECT Balance FROM Customers WHERE Account_Number = %s"
        bal_value = (str(cus_input),)  # convert the input to string
        trigger_handle.execute(acc_balance, bal_value)
        acc_bal_tpl = trigger_handle.fetchone()
        acc_bal = acc_bal_tpl[0]
        acc_bal_currency = locale.currency(acc_bal, grouping=True)
    except Exception as ex:
        print("Failed to carry out operation")
        print(ex)

    #   we select account name from the user input
    acc_name = "SELECT Name FROM Customers WHERE Account_Number = %s"
    name_value = (str(cus_input),)
    trigger_handle.execute(acc_name, name_value)
    name_display_tpl = trigger_handle.fetchone()
    name_display = name_display_tpl[0]

    print(f"Dear {name_display},\n"
          f"your account balance is:\n"
          f" {acc_bal_currency}")
    print("===============================================\n")
    print("What would you like to do next? \n")
    ussd_dail()


# ==============Transfers and Withdrawals=====================


def cash_transfer():
    sender_acc_input = input("Please enter your account Number: \n")
    transfer_amount = input("Enter transfer amount: \n")
    con_transfer_amount = float(transfer_amount)
    verify_tx_amount = locale.currency(con_transfer_amount, grouping=True)
    receiver_acc_num = input("Enter receiver's account number: \n")

    # We verify receiver's account details
    try:
        verify_receiver = "SELECT Name FROM Customers WHERE Account_Number = %s"
        receiver_name_value = (str(receiver_acc_num),)
        trigger_handle.execute(verify_receiver, receiver_name_value)
        name_display_tpl = trigger_handle.fetchone()
        name_display = name_display_tpl[0]
        print(f"You are sending {verify_tx_amount} to {name_display} ({receiver_acc_num}). \n"
              f" Do you confirm this to be correct? Yes/No")
        verify_response = input("")
        if verify_response.lower() == "yes":

            # We debit sender's account
            # first, we get account balance of sender
            try:
                sender_balance_query = "SELECT Balance FROM Customers WHERE Account_Number = %s"
                sender_bal_value = (str(sender_acc_input),)  # convert the input to string
                trigger_handle.execute(sender_balance_query, sender_bal_value)
                sender_acc_bal_tpl = trigger_handle.fetchone()
                sender_acc_bal = sender_acc_bal_tpl[0]
            except Exception as ex:
                print("Failed to carry out operation")
                print(ex)

            # 1. We convert the string tuple to float for calculation
            sender_old_bal = float(sender_acc_bal)
            sender_new_bal = sender_old_bal - con_transfer_amount
            if sender_new_bal < 1:
                print("Sorry, you do not have sufficient funds to carry out this transaction."
                      "Kindly fund your account and try again.")
                quit()
            else:
                # We update receiver's record on database with new balance
                try:
                    update_query = "UPDATE Customers SET Balance = %s WHERE Account_Number = %s"
                    sender_new_bal_value = (str(sender_new_bal), str(sender_acc_input))  # convert the input to string
                    trigger_handle.execute(update_query, sender_new_bal_value)
                    trigger.commit()
                except Exception as ex:
                    print("Failed to carry out operation")
                    print(ex)

            # 2. We credit receiver's account with the imputed amount
            try:
                receiver_balance_query = "SELECT Balance FROM Customers WHERE Account_Number = %s"
                receiver_bal_value = (str(receiver_acc_num),)  # convert the input to string
                trigger_handle.execute(receiver_balance_query, receiver_bal_value)
                acc_bal_tpl = trigger_handle.fetchone()
                acc_bal = acc_bal_tpl[0]
            except Exception as ex:
                print("Failed to carry out operation")
                print(ex)

            # 2. We convert the string tuple to float for calculation
            old_bal = float(acc_bal)
            new_bal = old_bal + con_transfer_amount

            # We update receiver's record on database with new balance
            try:
                update_query = "UPDATE Customers SET Balance = %s WHERE Account_Number = %s"
                new_bal_value = (str(new_bal), str(receiver_acc_num))  # convert the input to string
                trigger_handle.execute(update_query, new_bal_value)
                trigger.commit()
            except Exception as ex:
                print("Failed to carry out operation")
                print(ex)

            print("Transaction successful! Money has been sent.")
            print("===============================================\n")
            # ussd_dail()
        else:
            print("Transaction Cancelled."
                  "Thanks for banking with us.")
            # ussd_dail()
    except Exception as ex:
        print("Operation failed.")
        print(ex)

    ussd_dail()


# ==========================USSD DIAL===========================


def ussd_dail():
    user_action = input("Please select option (corresponding figure: \n"
                        "1: Check Account Balance\n"
                        "2: Deposit\n"
                        "3: Transfer\n"
                        "4: Create Account\n"
                        "5: Quit\n")

    if user_action == "1":
        account_bal_retrieval()
    elif user_action == "2":
        cash_deposit()
    elif user_action == "3":
        cash_transfer()
    elif user_action == "4":
        create_account()
    elif user_action == "5":
        print("Thank you for banking with us.")
        quit()
    else:
        print("That input was not recognised. Please try again later")
        quit()


# ==========================PROMPT==========================


def prompt_dail():
    print("====================================================")
    print("Welcome to XBZ Bank, your owned home banking system.\n"
          "Developed by Muhammad .A. Oyonumoh.\n"
          "====================================================\n"
          "This is a Simulator Bank to demonstrate what happens \n"
          "at the back end with customer service when you walk\n"
          "into a bank for transaction.\n"
          "Hope you enjoy it.\n")
    print("====================================================")
    qus_operation = input("Please select an option of corresponding figure: \n"
                          "1: System Setup\n"
                          "2: Bank Operation\n")
    if qus_operation == "1":
        system_setup()
    elif qus_operation == "2":
        ussd_dail()
    else:
        quit()


def system_setup():
    qus = input("This operation will setup a database, and a customer table for your banking system.\n"
                "Please confirm you have your MySQL service running on your local PC or you are connected\n"
                "to a remote server. For remote server, please modify the login parameter on the "
                "DatabseConnection.py module.\n"
                "Please confirm you have not already initiated this process.\n"
                "===================================================================================================\n"
                "Please confirm, do you have a database setup already? Yes or No\n")

    if qus.lower() == "no":
        print("setting up database...")
        print("===============================================\n")
        DatabaseConnection.sql_connect()
        try:
            DatabaseConnection.create_db()
        except Exception as ex:
            print("Failed to create database")
            print(ex)
        try:
            DatabaseConnection.create_table()
        except Exception as ex:
            print("Failed to create table")
            print(ex)
        try:
            DatabaseConnection.customer_dbconnect()
        except Exception as ex:
            print("Failed to connect to customer table")
            print(ex)
        print("=========================================================")
        print("Database and relevant customer table has been created,\n "
              "and connected to successfully.\n"
              "Please re-run the program to start banking now")
    else:
        ussd_dail()


prompt_dail()
