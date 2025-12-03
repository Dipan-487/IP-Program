import time
import pandas as pd
import sys
import os
import stdiomask  # Import the library for password masking
from colorama import init, Fore, Style  # Import Colorama for colored terminal text
from tabulate import tabulate   # Import tabulate for better table display

# --- Initialize Colorama ---
init(autoreset=True)

# --- Constants ---
STUDENT_FILE = 'students.csv'
MARKS_FILE = 'marks.csv'
FEES_FILE = 'fees.csv'
ATTENDANCE_FILE = 'attendance.csv'
TEACHER_FILE = 'teachers.csv'

# --- UI Helpers ---

def print_header(text):
    print("\n" + Fore.CYAN + Style.BRIGHT + "="*60)
    print(Fore.CYAN + Style.BRIGHT + f"{text.center(60)}")
    print(Fore.CYAN + Style.BRIGHT + "="*60 + "\n")

def print_error(text):
    print(Fore.RED + Style.BRIGHT + f"[-] Error: {text}")

def print_success(text):
    print(Fore.GREEN + Style.BRIGHT + f"[+] Success: {text}")

def print_table(df, headers='keys', color=Fore.CYAN):
    """
    Prints a styled dataframe using tabulate.
    It creates a COPY of the data to add colors (like Green for Paid)
    so we don't accidentally save color codes into the CSV file.
    """
    if df.empty:
        print(Fore.YELLOW + "No records found.🚨")
        return

    # Create a copy so we don't modify the original data
    display_df = df.copy()

    # --- COLOR LOGIC FOR CELLS ---
    # If there is a 'Status' column (Fees), color Paid/Pending
    if 'Status' in display_df.columns:
        display_df['Status'] = display_df['Status'].apply(
            lambda x: f"{Fore.GREEN}{x}{color}" if x == 'Paid' else f"{Fore.RED}{x}{color}"
        )
    
    # If there is a 'Marks' column, highlight high/low marks
    if 'Marks' in display_df.columns:
        # Note: We convert to string to add color, preventing math errors later
        display_df['Marks'] = display_df['Marks'].apply(
            lambda x: f"{Fore.GREEN}{x}{color}" if int(x) >= 90 else (f"{Fore.RED}{x}{color}" if int(x) < 40 else f"{Fore.YELLOW}{x}{color}")
        )

    # Print using tabulate
    # We add the main 'color' to the start so the grid lines get colored too
    print(color + tabulate(display_df, headers=headers, tablefmt='fancy_grid', showindex=False))

def check_files():
    files = [STUDENT_FILE, MARKS_FILE, FEES_FILE, ATTENDANCE_FILE, TEACHER_FILE]
    missing = []
    for f in files:
        if not os.path.exists(f):
            missing.append(f)
    
    if missing:
        print_error(f"Missing files: {', '.join(missing)}")
        print(Fore.YELLOW + "Please run 'data_generator.py' first.")
        sys.exit()

def get_remarks(avg_marks):
    if avg_marks >= 90: return Fore.GREEN + "Outstanding performance! Keep it up."
    elif avg_marks >= 75: return Fore.CYAN + "Very Good. Work a bit harder for top ranks."
    elif avg_marks >= 60: return Fore.YELLOW + "Good. Needs improvement in consistency."
    elif avg_marks >= 40: return Fore.MAGENTA + "Average. Must focus on studies."
    else: return Fore.RED + "Critical. Parents meeting required."

# ==========================================
#              STUDENT PANEL
# ==========================================

