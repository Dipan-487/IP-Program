import pandas as pd
import random

# --- Configuration ---
classes = range(1, 13) # Classes 1 to 12
sections = ['A', 'B']
subjects_list = ['Math', 'English', 'Science', 'CS', 'IP']
exam_types = ['Mid-Term', 'Finals']
teacher_names = ['Mr. Sharma', 'Mrs. Gupta', 'Mr. Singh', 'Ms. Lee', 'Mr. Khan', 'Mrs. Davis']

# --- Helper Functions to Generate Dummy Data ---

def generate_students():
    data = []
    adm_counter = 1001
    
    for cls in classes:
        # Create at least 10 students per class
        for i in range(10):
            student = {
                'AdmissionNo': adm_counter,
                'Name': f'Student_{adm_counter}',
                'Class': cls,
                'Section': random.choice(sections),
                'Password': f'pass{adm_counter}' # Simple password for login
            }
            data.append(student)
            adm_counter += 1
    return pd.DataFrame(data)

def generate_marks(students_df):
    data = []
    for index, row in students_df.iterrows():
        adm_no = row['AdmissionNo']
        cls = row['Class']
        
        # Assign marks for different exams and subjects
        for exam in exam_types:
            for sub in subjects_list:
                data.append({
                    'AdmissionNo': adm_no,
                    'Name': row['Name'],
                    'Class': cls,
                    'Exam': exam,
                    'Subject': sub,
                    'Marks': random.randint(35, 100)
                })
    return pd.DataFrame(data)

def generate_fees(students_df):
    data = []
    for index, row in students_df.iterrows():
        # Monthly fee logic based on class
        base_fee = 2000 + (row['Class'] * 500)
        
        # Generating data for 3 quarters
        for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            status = random.choice(['Paid', 'Paid', 'Paid', 'Pending']) # Mostly paid
            data.append({
                'AdmissionNo': row['AdmissionNo'],
                'Name': row['Name'],
                'Class': row['Class'],
                'Quarter': quarter,
                'Amount': base_fee,
                'Status': status
            })
    return pd.DataFrame(data)

def generate_attendance(students_df):
    data = []
    months = ['April', 'May', 'July', 'August', 'September']
    for index, row in students_df.iterrows():
        for month in months:
            total_days = 24
            present = random.randint(15, 24)
            data.append({
                'AdmissionNo': row['AdmissionNo'],
                'Name': row['Name'],
                'Month': month,
                'PresentDays': present,
                'TotalDays': total_days,
                'Percentage': round((present/total_days)*100, 2)
            })
    return pd.DataFrame(data)

def generate_teachers():
    data = []
    tid = 1
    for name in teacher_names:
        for sub in subjects_list:
            data.append({
                'TeacherID': f'T00{tid}',
                'Name': name,
                'Subject': sub,
                'Salary': random.randint(30000, 60000)
            })
            tid += 1
            if tid > 15: break 
    return pd.DataFrame(data)

# --- Main Execution ---
def create_files():
    print("Generating data...")
    
    # 1. Create Students
    df_students = generate_students()
    df_students.to_csv('students.csv', index=False)
    print(f"Created students.csv with {len(df_students)} records.")

    # 2. Create Marks (linked to students)
    df_marks = generate_marks(df_students)
    df_marks.to_csv('marks.csv', index=False)
    print("Created marks.csv")

    # 3. Create Fees
    df_fees = generate_fees(df_students)
    df_fees.to_csv('fees.csv', index=False)
    print("Created fees.csv")

    # 4. Create Attendance
    df_attendance = generate_attendance(df_students)
    df_attendance.to_csv('attendance.csv', index=False)
    print("Created attendance.csv")
    
    # 5. Create Teachers
    df_teachers = generate_teachers()
    df_teachers.to_csv('teachers.csv', index=False)
    print("Created teachers.csv")
    
    print("\nData generation complete! You can now run main_project.py")

if __name__ == "__main__":
    create_files()