def student_menu(adm_no):
    while True:
        print_header(f"🧑‍🎓 STUDENT DASHBOARD (ID: {adm_no}) 🧑‍🎓")
        print(Fore.BLUE + "1. " + Fore.CYAN + Style.BRIGHT + "View Attendance")
        print(Fore.BLUE + "2. " + Fore.CYAN + Style.BRIGHT + "View Marks")
        print(Fore.BLUE + "3. " + Fore.CYAN + Style.BRIGHT + "View Fees Status")
        print(Fore.BLUE + "4. " + Fore.CYAN + Style.BRIGHT + "View Remarks")
        print(Fore.BLUE + "5. " + Fore.RED + Style.BRIGHT + "Logout")
        
        choice = input(Fore.YELLOW + Style.BRIGHT + "\nEnter Choice: " + Fore.RESET)
        
        if choice == '1':
            print(Fore.CYAN + "\n--- Attendance Records ---")
            df = pd.read_csv(ATTENDANCE_FILE)
            my_att = df[df['AdmissionNo'] == adm_no]
            print_table(my_att[['Month', 'PresentDays', 'TotalDays', 'Percentage']], color=Fore.CYAN)
                
        elif choice == '2':
            print(Fore.CYAN + "\n--- Exam Marks ---")
            df = pd.read_csv(MARKS_FILE)
            my_marks = df[df['AdmissionNo'] == adm_no]
            print_table(my_marks[['Exam', 'Subject', 'Marks']], color=Fore.YELLOW)
                
        elif choice == '3':
            print(Fore.CYAN + "\n--- Fee Details ---")
            df = pd.read_csv(FEES_FILE)
            my_fees = df[df['AdmissionNo'] == adm_no]
            # The print_table function handles the Green/Red coloring for Status automatically
            print_table(my_fees[['Quarter', 'Amount', 'Status']], color=Fore.CYAN)
            
        elif choice == '4':
            print(Fore.CYAN + "\n--- Performance Remarks ---")
            df = pd.read_csv(MARKS_FILE)
            my_marks = df[df['AdmissionNo'] == adm_no]
            if not my_marks.empty:
                avg = my_marks['Marks'].mean()
                print(f"Your Average Marks: {Style.BRIGHT}{avg:.2f}")
                print(f"Remark: {get_remarks(avg)}")
            else:
                print(Fore.YELLOW + "No marks available to generate remarks.")
                
        elif choice == '5':
            break
        else:
            print_error("Invalid Choice.❌")
        input(Fore.CYAN + Style.DIM + "\nPress Enter to continue...")

def student_login():
    print_header("STUDENT LOGIN")
    try:
        adm_no = int(input("Enter Admission Number: "))
        # --- USING STDIOMASK HERE ---
        password = stdiomask.getpass(prompt="Enter Password: ", mask="*")
        print()
        
        df = pd.read_csv(STUDENT_FILE)
        user = df[(df['AdmissionNo'] == adm_no) & (df['Password'] == password)]
        
        if not user.empty:
            print_success(f"Welcome {user.iloc[0]['Name']}!")
            student_menu(adm_no)
        else:
            print_error("Invalid Admission Number or Password.❌")
            input("Press Enter to try again...")
            
    except ValueError:
        print_error("Admission Number must be an integer.🚨")
        input(Fore.CYAN + Style.DIM + "Press Enter to try again...")

# ==========================================
#               ADMIN PANEL
# ==========================================

def admin_manage_students():
    while True:
        print_header("MANAGE STUDENTS")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "1. Show Students (By Class)")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "2. Add New Student")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "3. Delete Student")
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "4. Back")
        
        c = input(Fore.YELLOW + Style.BRIGHT + "\nEnter Choice: " + Fore.RESET)
        
        if c == '1':
            try:
                cls_input = input("Enter Class (1-12) or 0 for all: ")
                cls = int(cls_input)
                df = pd.read_csv(STUDENT_FILE)
                
                if cls == 0:
                    print_table(df[['AdmissionNo', 'Name', 'Class', 'Section']], color=Fore.CYAN)
                else:
                    filtered = df[df['Class'] == cls]
                    print_table(filtered[['AdmissionNo', 'Name', 'Class', 'Section']], color=Fore.CYAN)
            except ValueError:
                print_error("Invalid input.❌")

        elif c == '2':
            try:
                print(Fore.CYAN + "\n--- Add New Student ---")
                adm = int(input("Enter New Admission No: "))
                name = input("Enter Name: ")
                cls = int(input("Enter Class: "))
                sec = input("Enter Section: ")
                pwd = input("Set Password: ")
                
                df = pd.read_csv(STUDENT_FILE)
                if adm in df['AdmissionNo'].values:
                    print_error("Admission Number already exists.🚨")
                else:
                    new_data = pd.DataFrame([{
                        'AdmissionNo': adm, 'Name': name, 'Class': cls, 'Section': sec, 'Password': pwd
                    }])
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(STUDENT_FILE, index=False)
                    print_success("Student Added Successfully.✅")
            except ValueError:
                print_error("Invalid Data Entered.❌")

        elif c == '3':
            try:
                print(Fore.CYAN + "\n--- Delete Student ---")
                adm = int(input("Enter Admission No to delete: "))
                df = pd.read_csv(STUDENT_FILE)
                
                if adm in df['AdmissionNo'].values:
                    df = df[df['AdmissionNo'] != adm]
                    df.to_csv(STUDENT_FILE, index=False)
                    print_success(f"Student {adm} deleted.")
                else:
                    print_error("Student not found.🚨")
            except ValueError:
                print_error("Invalid ID.❌")

        elif c == '4':
            break
        input(Fore.CYAN + Style.DIM + "\nPress Enter to Continue...")

def admin_manage_fees():
    while True:
        print_header("MANAGE FEES")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "1. Show Pending Fees (All)")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "2. Update Payment Status")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "3. Show Revenue")
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "4. Back")
        c = input(Fore.YELLOW + Style.BRIGHT + "\nEnter Choice: " + Fore.RESET)
        
        if c == '1':
            df = pd.read_csv(FEES_FILE)
            pending = df[df['Status'] == 'Pending']
            # Pass color=Fore.CYAN, but internal logic will turn Pending RED
            print_table(pending[['AdmissionNo', 'Name', 'Class', 'Quarter', 'Amount']], color=Fore.CYAN)
            
        elif c == '2':
            try:
                adm = int(input("Enter Admission No: "))
                qtr = input("Enter Quarter (Q1/Q2/Q3/Q4): ")
                
                df = pd.read_csv(FEES_FILE)
                mask = (df['AdmissionNo'] == adm) & (df['Quarter'] == qtr)
                
                if df.loc[mask].empty:
                    print_error("Record not found.❌")
                else:
                    df.loc[mask, 'Status'] = 'Paid'
                    df.to_csv(FEES_FILE, index=False)
                    print_success("Fee Status Updated to Paid.✅")
            except Exception as e:
                print_error(str(e))

        elif c == '3':
            df = pd.read_csv(FEES_FILE)
            revenue = df[df['Status'] == 'Paid']['Amount'].sum()
            print(Fore.GREEN + Style.BRIGHT + f"\n$$ Total Revenue Collected: Rs. {revenue:,.2f} $$")
            
        elif c == '4':
            break
        input(Fore.CYAN + Style.DIM + "\nPress Enter to Continue...")

def admin_manage_marks():
    while True:
        print_header("MANAGE MARKS")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "1. View Class Marks")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "2. Update Student Marks")
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "3. Back")
        c = input(Fore.YELLOW + Style.BRIGHT + "\nEnter Choice: " + Fore.RESET)
        
        if c == '1':
            try:
                cls = int(input("Enter Class: "))
                df = pd.read_csv(MARKS_FILE)
                print_table(df[df['Class'] == cls].head(20), color=Fore.YELLOW)
                print(Fore.CYAN + "(Showing top 20 records)")
            except ValueError: pass
            
        elif c == '2':
            try:
                adm = int(input("Enter Admission No: "))
                sub = input("Enter Subject (Math/English/Science/CS/IP): ")
                exam = input("Enter Exam (Mid-Term/Finals): ")
                new_marks = int(input("Enter New Marks: "))
                
                df = pd.read_csv(MARKS_FILE)
                mask = (df['AdmissionNo'] == adm) & (df['Subject'] == sub) & (df['Exam'] == exam)
                
                if df.loc[mask].empty:
                    print_error("Record not found.❌")
                else:
                    df.loc[mask, 'Marks'] = new_marks
                    df.to_csv(MARKS_FILE, index=False)
                    print_success("Marks Updated.✅")
            except ValueError: print_error("Invalid data.❌")
            
        elif c == '3':
            break
        input(Fore.CYAN + Style.DIM + "\nPress Enter to Continue...")

def admin_menu():
    print_header("ADMIN LOGIN")
    user = input("Admin Username: ")
    # --- USING STDIOMASK HERE ---
    pwd = stdiomask.getpass(prompt= "Admin Password: ", mask= "*")
    print()
    
    if user == "admin" and pwd == "admin123":
        while True:
            print_success("Welcome, Admin!")
            print_header("🧑‍💻 ADMIN DASHBOARD 🧑‍💻")
            print(Fore.BLUE + "1. " + Fore.CYAN + Style.BRIGHT + "Manage Student Details")
            print(Fore.BLUE + "2. " + Fore.CYAN + Style.BRIGHT + "Manage Fees & Revenue")
            print(Fore.BLUE + "3. " + Fore.CYAN + Style.BRIGHT + "Manage Marks")
            print(Fore.BLUE + "4. " + Fore.CYAN + Style.BRIGHT + "View Teachers")
            print(Fore.BLUE + "5. " + Fore.RED + Style.BRIGHT + "Logout")
            
            choice = input(Fore.YELLOW + Style.BRIGHT + "\nEnter Choice: " + Fore.RESET)
            
            if choice == '1': admin_manage_students()
            elif choice == '2': admin_manage_fees()
            elif choice == '3': admin_manage_marks()
            elif choice == '4':
                df = pd.read_csv(TEACHER_FILE)
                print_table(df, color=Fore.MAGENTA)
                input(Fore.CYAN + Style.DIM + "\nPress Enter to Continue...")
            elif choice == '5':
                break
            else: print_error("Invalid Choice.❌")
    else:
        print_error("Access Denied!🚨")
        input(Fore.CYAN + Style.DIM + "Press Enter to Continue...")

# ==========================================
#               MAIN PROGRAM
# ==========================================

def main():
    check_files()
    while True:
        # ASCII Art with Color
        print(Fore.MAGENTA + Style.BRIGHT + """
    .-------------------------------------------------------.
    |           🏫 SCHOOL MANAGEMENT SYSTEM 🏫               |
    '-------------------------------------------------------'
        """)
        print(Fore.GREEN + Style.BRIGHT + "1. Student Login")
        print(Fore.RED + Style.BRIGHT + "2. Admin Login")
        print(Fore.CYAN + Style.BRIGHT + "3. Exit")
        
        choice = input(Fore.YELLOW + Style.BRIGHT + "\nEnter Choice: " + Fore.RESET)
        
        if choice == '1':
            student_login()
        elif choice == '2':
            admin_menu()
        elif choice == '3':
            print(Fore.MAGENTA + Style.BRIGHT + "\n🙏 Thank you for using the School Management System 🙏\n")
            sys.exit()
        else:
            print_error("Invalid Choice.❌")
            input()

if __name__ == "__main__":
    print(Fore.GREEN + Style.NORMAL + "INTIALIZING SCHOOL MANAGEMENT SYSTEM...")
    time.sleep(2)
    print(Fore.GREEN + Style.NORMAL + "LOADING MODULES...")
    time.sleep(2)
    print(Fore.GREEN + Style.NORMAL + "SYSTEM READY!")
    time.sleep(1)
    main()