import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime

# SECTION 1: DATABASE CONNECTION
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Debajani@20",
    "database": "hospital_management",
    "port": 3306
}
CURRENT_ADMIN = {"username": None, "full_name": None}

def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection failed: {e}")
        return None
def hash_password(plain_password):

    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()

def log_history(action, entity_name, details):
    connection = get_connection()
    if connection is None:
        return
    try:
        cursor = connection.cursor()
        query = """INSERT INTO history_log (admin_username, action, entity_name, details)
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (CURRENT_ADMIN.get("username"), action, entity_name, details))
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"History log failed: {e}")
    finally:
        connection.close()

def get_all_history(limit=200):
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute(
            """SELECT log_id, admin_username, action, entity_name, details, log_time
               FROM history_log ORDER BY log_time DESC LIMIT %s""",
            (limit,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching history failed: {e}")
        return []
    finally:
        connection.close()

# SECTION 2: ADMIN LOGIN (backend)
def check_login(username, password):
    connection = get_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM admin WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return None
        stored_password = result.get("password", "")
        hashed_input = hash_password(password)

        # Backward-compatible: old plain-text rows still match directly.
        if stored_password == hashed_input or stored_password == password:
            return result
        return None
    except Error as e:
        print(f"Login check failed: {e}")
        return None
    finally:
        connection.close()

# SECTION 3: PATIENT CRUD (backend)
def add_patient(name, dob, gender, phone, blood_group, address):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO patient (patient_name, dob, gender, phone, blood_group, address)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (name, dob, gender, phone, blood_group, address))
        connection.commit()
        cursor.close()
        log_history("ADD", "Patient", f"Added patient '{name}'")
        return True
    except Error as e:
        connection.rollback()
        print(f"Add patient failed: {e}")
        return False
    finally:
        connection.close()

def get_all_patients():
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM patient")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching patients failed: {e}")
        return []
    finally:
        connection.close()

def update_patient(patient_id, name, dob, gender, phone, blood_group, address):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE patient
                   SET patient_name = %s, dob = %s, gender = %s,
                       phone = %s, blood_group = %s, address = %s
                   WHERE patient_id = %s"""
        cursor.execute(query, (name, dob, gender, phone, blood_group, address, patient_id))
        connection.commit()
        cursor.close()
        log_history("UPDATE", "Patient", f"Updated patient #{patient_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Update patient failed: {e}")
        return False
    finally:
        connection.close()

def delete_patient(patient_id):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))
        connection.commit()
        cursor.close()
        log_history("DELETE", "Patient", f"Deleted patient #{patient_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Delete patient failed: {e}")
        messagebox.showerror(
            "Delete failed",
            "Could not delete this patient. They may still have appointments, "
            "admissions, or bills linked to them."
        )
        return False
    finally:
        connection.close()

# SECTION 3.5: DEPARTMENT CRUD (backend)
def add_department(dept_name, location, contact_number):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO department (dept_name, location, contact_number)
                   VALUES (%s, %s, %s)"""
        cursor.execute(query, (dept_name, location, contact_number))
        connection.commit()
        cursor.close()
        log_history("ADD", "Department", f"Added department '{dept_name}'")
        return True
    except Error as e:
        connection.rollback()
        print(f"Add department failed: {e}")
        return False
    finally:
        connection.close()

def get_all_departments():
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM department")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching departments failed: {e}")
        return []
    finally:
        connection.close()

def update_department(department_id, dept_name, location, contact_number):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE department
                   SET dept_name = %s, location = %s, contact_number = %s
                   WHERE department_id = %s"""
        cursor.execute(query, (dept_name, location, contact_number, department_id))
        connection.commit()
        cursor.close()
        log_history("UPDATE", "Department", f"Updated department #{department_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Update department failed: {e}")
        return False
    finally:
        connection.close()

def delete_department(department_id):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM department WHERE department_id = %s", (department_id,))
        connection.commit()
        cursor.close()
        log_history("DELETE", "Department", f"Deleted department #{department_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Delete department failed: {e}")
        messagebox.showerror(
            "Delete failed",
            "Could not delete this department. Doctors may still be linked to it."
        )
        return False
    finally:
        connection.close()

# SECTION 3.6: DOCTOR CRUD (backend)
def add_doctor(doctor_name, specialization, phone, department_id, consultation_fee):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO doctor (doctor_name, specialization, phone, department_id, consultation_fee)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (doctor_name, specialization, phone, department_id, consultation_fee))
        connection.commit()
        cursor.close()
        log_history("ADD", "Doctor", f"Added doctor '{doctor_name}'")
        return True
    except Error as e:
        connection.rollback()
        print(f"Add doctor failed: {e}")
        return False
    finally:
        connection.close()

def get_all_doctors():
    """Returns doctor rows joined with department name for easier reading."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = """SELECT d.doctor_id, d.doctor_name, d.specialization, d.phone,
                          dep.dept_name, d.consultation_fee, d.department_id
                   FROM doctor d
                   LEFT JOIN department dep ON d.department_id = dep.department_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching doctors failed: {e}")
        return []
    finally:
        connection.close()

def update_doctor(doctor_id, doctor_name, specialization, phone, department_id, consultation_fee):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE doctor
                   SET doctor_name = %s, specialization = %s, phone = %s,
                       department_id = %s, consultation_fee = %s
                   WHERE doctor_id = %s"""
        cursor.execute(query, (doctor_name, specialization, phone, department_id, consultation_fee, doctor_id))
        connection.commit()
        cursor.close()
        log_history("UPDATE", "Doctor", f"Updated doctor #{doctor_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Update doctor failed: {e}")
        return False
    finally:
        connection.close()

def delete_doctor(doctor_id):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM doctor WHERE doctor_id = %s", (doctor_id,))
        connection.commit()
        cursor.close()
        log_history("DELETE", "Doctor", f"Deleted doctor #{doctor_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Delete doctor failed: {e}")
        messagebox.showerror(
            "Delete failed",
            "Could not delete this doctor. They may still have appointments or admissions linked."
        )
        return False
    finally:
        connection.close()

def get_department_pairs():
    """Returns list of (department_id, dept_name) - used to fill the dropdown in Doctor tab."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT department_id, dept_name FROM department")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching department pairs failed: {e}")
        return []
    finally:
        connection.close()
# SECTION 3.7: BED CRUD (backend)
def add_bed(room_no, ward_type, status, charge_per_day):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO bed (room_no, ward_type, status, charge_per_day)
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (room_no, ward_type, status, charge_per_day))
        connection.commit()
        cursor.close()
        log_history("ADD", "Bed", f"Added bed room '{room_no}'")
        return True
    except Error as e:
        connection.rollback()
        print(f"Add bed failed: {e}")
        return False
    finally:
        connection.close()

def get_all_beds():
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bed")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching beds failed: {e}")
        return []
    finally:
        connection.close()

def update_bed(bed_id, room_no, ward_type, status, charge_per_day):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE bed SET room_no = %s, ward_type = %s, status = %s, charge_per_day = %s
                   WHERE bed_id = %s"""
        cursor.execute(query, (room_no, ward_type, status, charge_per_day, bed_id))
        connection.commit()
        cursor.close()
        log_history("UPDATE", "Bed", f"Updated bed #{bed_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Update bed failed: {e}")
        return False
    finally:
        connection.close()

def set_bed_status(bed_id, status):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE bed SET status = %s WHERE bed_id = %s", (status, bed_id))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        connection.rollback()
        print(f"Bed status update failed: {e}")
        return False
    finally:
        connection.close()

def delete_bed(bed_id):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM bed WHERE bed_id = %s", (bed_id,))
        connection.commit()
        cursor.close()
        log_history("DELETE", "Bed", f"Deleted bed #{bed_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Delete bed failed: {e}")
        messagebox.showerror(
            "Delete failed",
            "Could not delete this bed. It may still be linked to an admission record."
        )
        return False
    finally:
        connection.close()

# SECTION 3.8: APPOINTMENT CRUD (backend) - LINK ENTITY
# Connects patient <--> doctor (many-to-many)
def get_patient_pairs():
    """Returns [(patient_id, patient_name), ...] - dropdown fill korar jonno."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT patient_id, patient_name FROM patient")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching patient pairs failed: {e}")
        return []
    finally:
        connection.close()

def get_doctor_pairs():
    """Returns [(doctor_id, doctor_name), ...] - dropdown fill korar jonno."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT doctor_id, doctor_name FROM doctor")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching doctor pairs failed: {e}")
        return []
    finally:
        connection.close()

def is_doctor_slot_taken(doctor_id, appointment_date, appointment_time, exclude_appointment_id=None):
    """Check kore ei doctor er already ei date+time e onno kono (Scheduled) appointment ache kina.
    Double-booking thekano jonno - add/update er age eita call hobe."""
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """SELECT appointment_id FROM appointment
                   WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
                   AND status != 'Cancelled'"""
        params = [doctor_id, appointment_date, appointment_time]
        if exclude_appointment_id is not None:
            query += " AND appointment_id != %s"
            params.append(exclude_appointment_id)
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Error as e:
        print(f"Slot check failed: {e}")
        return False
    finally:
        connection.close()

def add_appointment(patient_id, doctor_id, appointment_date, appointment_time, status):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO appointment (patient_id, doctor_id, appointment_date, appointment_time, status)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (patient_id, doctor_id, appointment_date, appointment_time, status))
        connection.commit()
        cursor.close()
        log_history("ADD", "Appointment", f"Booked appointment for patient #{patient_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Add appointment failed: {e}")
        return False
    finally:
        connection.close()

def get_all_appointments():
    """Joined with patient + doctor name for easier reading in the table."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = """SELECT a.appointment_id, p.patient_name, doc.doctor_name,
                          a.appointment_date, a.appointment_time, a.status,
                          a.patient_id, a.doctor_id
                   FROM appointment a
                   LEFT JOIN patient p ON a.patient_id = p.patient_id
                   LEFT JOIN doctor doc ON a.doctor_id = doc.doctor_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching appointments failed: {e}")
        return []
    finally:
        connection.close()

def update_appointment(appointment_id, patient_id, doctor_id, appointment_date, appointment_time, status):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE appointment
                   SET patient_id = %s, doctor_id = %s, appointment_date = %s,
                       appointment_time = %s, status = %s
                   WHERE appointment_id = %s"""
        cursor.execute(query, (patient_id, doctor_id, appointment_date, appointment_time, status, appointment_id))
        connection.commit()
        cursor.close()
        log_history("UPDATE", "Appointment", f"Updated appointment #{appointment_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Update appointment failed: {e}")
        return False
    finally:
        connection.close()

def delete_appointment(appointment_id):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM appointment WHERE appointment_id = %s", (appointment_id,))
        connection.commit()
        cursor.close()
        log_history("DELETE", "Appointment", f"Deleted appointment #{appointment_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Delete appointment failed: {e}")
        messagebox.showerror(
            "Delete failed",
            "Could not delete this appointment. A prescription may still be linked to it."
        )
        return False
    finally:
        connection.close()

# SECTION 3.9: ADMISSION CRUD (backend) - LINK ENTITY
# Connects patient <--> doctor <--> bed
def get_bed_pairs():
    """Returns [(bed_id, room_no), ...] - dropdown fill korar jonno."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT bed_id, room_no FROM bed")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching bed pairs failed: {e}")
        return []
    finally:
        connection.close()

def get_available_bed_pairs():
    """Only beds that are currently Available - admission form e eita use hobe."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT bed_id, room_no FROM bed WHERE status = 'Available'")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching available beds failed: {e}")
        return []
    finally:
        connection.close()

def add_admission(patient_id, doctor_id, bed_id, admission_date, discharge_date, diagnosis):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO admission (patient_id, doctor_id, bed_id, admission_date, discharge_date, diagnosis)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (patient_id, doctor_id, bed_id, admission_date,
                                discharge_date if discharge_date else None, diagnosis))
        connection.commit()
        cursor.close()
        log_history("ADD", "Admission", f"Admitted patient #{patient_id} to bed #{bed_id}")
        # Bed ekhon occupied - jodi already discharge_date deya na thake
        if not discharge_date:
            set_bed_status(bed_id, "Occupied")
        return True
    except Error as e:
        connection.rollback()
        print(f"Add admission failed: {e}")
        return False
    finally:
        connection.close()

def get_all_admissions():
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = """SELECT ad.admission_id, p.patient_name, doc.doctor_name, b.room_no,
                          ad.admission_date, ad.discharge_date, ad.diagnosis,
                          ad.patient_id, ad.doctor_id, ad.bed_id
                   FROM admission ad
                   LEFT JOIN patient p ON ad.patient_id = p.patient_id
                   LEFT JOIN doctor doc ON ad.doctor_id = doc.doctor_id
                   LEFT JOIN bed b ON ad.bed_id = b.bed_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching admissions failed: {e}")
        return []
    finally:
        connection.close()

def update_admission(admission_id, patient_id, doctor_id, bed_id, admission_date, discharge_date, diagnosis,
                      old_bed_id=None):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE admission
                   SET patient_id = %s, doctor_id = %s, bed_id = %s,
                       admission_date = %s, discharge_date = %s, diagnosis = %s
                   WHERE admission_id = %s"""
        cursor.execute(query, (patient_id, doctor_id, bed_id, admission_date,
                                discharge_date if discharge_date else None, diagnosis, admission_id))
        connection.commit()
        cursor.close()
        log_history("UPDATE", "Admission", f"Updated admission #{admission_id}")

        # Bed status auto-sync: discharge dile bed free hoye jabe,
        # bed change hole purono bed o free hobe, notun bed occupied hobe.
        if discharge_date:
            set_bed_status(bed_id, "Available")
        else:
            set_bed_status(bed_id, "Occupied")
        if old_bed_id and old_bed_id != bed_id:
            set_bed_status(old_bed_id, "Available")
        return True
    except Error as e:
        connection.rollback()
        print(f"Update admission failed: {e}")
        return False
    finally:
        connection.close()

def delete_admission(admission_id, bed_id=None):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM admission WHERE admission_id = %s", (admission_id,))
        connection.commit()
        cursor.close()
        log_history("DELETE", "Admission", f"Deleted admission #{admission_id}")
        if bed_id:
            set_bed_status(bed_id, "Available")
        return True
    except Error as e:
        connection.rollback()
        print(f"Delete admission failed: {e}")
        messagebox.showerror(
            "Delete failed",
            "Could not delete this admission. A bill may still be linked to it."
        )
        return False
    finally:
        connection.close()

# SECTION 3.10: PRESCRIPTION CRUD (backend) - LINK ENTITY
# Connects appointment <--> doctor
def get_appointment_pairs():
    """Returns [(appointment_id, display_text), ...] - dropdown fill korar jonno."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = """SELECT a.appointment_id, p.patient_name, a.appointment_date
                   FROM appointment a
                   LEFT JOIN patient p ON a.patient_id = p.patient_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [(r[0], f"#{r[0]} - {r[1]} ({r[2]})") for r in rows]
    except Error as e:
        print(f"Fetching appointment pairs failed: {e}")
        return []
    finally:
        connection.close()

def add_prescription(appointment_id, doctor_id, prescription_date, medicine_details, notes):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO prescription (appointment_id, doctor_id, prescription_date, medicine_details, notes)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (appointment_id, doctor_id, prescription_date, medicine_details, notes))
        connection.commit()
        cursor.close()
        log_history("ADD", "Prescription", f"Added prescription for appointment #{appointment_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Add prescription failed: {e}")
        return False
    finally:
        connection.close()

def get_all_prescriptions():
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = """SELECT pr.prescription_id, p.patient_name, doc.doctor_name,
                          pr.prescription_date, pr.medicine_details, pr.notes,
                          pr.appointment_id, pr.doctor_id
                   FROM prescription pr
                   LEFT JOIN appointment a ON pr.appointment_id = a.appointment_id
                   LEFT JOIN patient p ON a.patient_id = p.patient_id
                   LEFT JOIN doctor doc ON pr.doctor_id = doc.doctor_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching prescriptions failed: {e}")
        return []
    finally:
        connection.close()

def update_prescription(prescription_id, appointment_id, doctor_id, prescription_date, medicine_details, notes):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE prescription
                   SET appointment_id = %s, doctor_id = %s, prescription_date = %s,
                       medicine_details = %s, notes = %s
                   WHERE prescription_id = %s"""
        cursor.execute(query, (appointment_id, doctor_id, prescription_date, medicine_details, notes, prescription_id))
        connection.commit()
        cursor.close()
        log_history("UPDATE", "Prescription", f"Updated prescription #{prescription_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Update prescription failed: {e}")
        return False
    finally:
        connection.close()

def delete_prescription(prescription_id):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM prescription WHERE prescription_id = %s", (prescription_id,))
        connection.commit()
        cursor.close()
        log_history("DELETE", "Prescription", f"Deleted prescription #{prescription_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Delete prescription failed: {e}")
        return False
    finally:
        connection.close()

# SECTION 3.11: BILLING CRUD (backend) - LINK ENTITY
# Connects patient <--> admission
def get_admission_pairs():
    """Returns [(admission_id, display_text), ...] - dropdown fill korar jonno."""
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = """SELECT ad.admission_id, p.patient_name, ad.admission_date
                   FROM admission ad
                   LEFT JOIN patient p ON ad.patient_id = p.patient_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [(r[0], f"#{r[0]} - {r[1]} ({r[2]})") for r in rows]
    except Error as e:
        print(f"Fetching admission pairs failed: {e}")
        return []
    finally:
        connection.close()

def add_billing(patient_id, admission_id, total_amount, payment_status, payment_method):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO billing (patient_id, admission_id, total_amount, payment_status, payment_method)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (patient_id, admission_id, total_amount, payment_status, payment_method))
        connection.commit()
        cursor.close()
        log_history("ADD", "Billing", f"Created bill for patient #{patient_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Add billing failed: {e}")
        return False
    finally:
        connection.close()

def get_all_billings():
    connection = get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = """SELECT b.bill_id, p.patient_name, b.admission_id, b.total_amount,
                          b.bill_date, b.payment_status, b.payment_method, b.patient_id
                   FROM billing b
                   LEFT JOIN patient p ON b.patient_id = p.patient_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as e:
        print(f"Fetching billings failed: {e}")
        return []
    finally:
        connection.close()

def update_billing(bill_id, patient_id, admission_id, total_amount, payment_status, payment_method):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE billing
                   SET patient_id = %s, admission_id = %s, total_amount = %s,
                       payment_status = %s, payment_method = %s
                   WHERE bill_id = %s"""
        cursor.execute(query, (patient_id, admission_id, total_amount, payment_status, payment_method, bill_id))
        connection.commit()
        cursor.close()
        log_history("UPDATE", "Billing", f"Updated bill #{bill_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Update billing failed: {e}")
        return False
    finally:
        connection.close()

def delete_billing(bill_id):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM billing WHERE bill_id = %s", (bill_id,))
        connection.commit()
        cursor.close()
        log_history("DELETE", "Billing", f"Deleted bill #{bill_id}")
        return True
    except Error as e:
        connection.rollback()
        print(f"Delete billing failed: {e}")
        return False
    finally:
        connection.close()

# SECTION 3.12: SUMMARY STATS (backend)
def get_summary_stats():
    """Prottek entity theke count/sum ber kore ekta dictionary e return kore."""
    connection = get_connection()
    if connection is None:
        return {}
    try:
        cursor = connection.cursor()
        stats = {}

        cursor.execute("SELECT COUNT(*) FROM patient")
        stats["total_patients"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM doctor")
        stats["total_doctors"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM department")
        stats["total_departments"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bed WHERE status = 'Available'")
        stats["available_beds"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM appointment WHERE appointment_date = CURDATE()")
        stats["today_appointments"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM admission WHERE discharge_date IS NULL")
        stats["current_admissions"] = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM billing WHERE payment_status = 'Unpaid'")
        stats["unpaid_amount"] = cursor.fetchone()[0]

        cursor.close()
        return stats
    except Error as e:
        print(f"Fetching stats failed: {e}")
        return {}
    finally:
        connection.close()

# SECTION 3.13: VALIDATION HELPERS (backend)
def is_valid_date(text):
    """YYYY-MM-DD format check kore."""
    if not text:
        return True  # optional field hole empty allow
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_valid_time(text):
    """HH:MM:SS or HH:MM format check kore."""
    if not text:
        return False
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            datetime.strptime(text, fmt)
            return True
        except ValueError:
            continue
    return False

def is_valid_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

# SECTION 4: LOGIN WINDOW (GUI)
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System - Login")
        self.root.geometry("380x300")
        self.root.resizable(False, False)
        self.root.configure(bg="#3B4B63")

        card = tk.Frame(root, bg="white", padx=30, pady=25)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="🏥", font=("Segoe UI", 28), bg="white").pack()
        tk.Label(card, text="Hospital Management System",
                 font=("Segoe UI", 12, "bold"), bg="white", fg="#3B4B63").pack(pady=(0, 15))

        tk.Label(card, text="Username", bg="white", font=("Segoe UI", 9),
                 anchor="w").pack(fill="x")
        self.username_entry = tk.Entry(card, width=28, font=("Segoe UI", 10),
                                        relief="solid", bd=1)
        self.username_entry.pack(pady=(2, 10), ipady=4)

        tk.Label(card, text="Password", bg="white", font=("Segoe UI", 9),
                 anchor="w").pack(fill="x")
        self.password_entry = tk.Entry(card, width=28, show="*", font=("Segoe UI", 10),
                                        relief="solid", bd=1)
        self.password_entry.pack(pady=(2, 15), ipady=4)
        self.password_entry.bind("<Return>", lambda event: self.handle_login())

        tk.Button(card, text="Login", width=20, command=self.handle_login,
                  bg="#0E7C9D", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", pady=6).pack()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing info", "Please enter both username and password.")
            return

        admin = check_login(username, password)

        if admin:
            CURRENT_ADMIN["username"] = admin["username"]
            CURRENT_ADMIN["full_name"] = admin.get("full_name", admin["username"])
            log_history("LOGIN", "Admin", f"'{admin['username']}' logged in")
            messagebox.showinfo("Success", f"Welcome, {admin['full_name']}!")
            self.root.destroy()
            root2 = tk.Tk()
            Dashboard(root2)
            root2.mainloop()
        else:
            messagebox.showerror("Login failed", "Incorrect username or password.")
# SECTION 5: DASHBOARD (GUI)
# UI THEME - প্রতিটা entity এর জন্য আলাদা accent color
ENTITY_THEME = {
    "Patient":      {"icon": "🧑‍🤝‍🧑", "color": "#0E7C9D"},
    "Department":   {"icon": "🏥", "color": "#6C4FB6"},
    "Doctor":       {"icon": "🩺", "color": "#1D6FA5"},
    "Bed":          {"icon": "🛏️", "color": "#C67C1E"},
    "Appointment":  {"icon": "📅", "color": "#2E9E5B"},
    "Admission":    {"icon": "🏨", "color": "#C0392B"},
    "Prescription": {"icon": "💊", "color": "#B23A78"},
    "Billing":      {"icon": "💳", "color": "#3E4C82"},
    "History":      {"icon": "🕒", "color": "#555555"},
}
class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System - Dashboard")
        self.root.geometry("1200x680")
        self.root.minsize(1150, 600)
        self.root.configure(bg="#F2F4F7")

        self.setup_style()

        # ---- Top bar: welcome text + logout ----
        topbar = tk.Frame(root, bg="#3B4B63", height=40)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)
        welcome_text = f"Logged in as: {CURRENT_ADMIN.get('full_name') or 'Admin'}"
        tk.Label(topbar, text=welcome_text, bg="#3B4B63", fg="white",
                 font=("Segoe UI", 10)).pack(side="left", padx=12)
        tk.Button(topbar, text="Logout", command=self.handle_logout,
                  bg="#E24B4A", fg="white", relief="flat", padx=10,
                  cursor="hand2").pack(side="right", padx=12, pady=5)

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)
        self.notebook = notebook
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Safety net: if there are ever too many tabs to fit the window width,
        # scrolling the mouse wheel over the tab bar switches tabs - this way
        # a tab is never permanently stuck off-screen with no way to reach it.
        def scroll_tabs(event):
            direction = -1 if event.delta > 0 else 1
            try:
                current = notebook.index(notebook.select())
                total = notebook.index("end")
                new_index = (current + direction) % total
                notebook.select(new_index)
            except tk.TclError:
                pass
        notebook.bind("<MouseWheel>", scroll_tabs)      # Windows / macOS
        notebook.bind("<Button-4>", lambda e: scroll_tabs(type("E", (), {"delta": 120})()))  # Linux scroll up
        notebook.bind("<Button-5>", lambda e: scroll_tabs(type("E", (), {"delta": -120})()))  # Linux scroll down

        # ---- Home tab (summary dashboard) ----
        self.home_tab = ttk.Frame(notebook)
        notebook.add(self.home_tab, text=" 🏠 Home ")
        self.build_home_tab()

        # ---- Patient tab ----
        self.patient_tab = ttk.Frame(notebook)
        notebook.add(self.patient_tab, text=" Patient ")
        self.build_patient_tab()

        # ---- Department tab ----
        self.department_tab = ttk.Frame(notebook)
        notebook.add(self.department_tab, text=" Department ")
        self.build_department_tab()

        # ---- Doctor tab ----
        self.doctor_tab = ttk.Frame(notebook)
        notebook.add(self.doctor_tab, text=" Doctor ")
        self.build_doctor_tab()

        # ---- Bed tab ----
        self.bed_tab = ttk.Frame(notebook)
        notebook.add(self.bed_tab, text=" Bed ")
        self.build_bed_tab()

        # ---- Appointment tab (link entity) ----
        self.appointment_tab = ttk.Frame(notebook)
        notebook.add(self.appointment_tab, text=" Appointment ")
        self.build_appointment_tab()

        # ---- Admission tab (link entity - patient/doctor/bed) ----
        self.admission_tab = ttk.Frame(notebook)
        notebook.add(self.admission_tab, text=" Admission ")
        self.build_admission_tab()

        # ---- Prescription tab (link entity - appointment/doctor) ----
        self.prescription_tab = ttk.Frame(notebook)
        notebook.add(self.prescription_tab, text=" Prescription ")
        self.build_prescription_tab()

        # ---- Billing tab (link entity - patient/admission) ----
        self.billing_tab = ttk.Frame(notebook)
        notebook.add(self.billing_tab, text=" Billing ")
        self.build_billing_tab()

        # ---- History tab ----
        self.history_tab = ttk.Frame(notebook)
        notebook.add(self.history_tab, text=" 🕒 History ")
        self.build_history_tab()

    def handle_logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            log_history("LOGOUT", "Admin", f"'{CURRENT_ADMIN.get('username')}' logged out")
            CURRENT_ADMIN["username"] = None
            CURRENT_ADMIN["full_name"] = None
            self.root.destroy()
            root2 = tk.Tk()
            LoginWindow(root2)
            root2.mainloop()

    def on_tab_changed(self, event):
        """Home tab e switch korle stats auto-refresh hoye jabe."""
        selected = event.widget.select()
        tab_text = event.widget.tab(selected, "text")
        if "Home" in tab_text:
            self.load_home_stats()
        elif "History" in tab_text:
            self.load_history()
    # Theme / style setup - shob tab ei ekbar apply hobe
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#F2F4F7", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"),
                         padding=[7, 6], background="#DCE3EA")
        style.map("TNotebook.Tab",
                   background=[("selected", "#3B4B63")],
                   foreground=[("selected", "white")])

        style.configure("TFrame", background="#FFFFFF")

        style.configure("Treeview", font=("Segoe UI", 9), rowheight=26,
                         background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                         background="#E8ECF1")
        style.map("Treeview", background=[("selected", "#B7D3E8")])

    def add_header(self, frame, entity_name):
        """Prottek tab er upore ekta colored banner - entity ke alada dekhanor jonno."""
        info = ENTITY_THEME.get(entity_name, {"icon": "📋", "color": "#333333"})
        header = tk.Frame(frame, bg=info["color"], height=42)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text=f"  {info['icon']}  {entity_name} Management",
                 bg=info["color"], fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left", pady=6)

    # HOME TAB - summary dashboard (count cards)
    def build_home_tab(self):
        frame = self.home_tab
        self.add_header(frame, "Home")

        top = tk.Frame(frame, bg="white")
        top.pack(fill="x", padx=15, pady=10)
        tk.Label(top, text="Overview", font=("Segoe UI", 12, "bold"), bg="white").pack(side="left")
        tk.Button(top, text="Refresh", command=self.load_home_stats,
                  bg="#0E7C9D", fg="white", relief="flat", padx=10).pack(side="right")

        self.home_cards_frame = tk.Frame(frame, bg="white")
        self.home_cards_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.load_home_stats()

    def load_home_stats(self):
        for widget in self.home_cards_frame.winfo_children():
            widget.destroy()
        stats = get_summary_stats()

        cards = [
            ("🧑‍🤝‍🧑", "Total Patients", stats.get("total_patients", 0), "#0E7C9D"),
            ("🩺", "Total Doctors", stats.get("total_doctors", 0), "#1D6FA5"),
            ("🏥", "Departments", stats.get("total_departments", 0), "#6C4FB6"),
            ("🛏️", "Available Beds", stats.get("available_beds", 0), "#C67C1E"),
            ("📅", "Today's Appointments", stats.get("today_appointments", 0), "#2E9E5B"),
            ("🏨", "Current Admissions", stats.get("current_admissions", 0), "#C0392B"),
            ("💳", "Unpaid Amount", f"৳{stats.get('unpaid_amount', 0)}", "#3E4C82"),
        ]

        columns = 4
        for index, (icon, label, value, color) in enumerate(cards):
            row = index // columns
            col = index % columns

            card = tk.Frame(self.home_cards_frame, bg=color, width=180, height=100)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)

            tk.Label(card, text=icon, font=("Segoe UI", 18), bg=color, fg="white").pack(pady=(10, 0))
            tk.Label(card, text=str(value), font=("Segoe UI", 16, "bold"),
                     bg=color, fg="white").pack()
            tk.Label(card, text=label, font=("Segoe UI", 9), bg=color, fg="white").pack()

        for c in range(columns):
            self.home_cards_frame.grid_columnconfigure(c, weight=1)

    # HISTORY TAB - shows audit log of every CRUD action
    def build_history_tab(self):
        frame = self.history_tab
        self.add_header(frame, "History")

        top = tk.Frame(frame, bg="white")
        top.pack(fill="x", padx=10, pady=8)
        tk.Label(top, text="Recent activity (latest 200 actions)",
                 font=("Segoe UI", 10, "bold"), bg="white").pack(side="left")
        tk.Button(top, text="Refresh", command=self.load_history,
                  bg="#0E7C9D", fg="white", relief="flat", padx=10).pack(side="right")

        columns = ("log_id", "admin_username", "action", "entity_name", "details", "log_time")
        self.history_table = ttk.Treeview(frame, columns=columns, show="headings", height=18)
        widths = {"log_id": 60, "admin_username": 100, "action": 80,
                  "entity_name": 110, "details": 320, "log_time": 150}
        for col in columns:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, width=widths.get(col, 100))
        self.history_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_history()

    def load_history(self):
        for row in self.history_table.get_children():
            self.history_table.delete(row)
        for record in get_all_history():
            self.history_table.insert("", "end", values=record)

    # ---- Patient tab UI + logic ----
    def build_patient_tab(self):
        frame = self.patient_tab
        self.add_header(frame, "Patient")

        form = tk.Frame(frame)
        form.pack(pady=10)

        labels = ["Name", "DOB (YYYY-MM-DD)", "Gender", "Phone", "Blood Group", "Address"]
        self.patient_entries = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=3)
            entry = tk.Entry(form, width=30)
            entry.grid(row=i, column=1, padx=5, pady=3)
            self.patient_entries[label] = entry

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", width=10, bg="#3B8BD4", fg="white",
                  command=self.handle_add_patient).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, bg="#EF9F27", fg="white",
                  command=self.handle_update_patient).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, bg="#E24B4A", fg="white",
                  command=self.handle_delete_patient).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10,
                  command=self.clear_patient_fields).grid(row=0, column=3, padx=5)

        search_frame = tk.Frame(frame)
        search_frame.pack(pady=(0, 5))
        tk.Label(search_frame, text="Search (name/phone):").pack(side="left", padx=5)
        self.patient_search_entry = tk.Entry(search_frame, width=25)
        self.patient_search_entry.pack(side="left", padx=5)
        self.patient_search_entry.bind("<KeyRelease>", lambda e: self.load_patients())

        columns = ("patient_id", "patient_name", "dob", "gender", "phone", "blood_group", "address")
        self.patient_table = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.patient_table.heading(col, text=col)
            self.patient_table.column(col, width=100)
        self.patient_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.patient_table.bind("<<TreeviewSelect>>", self.on_row_select)

        self.load_patients()

    def load_patients(self):
        for row in self.patient_table.get_children():
            self.patient_table.delete(row)
        keyword = self.patient_search_entry.get().strip().lower() if hasattr(self, "patient_search_entry") else ""
        for record in get_all_patients():
            if keyword:
                name = str(record[1]).lower() if len(record) > 1 else ""
                phone = str(record[4]).lower() if len(record) > 4 else ""
                if keyword not in name and keyword not in phone:
                    continue
            self.patient_table.insert("", "end", values=record)

    def on_row_select(self, event):
        selected = self.patient_table.selection()
        if not selected:
            return
        values = self.patient_table.item(selected[0])["values"]
        self.selected_patient_id = values[0]

        self.patient_entries["Name"].delete(0, tk.END)
        self.patient_entries["Name"].insert(0, values[1])
        self.patient_entries["DOB (YYYY-MM-DD)"].delete(0, tk.END)
        self.patient_entries["DOB (YYYY-MM-DD)"].insert(0, values[2])
        self.patient_entries["Gender"].delete(0, tk.END)
        self.patient_entries["Gender"].insert(0, values[3])
        self.patient_entries["Phone"].delete(0, tk.END)
        self.patient_entries["Phone"].insert(0, values[4])
        self.patient_entries["Blood Group"].delete(0, tk.END)
        self.patient_entries["Blood Group"].insert(0, values[5])
        self.patient_entries["Address"].delete(0, tk.END)
        self.patient_entries["Address"].insert(0, values[6])

    def get_form_values(self):
        return (
            self.patient_entries["Name"].get().strip(),
            self.patient_entries["DOB (YYYY-MM-DD)"].get().strip(),
            self.patient_entries["Gender"].get().strip(),
            self.patient_entries["Phone"].get().strip(),
            self.patient_entries["Blood Group"].get().strip(),
            self.patient_entries["Address"].get().strip(),
        )
    def handle_add_patient(self):
        name, dob, gender, phone, blood_group, address = self.get_form_values()
        if not name:
            messagebox.showwarning("Missing info", "Patient name is required.")
            return
        if dob and not is_valid_date(dob):
            messagebox.showwarning("Invalid date", "DOB must be in YYYY-MM-DD format.")
            return
        if add_patient(name, dob, gender, phone, blood_group, address):
            messagebox.showinfo("Success", "Patient added successfully.")
            self.clear_patient_fields()
            self.load_patients()

    def handle_update_patient(self):
        if not hasattr(self, "selected_patient_id"):
            messagebox.showwarning("No selection", "Please select a patient from the table first.")
            return
        name, dob, gender, phone, blood_group, address = self.get_form_values()
        if not name:
            messagebox.showwarning("Missing info", "Patient name is required.")
            return
        if dob and not is_valid_date(dob):
            messagebox.showwarning("Invalid date", "DOB must be in YYYY-MM-DD format.")
            return
        if update_patient(self.selected_patient_id, name, dob, gender, phone, blood_group, address):
            messagebox.showinfo("Success", "Patient updated successfully.")
            self.clear_patient_fields()
            self.load_patients()

    def handle_delete_patient(self):
        if not hasattr(self, "selected_patient_id"):
            messagebox.showwarning("No selection", "Please select a patient from the table first.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            if delete_patient(self.selected_patient_id):
                messagebox.showinfo("Deleted", "Patient deleted successfully.")
                self.clear_patient_fields()
                self.load_patients()

    def clear_patient_fields(self):
        for entry in self.patient_entries.values():
            entry.delete(0, tk.END)
        if hasattr(self, "selected_patient_id"):
            del self.selected_patient_id

    # DEPARTMENT TAB - full CRUD
    def build_department_tab(self):
        frame = self.department_tab
        self.add_header(frame, "Department")

        form = tk.Frame(frame)
        form.pack(pady=10)

        labels = ["Dept Name", "Location", "Contact Number"]
        self.department_entries = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=3)
            entry = tk.Entry(form, width=30)
            entry.grid(row=i, column=1, padx=5, pady=3)
            self.department_entries[label] = entry

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", width=10, bg="#3B8BD4", fg="white",
                  command=self.handle_add_department).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, bg="#EF9F27", fg="white",
                  command=self.handle_update_department).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, bg="#E24B4A", fg="white",
                  command=self.handle_delete_department).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10,
                  command=self.clear_department_fields).grid(row=0, column=3, padx=5)

        columns = ("department_id", "dept_name", "location", "contact_number")
        self.department_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.department_table.heading(col, text=col)
            self.department_table.column(col, width=130)
        self.department_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.department_table.bind("<<TreeviewSelect>>", self.on_department_row_select)

        self.load_departments()

    def load_departments(self):
        for row in self.department_table.get_children():
            self.department_table.delete(row)
        for record in get_all_departments():
            self.department_table.insert("", "end", values=record)

    def on_department_row_select(self, event):
        selected = self.department_table.selection()
        if not selected:
            return
        values = self.department_table.item(selected[0])["values"]
        self.selected_department_id = values[0]

        self.department_entries["Dept Name"].delete(0, tk.END)
        self.department_entries["Dept Name"].insert(0, values[1])
        self.department_entries["Location"].delete(0, tk.END)
        self.department_entries["Location"].insert(0, values[2])
        self.department_entries["Contact Number"].delete(0, tk.END)
        self.department_entries["Contact Number"].insert(0, values[3])

    def handle_add_department(self):
        name = self.department_entries["Dept Name"].get().strip()
        location = self.department_entries["Location"].get().strip()
        contact = self.department_entries["Contact Number"].get().strip()
        if not name:
            messagebox.showwarning("Missing info", "Department name is required.")
            return
        if add_department(name, location, contact):
            messagebox.showinfo("Success", "Department added successfully.")
            self.clear_department_fields()
            self.load_departments()
            self.refresh_department_dropdown()

    def handle_update_department(self):
        if not hasattr(self, "selected_department_id"):
            messagebox.showwarning("No selection", "Please select a department from the table first.")
            return
        name = self.department_entries["Dept Name"].get().strip()
        location = self.department_entries["Location"].get().strip()
        contact = self.department_entries["Contact Number"].get().strip()
        if not name:
            messagebox.showwarning("Missing info", "Department name is required.")
            return
        if update_department(self.selected_department_id, name, location, contact):
            messagebox.showinfo("Success", "Department updated successfully.")
            self.clear_department_fields()
            self.load_departments()
            self.refresh_department_dropdown()

    def handle_delete_department(self):
        if not hasattr(self, "selected_department_id"):
            messagebox.showwarning("No selection", "Please select a department from the table first.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            if delete_department(self.selected_department_id):
                messagebox.showinfo("Deleted", "Department deleted successfully.")
                self.clear_department_fields()
                self.load_departments()
                self.refresh_department_dropdown()

    def clear_department_fields(self):
        for entry in self.department_entries.values():
            entry.delete(0, tk.END)
        if hasattr(self, "selected_department_id"):
            del self.selected_department_id

    # DOCTOR TAB - full CRUD (department_id is a Foreign Key)
    def build_doctor_tab(self):
        frame = self.doctor_tab
        self.add_header(frame, "Doctor")

        form = tk.Frame(frame)
        form.pack(pady=10)

        tk.Label(form, text="Doctor Name:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.doctor_name_entry = tk.Entry(form, width=30)
        self.doctor_name_entry.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(form, text="Specialization:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.doctor_spec_entry = tk.Entry(form, width=30)
        self.doctor_spec_entry.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(form, text="Phone:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.doctor_phone_entry = tk.Entry(form, width=30)
        self.doctor_phone_entry.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(form, text="Department:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.doctor_dept_combo = ttk.Combobox(form, width=28, state="readonly")
        self.doctor_dept_combo.grid(row=3, column=1, padx=5, pady=3)

        tk.Label(form, text="Consultation Fee:").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        self.doctor_fee_entry = tk.Entry(form, width=30)
        self.doctor_fee_entry.grid(row=4, column=1, padx=5, pady=3)

        self.refresh_department_dropdown()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", width=10, bg="#3B8BD4", fg="white",
                  command=self.handle_add_doctor).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, bg="#EF9F27", fg="white",
                  command=self.handle_update_doctor).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, bg="#E24B4A", fg="white",
                  command=self.handle_delete_doctor).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10,
                  command=self.clear_doctor_fields).grid(row=0, column=3, padx=5)

        columns = ("doctor_id", "doctor_name", "specialization", "phone", "dept_name", "consultation_fee")
        self.doctor_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.doctor_table.heading(col, text=col)
            self.doctor_table.column(col, width=110)
        self.doctor_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.doctor_table.bind("<<TreeviewSelect>>", self.on_doctor_row_select)

        self.load_doctors()

    def refresh_department_dropdown(self):
        """Dept dropdown re-load kore - notun department add korle eita call hobe."""
        self.department_pairs = get_department_pairs()
        names = [name for (_id, name) in self.department_pairs]
        self.doctor_dept_combo["values"] = names

    def load_doctors(self):
        for row in self.doctor_table.get_children():
            self.doctor_table.delete(row)
        for record in get_all_doctors():
            self.doctor_table.insert("", "end", values=record[:6])

    def on_doctor_row_select(self, event):
        selected = self.doctor_table.selection()
        if not selected:
            return
        values = self.doctor_table.item(selected[0])["values"]
        self.selected_doctor_id = values[0]

        self.doctor_name_entry.delete(0, tk.END)
        self.doctor_name_entry.insert(0, values[1])
        self.doctor_spec_entry.delete(0, tk.END)
        self.doctor_spec_entry.insert(0, values[2])
        self.doctor_phone_entry.delete(0, tk.END)
        self.doctor_phone_entry.insert(0, values[3])
        self.doctor_dept_combo.set(values[4] if values[4] else "")
        self.doctor_fee_entry.delete(0, tk.END)
        self.doctor_fee_entry.insert(0, values[5])

    def get_selected_department_id(self):
        selected_name = self.doctor_dept_combo.get()
        for dept_id, name in self.department_pairs:
            if name == selected_name:
                return dept_id
        return None

    def handle_add_doctor(self):
        name = self.doctor_name_entry.get().strip()
        spec = self.doctor_spec_entry.get().strip()
        phone = self.doctor_phone_entry.get().strip()
        dept_id = self.get_selected_department_id()
        fee = self.doctor_fee_entry.get().strip() or "0"

        if not name:
            messagebox.showwarning("Missing info", "Doctor name is required.")
            return
        if dept_id is None:
            messagebox.showwarning("Missing info", "Please select a department.")
            return
        if not is_valid_number(fee):
            messagebox.showwarning("Invalid fee", "Consultation fee must be a number.")
            return

        if add_doctor(name, spec, phone, dept_id, fee):
            messagebox.showinfo("Success", "Doctor added successfully.")
            self.clear_doctor_fields()
            self.load_doctors()

    def handle_update_doctor(self):
        if not hasattr(self, "selected_doctor_id"):
            messagebox.showwarning("No selection", "Please select a doctor from the table first.")
            return
        name = self.doctor_name_entry.get().strip()
        spec = self.doctor_spec_entry.get().strip()
        phone = self.doctor_phone_entry.get().strip()
        dept_id = self.get_selected_department_id()
        fee = self.doctor_fee_entry.get().strip() or "0"

        if not name:
            messagebox.showwarning("Missing info", "Doctor name is required.")
            return
        if not is_valid_number(fee):
            messagebox.showwarning("Invalid fee", "Consultation fee must be a number.")
            return

        if update_doctor(self.selected_doctor_id, name, spec, phone, dept_id, fee):
            messagebox.showinfo("Success", "Doctor updated successfully.")
            self.clear_doctor_fields()
            self.load_doctors()

    def handle_delete_doctor(self):
        if not hasattr(self, "selected_doctor_id"):
            messagebox.showwarning("No selection", "Please select a doctor from the table first.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            if delete_doctor(self.selected_doctor_id):
                messagebox.showinfo("Deleted", "Doctor deleted successfully.")
                self.clear_doctor_fields()
                self.load_doctors()

    def clear_doctor_fields(self):
        self.doctor_name_entry.delete(0, tk.END)
        self.doctor_spec_entry.delete(0, tk.END)
        self.doctor_phone_entry.delete(0, tk.END)
        self.doctor_dept_combo.set("")
        self.doctor_fee_entry.delete(0, tk.END)
        if hasattr(self, "selected_doctor_id"):
            del self.selected_doctor_id

    # BED TAB - full CRUD
    def build_bed_tab(self):
        frame = self.bed_tab
        self.add_header(frame, "Bed")

        form = tk.Frame(frame)
        form.pack(pady=10)

        tk.Label(form, text="Room No:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.bed_room_entry = tk.Entry(form, width=30)
        self.bed_room_entry.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(form, text="Ward Type:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.bed_ward_entry = tk.Entry(form, width=30)
        self.bed_ward_entry.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(form, text="Status:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.bed_status_combo = ttk.Combobox(form, width=28, state="readonly",
                                              values=["Available", "Occupied", "Maintenance"])
        self.bed_status_combo.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(form, text="Charge Per Day:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.bed_charge_entry = tk.Entry(form, width=30)
        self.bed_charge_entry.grid(row=3, column=1, padx=5, pady=3)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", width=10, bg="#3B8BD4", fg="white",
                  command=self.handle_add_bed).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, bg="#EF9F27", fg="white",
                  command=self.handle_update_bed).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, bg="#E24B4A", fg="white",
                  command=self.handle_delete_bed).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10,
                  command=self.clear_bed_fields).grid(row=0, column=3, padx=5)

        columns = ("bed_id", "room_no", "ward_type", "status", "charge_per_day")
        self.bed_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.bed_table.heading(col, text=col)
            self.bed_table.column(col, width=120)
        self.bed_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.bed_table.bind("<<TreeviewSelect>>", self.on_bed_row_select)

        self.load_beds()

    def load_beds(self):
        for row in self.bed_table.get_children():
            self.bed_table.delete(row)
        for record in get_all_beds():
            self.bed_table.insert("", "end", values=record)

    def on_bed_row_select(self, event):
        selected = self.bed_table.selection()
        if not selected:
            return
        values = self.bed_table.item(selected[0])["values"]
        self.selected_bed_id = values[0]

        self.bed_room_entry.delete(0, tk.END)
        self.bed_room_entry.insert(0, values[1])
        self.bed_ward_entry.delete(0, tk.END)
        self.bed_ward_entry.insert(0, values[2])
        self.bed_status_combo.set(values[3] if values[3] else "")
        self.bed_charge_entry.delete(0, tk.END)
        self.bed_charge_entry.insert(0, values[4])

    def handle_add_bed(self):
        room_no = self.bed_room_entry.get().strip()
        ward_type = self.bed_ward_entry.get().strip()
        status = self.bed_status_combo.get().strip() or "Available"
        charge = self.bed_charge_entry.get().strip() or "0"
        if not room_no:
            messagebox.showwarning("Missing info", "Room number is required.")
            return
        if not is_valid_number(charge):
            messagebox.showwarning("Invalid charge", "Charge per day must be a number.")
            return
        if add_bed(room_no, ward_type, status, charge):
            messagebox.showinfo("Success", "Bed added successfully.")
            self.clear_bed_fields()
            self.load_beds()

    def handle_update_bed(self):
        if not hasattr(self, "selected_bed_id"):
            messagebox.showwarning("No selection", "Please select a bed from the table first.")
            return
        room_no = self.bed_room_entry.get().strip()
        ward_type = self.bed_ward_entry.get().strip()
        status = self.bed_status_combo.get().strip()
        charge = self.bed_charge_entry.get().strip() or "0"
        if not room_no:
            messagebox.showwarning("Missing info", "Room number is required.")
            return
        if not is_valid_number(charge):
            messagebox.showwarning("Invalid charge", "Charge per day must be a number.")
            return
        if update_bed(self.selected_bed_id, room_no, ward_type, status, charge):
            messagebox.showinfo("Success", "Bed updated successfully.")
            self.clear_bed_fields()
            self.load_beds()

    def handle_delete_bed(self):
        if not hasattr(self, "selected_bed_id"):
            messagebox.showwarning("No selection", "Please select a bed from the table first.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            if delete_bed(self.selected_bed_id):
                messagebox.showinfo("Deleted", "Bed deleted successfully.")
                self.clear_bed_fields()
                self.load_beds()

    def clear_bed_fields(self):
        self.bed_room_entry.delete(0, tk.END)
        self.bed_ward_entry.delete(0, tk.END)
        self.bed_status_combo.set("")
        self.bed_charge_entry.delete(0, tk.END)
        if hasattr(self, "selected_bed_id"):
            del self.selected_bed_id

    # APPOINTMENT TAB - full CRUD (LINK ENTITY: patient <-> doctor)
    def build_appointment_tab(self):
        frame = self.appointment_tab
        self.add_header(frame, "Appointment")

        form = tk.Frame(frame)
        form.pack(pady=10)

        tk.Label(form, text="Patient:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.appt_patient_combo = ttk.Combobox(form, width=28, state="readonly")
        self.appt_patient_combo.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(form, text="Doctor:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.appt_doctor_combo = ttk.Combobox(form, width=28, state="readonly")
        self.appt_doctor_combo.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(form, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.appt_date_entry = tk.Entry(form, width=30)
        self.appt_date_entry.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(form, text="Time (HH:MM:SS):").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.appt_time_entry = tk.Entry(form, width=30)
        self.appt_time_entry.grid(row=3, column=1, padx=5, pady=3)

        tk.Label(form, text="Status:").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        self.appt_status_combo = ttk.Combobox(form, width=28, state="readonly",
                                               values=["Scheduled", "Completed", "Cancelled"])
        self.appt_status_combo.grid(row=4, column=1, padx=5, pady=3)

        self.refresh_appointment_dropdowns()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", width=10, bg="#3B8BD4", fg="white",
                  command=self.handle_add_appointment).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, bg="#EF9F27", fg="white",
                  command=self.handle_update_appointment).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, bg="#E24B4A", fg="white",
                  command=self.handle_delete_appointment).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10,
                  command=self.clear_appointment_fields).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Refresh Lists", width=12,
                  command=self.refresh_appointment_dropdowns).grid(row=0, column=4, padx=5)

        columns = ("appointment_id", "patient_name", "doctor_name", "appointment_date",
                   "appointment_time", "status")
        self.appointment_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.appointment_table.heading(col, text=col)
            self.appointment_table.column(col, width=110)
        self.appointment_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.appointment_table.bind("<<TreeviewSelect>>", self.on_appointment_row_select)
        self.load_appointments()
    def refresh_appointment_dropdowns(self):
        self.appt_patient_pairs = get_patient_pairs()
        self.appt_doctor_pairs = get_doctor_pairs()
        self.appt_patient_combo["values"] = [name for (_id, name) in self.appt_patient_pairs]
        self.appt_doctor_combo["values"] = [name for (_id, name) in self.appt_doctor_pairs]

    def load_appointments(self):
        for row in self.appointment_table.get_children():
            self.appointment_table.delete(row)
        for record in get_all_appointments():
            self.appointment_table.insert("", "end", values=record[:6])

    def on_appointment_row_select(self, event):
        selected = self.appointment_table.selection()
        if not selected:
            return
        values = self.appointment_table.item(selected[0])["values"]
        self.selected_appointment_id = values[0]

        self.appt_patient_combo.set(values[1] if values[1] else "")
        self.appt_doctor_combo.set(values[2] if values[2] else "")
        self.appt_date_entry.delete(0, tk.END)
        self.appt_date_entry.insert(0, values[3])
        self.appt_time_entry.delete(0, tk.END)
        self.appt_time_entry.insert(0, values[4])
        self.appt_status_combo.set(values[5] if values[5] else "")

    def get_selected_patient_id(self):
        selected_name = self.appt_patient_combo.get()
        for pid, name in self.appt_patient_pairs:
            if name == selected_name:
                return pid
        return None

    def get_selected_doctor_id_for_appointment(self):
        selected_name = self.appt_doctor_combo.get()
        for did, name in self.appt_doctor_pairs:
            if name == selected_name:
                return did
        return None

    def handle_add_appointment(self):
        patient_id = self.get_selected_patient_id()
        doctor_id = self.get_selected_doctor_id_for_appointment()
        date = self.appt_date_entry.get().strip()
        time = self.appt_time_entry.get().strip()
        status = self.appt_status_combo.get().strip() or "Scheduled"

        if patient_id is None or doctor_id is None:
            messagebox.showwarning("Missing info", "Please select both a patient and a doctor.")
            return
        if not date or not is_valid_date(date):
            messagebox.showwarning("Invalid date", "Please enter a valid date (YYYY-MM-DD).")
            return
        if not time or not is_valid_time(time):
            messagebox.showwarning("Invalid time", "Please enter a valid time (HH:MM:SS).")
            return

        # Double-booking check: eki doctor er eki date+time e onno appointment thakle atkabe
        if is_doctor_slot_taken(doctor_id, date, time):
            messagebox.showwarning(
                "Slot unavailable",
                "This doctor already has an appointment at this date and time. "
                "Please choose a different time."
            )
            return

        if add_appointment(patient_id, doctor_id, date, time, status):
            messagebox.showinfo("Success", "Appointment booked successfully.")
            self.clear_appointment_fields()
            self.load_appointments()

    def handle_update_appointment(self):
        if not hasattr(self, "selected_appointment_id"):
            messagebox.showwarning("No selection", "Please select an appointment from the table first.")
            return
        patient_id = self.get_selected_patient_id()
        doctor_id = self.get_selected_doctor_id_for_appointment()
        date = self.appt_date_entry.get().strip()
        time = self.appt_time_entry.get().strip()
        status = self.appt_status_combo.get().strip()

        if not date or not is_valid_date(date):
            messagebox.showwarning("Invalid date", "Please enter a valid date (YYYY-MM-DD).")
            return
        if not time or not is_valid_time(time):
            messagebox.showwarning("Invalid time", "Please enter a valid time (HH:MM:SS).")
            return

        # Double-booking check - nijer current appointment ke exclude kore check kora hocche
        if is_doctor_slot_taken(doctor_id, date, time, exclude_appointment_id=self.selected_appointment_id):
            messagebox.showwarning(
                "Slot unavailable",
                "This doctor already has another appointment at this date and time. "
                "Please choose a different time."
            )
            return

        if update_appointment(self.selected_appointment_id, patient_id, doctor_id, date, time, status):
            messagebox.showinfo("Success", "Appointment updated successfully.")
            self.clear_appointment_fields()
            self.load_appointments()

    def handle_delete_appointment(self):
        if not hasattr(self, "selected_appointment_id"):
            messagebox.showwarning("No selection", "Please select an appointment from the table first.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            if delete_appointment(self.selected_appointment_id):
                messagebox.showinfo("Deleted", "Appointment deleted successfully.")
                self.clear_appointment_fields()
                self.load_appointments()

    def clear_appointment_fields(self):
        self.appt_patient_combo.set("")
        self.appt_doctor_combo.set("")
        self.appt_date_entry.delete(0, tk.END)
        self.appt_time_entry.delete(0, tk.END)
        self.appt_status_combo.set("")
        if hasattr(self, "selected_appointment_id"):
            del self.selected_appointment_id

    # ADMISSION TAB - full CRUD (LINK ENTITY: patient <-> doctor <-> bed)
    # Bed status auto-syncs with admission/discharge here.
    def build_admission_tab(self):
        frame = self.admission_tab
        self.add_header(frame, "Admission")

        form = tk.Frame(frame)
        form.pack(pady=10)

        tk.Label(form, text="Patient:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.adm_patient_combo = ttk.Combobox(form, width=28, state="readonly")
        self.adm_patient_combo.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(form, text="Doctor:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.adm_doctor_combo = ttk.Combobox(form, width=28, state="readonly")
        self.adm_doctor_combo.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(form, text="Bed (Room No):").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.adm_bed_combo = ttk.Combobox(form, width=28, state="readonly")
        self.adm_bed_combo.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(form, text="Admission Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.adm_date_entry = tk.Entry(form, width=30)
        self.adm_date_entry.grid(row=3, column=1, padx=5, pady=3)

        tk.Label(form, text="Discharge Date (optional):").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        self.adm_discharge_entry = tk.Entry(form, width=30)
        self.adm_discharge_entry.grid(row=4, column=1, padx=5, pady=3)

        tk.Label(form, text="Diagnosis:").grid(row=5, column=0, sticky="e", padx=5, pady=3)
        self.adm_diagnosis_entry = tk.Entry(form, width=30)
        self.adm_diagnosis_entry.grid(row=5, column=1, padx=5, pady=3)

        self.refresh_admission_dropdowns()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", width=10, bg="#3B8BD4", fg="white",
                  command=self.handle_add_admission).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, bg="#EF9F27", fg="white",
                  command=self.handle_update_admission).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, bg="#E24B4A", fg="white",
                  command=self.handle_delete_admission).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10,
                  command=self.clear_admission_fields).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Refresh Lists", width=12,
                  command=self.refresh_admission_dropdowns).grid(row=0, column=4, padx=5)

        note = tk.Label(frame, fg="#666666",
                         text="Note: Bed dropdown shows only Available beds. Setting a discharge date frees the bed.")
        note.pack(pady=(0, 4))

        columns = ("admission_id", "patient_name", "doctor_name", "room_no",
                   "admission_date", "discharge_date", "diagnosis")
        self.admission_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.admission_table.heading(col, text=col)
            self.admission_table.column(col, width=100)
        self.admission_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.admission_table.bind("<<TreeviewSelect>>", self.on_admission_row_select)

        self.load_admissions()

    def refresh_admission_dropdowns(self, keep_current_bed=None):
        """Bed dropdown e sudhu Available bed dekhabe. Update korar somoy currently-selected
        bed o list e rakhte hobe, na hole ai bed select kora jabe na."""
        self.adm_patient_pairs = get_patient_pairs()
        self.adm_doctor_pairs = get_doctor_pairs()
        self.adm_bed_pairs = get_available_bed_pairs()

        if keep_current_bed:
            all_beds = get_bed_pairs()
            for bid, room in all_beds:
                if bid == keep_current_bed and bid not in [b[0] for b in self.adm_bed_pairs]:
                    self.adm_bed_pairs.append((bid, room))

        self.adm_patient_combo["values"] = [name for (_id, name) in self.adm_patient_pairs]
        self.adm_doctor_combo["values"] = [name for (_id, name) in self.adm_doctor_pairs]
        self.adm_bed_combo["values"] = [room for (_id, room) in self.adm_bed_pairs]

    def load_admissions(self):
        for row in self.admission_table.get_children():
            self.admission_table.delete(row)
        for record in get_all_admissions():
            # record = (admission_id, patient_name, doctor_name, room_no, admission_date,
            #           discharge_date, diagnosis, patient_id, doctor_id, bed_id)
            self.admission_table.insert("", "end", values=record[:7])
        # full records (with raw ids) alada rakhi selection mapping er jonno
        self._admission_full_records = {r[0]: r for r in get_all_admissions()}

    def on_admission_row_select(self, event):
        selected = self.admission_table.selection()
        if not selected:
            return
        values = self.admission_table.item(selected[0])["values"]
        self.selected_admission_id = values[0]

        full = self._admission_full_records.get(self.selected_admission_id)
        self.selected_admission_bed_id = full[9] if full else None

        # notun beder dropdown e ei admission-er current bed o dekhano dorkar
        self.refresh_admission_dropdowns(keep_current_bed=self.selected_admission_bed_id)

        self.adm_patient_combo.set(values[1] if values[1] else "")
        self.adm_doctor_combo.set(values[2] if values[2] else "")
        self.adm_bed_combo.set(values[3] if values[3] else "")
        self.adm_date_entry.delete(0, tk.END)
        self.adm_date_entry.insert(0, values[4])
        self.adm_discharge_entry.delete(0, tk.END)
        self.adm_discharge_entry.insert(0, values[5] if values[5] else "")
        self.adm_diagnosis_entry.delete(0, tk.END)
        self.adm_diagnosis_entry.insert(0, values[6] if values[6] else "")

    def get_adm_selected_patient_id(self):
        selected_name = self.adm_patient_combo.get()
        for pid, name in self.adm_patient_pairs:
            if name == selected_name:
                return pid
        return None

    def get_adm_selected_doctor_id(self):
        selected_name = self.adm_doctor_combo.get()
        for did, name in self.adm_doctor_pairs:
            if name == selected_name:
                return did
        return None

    def get_adm_selected_bed_id(self):
        selected_room = self.adm_bed_combo.get()
        for bid, room in self.adm_bed_pairs:
            if room == selected_room:
                return bid
        return None

    def handle_add_admission(self):
        patient_id = self.get_adm_selected_patient_id()
        doctor_id = self.get_adm_selected_doctor_id()
        bed_id = self.get_adm_selected_bed_id()
        date = self.adm_date_entry.get().strip()
        discharge = self.adm_discharge_entry.get().strip()
        diagnosis = self.adm_diagnosis_entry.get().strip()

        if patient_id is None or doctor_id is None or bed_id is None:
            messagebox.showwarning("Missing info", "Please select patient, doctor, and bed.")
            return
        if not date or not is_valid_date(date):
            messagebox.showwarning("Invalid date", "Please enter a valid admission date (YYYY-MM-DD).")
            return
        if discharge and not is_valid_date(discharge):
            messagebox.showwarning("Invalid date", "Discharge date must be in YYYY-MM-DD format.")
            return

        if add_admission(patient_id, doctor_id, bed_id, date, discharge, diagnosis):
            messagebox.showinfo("Success", "Patient admitted successfully. Bed marked Occupied.")
            self.clear_admission_fields()
            self.load_admissions()
            self.refresh_admission_dropdowns()

    def handle_update_admission(self):
        if not hasattr(self, "selected_admission_id"):
            messagebox.showwarning("No selection", "Please select an admission record from the table first.")
            return
        patient_id = self.get_adm_selected_patient_id()
        doctor_id = self.get_adm_selected_doctor_id()
        bed_id = self.get_adm_selected_bed_id()
        date = self.adm_date_entry.get().strip()
        discharge = self.adm_discharge_entry.get().strip()
        diagnosis = self.adm_diagnosis_entry.get().strip()

        if bed_id is None:
            messagebox.showwarning("Missing info", "Please select a bed.")
            return
        if not date or not is_valid_date(date):
            messagebox.showwarning("Invalid date", "Please enter a valid admission date (YYYY-MM-DD).")
            return
        if discharge and not is_valid_date(discharge):
            messagebox.showwarning("Invalid date", "Discharge date must be in YYYY-MM-DD format.")
            return

        old_bed_id = getattr(self, "selected_admission_bed_id", None)

        if update_admission(self.selected_admission_id, patient_id, doctor_id, bed_id, date,
                             discharge, diagnosis, old_bed_id=old_bed_id):
            messagebox.showinfo("Success", "Admission updated successfully.")
            self.clear_admission_fields()
            self.load_admissions()
            self.refresh_admission_dropdowns()

    def handle_delete_admission(self):
        if not hasattr(self, "selected_admission_id"):
            messagebox.showwarning("No selection", "Please select an admission record from the table first.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            bed_id = getattr(self, "selected_admission_bed_id", None)
            if delete_admission(self.selected_admission_id, bed_id=bed_id):
                messagebox.showinfo("Deleted", "Admission deleted successfully. Bed freed.")
                self.clear_admission_fields()
                self.load_admissions()
                self.refresh_admission_dropdowns()

    def clear_admission_fields(self):
        self.adm_patient_combo.set("")
        self.adm_doctor_combo.set("")
        self.adm_bed_combo.set("")
        self.adm_date_entry.delete(0, tk.END)
        self.adm_discharge_entry.delete(0, tk.END)
        self.adm_diagnosis_entry.delete(0, tk.END)
        if hasattr(self, "selected_admission_id"):
            del self.selected_admission_id
        if hasattr(self, "selected_admission_bed_id"):
            del self.selected_admission_bed_id

    # PRESCRIPTION TAB - full CRUD (LINK ENTITY: appointment <-> doctor)
    def build_prescription_tab(self):
        frame = self.prescription_tab
        self.add_header(frame, "Prescription")

        form = tk.Frame(frame)
        form.pack(pady=10)

        tk.Label(form, text="Appointment:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.pres_appointment_combo = ttk.Combobox(form, width=35, state="readonly")
        self.pres_appointment_combo.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(form, text="Doctor:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.pres_doctor_combo = ttk.Combobox(form, width=35, state="readonly")
        self.pres_doctor_combo.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(form, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.pres_date_entry = tk.Entry(form, width=37)
        self.pres_date_entry.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(form, text="Medicine Details:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.pres_medicine_entry = tk.Entry(form, width=37)
        self.pres_medicine_entry.grid(row=3, column=1, padx=5, pady=3)

        tk.Label(form, text="Notes:").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        self.pres_notes_entry = tk.Entry(form, width=37)
        self.pres_notes_entry.grid(row=4, column=1, padx=5, pady=3)

        self.refresh_prescription_dropdowns()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", width=10, bg="#3B8BD4", fg="white",
                  command=self.handle_add_prescription).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, bg="#EF9F27", fg="white",
                  command=self.handle_update_prescription).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, bg="#E24B4A", fg="white",
                  command=self.handle_delete_prescription).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10,
                  command=self.clear_prescription_fields).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Refresh Lists", width=12,
                  command=self.refresh_prescription_dropdowns).grid(row=0, column=4, padx=5)

        columns = ("prescription_id", "patient_name", "doctor_name", "prescription_date",
                   "medicine_details", "notes")
        self.prescription_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.prescription_table.heading(col, text=col)
            self.prescription_table.column(col, width=110)
        self.prescription_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.prescription_table.bind("<<TreeviewSelect>>", self.on_prescription_row_select)

        self.load_prescriptions()

    def refresh_prescription_dropdowns(self):
        self.pres_appointment_pairs = get_appointment_pairs()
        self.pres_doctor_pairs = get_doctor_pairs()
        self.pres_appointment_combo["values"] = [text for (_id, text) in self.pres_appointment_pairs]
        self.pres_doctor_combo["values"] = [name for (_id, name) in self.pres_doctor_pairs]

    def load_prescriptions(self):
        for row in self.prescription_table.get_children():
            self.prescription_table.delete(row)
        records = get_all_prescriptions()
        self._prescription_full_records = {r[0]: r for r in records}
        for record in records:
            # record = (prescription_id, patient_name, doctor_name, date, medicine_details,
            #           notes, appointment_id, doctor_id)
            self.prescription_table.insert("", "end", values=record[:6])

    def on_prescription_row_select(self, event):
        selected = self.prescription_table.selection()
        if not selected:
            return
        values = self.prescription_table.item(selected[0])["values"]
        self.selected_prescription_id = values[0]

        # BUG FIX: age appointment combo blank thakto. Ekhon actual appointment_id
        # theke matching display text khuje set kora hoy - billing tab er pattern e.
        full = self._prescription_full_records.get(self.selected_prescription_id)
        appointment_id = full[6] if full else None
        matched_text = ""
        for aid, text in self.pres_appointment_pairs:
            if aid == appointment_id:
                matched_text = text
                break
        self.pres_appointment_combo.set(matched_text)

        self.pres_doctor_combo.set(values[2] if values[2] else "")
        self.pres_date_entry.delete(0, tk.END)
        self.pres_date_entry.insert(0, values[3])
        self.pres_medicine_entry.delete(0, tk.END)
        self.pres_medicine_entry.insert(0, values[4] if values[4] else "")
        self.pres_notes_entry.delete(0, tk.END)
        self.pres_notes_entry.insert(0, values[5] if values[5] else "")

    def get_pres_selected_appointment_id(self):
        selected_text = self.pres_appointment_combo.get()
        for aid, text in self.pres_appointment_pairs:
            if text == selected_text:
                return aid
        return None

    def get_pres_selected_doctor_id(self):
        selected_name = self.pres_doctor_combo.get()
        for did, name in self.pres_doctor_pairs:
            if name == selected_name:
                return did
        return None

    def handle_add_prescription(self):
        appointment_id = self.get_pres_selected_appointment_id()
        doctor_id = self.get_pres_selected_doctor_id()
        date = self.pres_date_entry.get().strip()
        medicine = self.pres_medicine_entry.get().strip()
        notes = self.pres_notes_entry.get().strip()

        if appointment_id is None or doctor_id is None:
            messagebox.showwarning("Missing info", "Please select both an appointment and a doctor.")
            return
        if not date or not is_valid_date(date):
            messagebox.showwarning("Invalid date", "Please enter a valid date (YYYY-MM-DD).")
            return
        if not medicine:
            messagebox.showwarning("Missing info", "Medicine details are required.")
            return

        if add_prescription(appointment_id, doctor_id, date, medicine, notes):
            messagebox.showinfo("Success", "Prescription added successfully.")
            self.clear_prescription_fields()
            self.load_prescriptions()

    def handle_update_prescription(self):
        if not hasattr(self, "selected_prescription_id"):
            messagebox.showwarning("No selection", "Please select a prescription from the table first.")
            return
        appointment_id = self.get_pres_selected_appointment_id()
        doctor_id = self.get_pres_selected_doctor_id()
        date = self.pres_date_entry.get().strip()
        medicine = self.pres_medicine_entry.get().strip()
        notes = self.pres_notes_entry.get().strip()

        if appointment_id is None:
            messagebox.showwarning("Missing info", "Please reselect the appointment from the dropdown.")
            return
        if not date or not is_valid_date(date):
            messagebox.showwarning("Invalid date", "Please enter a valid date (YYYY-MM-DD).")
            return

        if update_prescription(self.selected_prescription_id, appointment_id, doctor_id, date, medicine, notes):
            messagebox.showinfo("Success", "Prescription updated successfully.")
            self.clear_prescription_fields()
            self.load_prescriptions()

    def handle_delete_prescription(self):
        if not hasattr(self, "selected_prescription_id"):
            messagebox.showwarning("No selection", "Please select a prescription from the table first.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            if delete_prescription(self.selected_prescription_id):
                messagebox.showinfo("Deleted", "Prescription deleted successfully.")
                self.clear_prescription_fields()
                self.load_prescriptions()

    def clear_prescription_fields(self):
        self.pres_appointment_combo.set("")
        self.pres_doctor_combo.set("")
        self.pres_date_entry.delete(0, tk.END)
        self.pres_medicine_entry.delete(0, tk.END)
        self.pres_notes_entry.delete(0, tk.END)
        if hasattr(self, "selected_prescription_id"):
            del self.selected_prescription_id

    # BILLING TAB - full CRUD (LINK ENTITY: patient <-> admission)
    def build_billing_tab(self):
        frame = self.billing_tab
        self.add_header(frame, "Billing")

        form = tk.Frame(frame)
        form.pack(pady=10)

        tk.Label(form, text="Patient:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.bill_patient_combo = ttk.Combobox(form, width=35, state="readonly")
        self.bill_patient_combo.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(form, text="Admission (optional):").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.bill_admission_combo = ttk.Combobox(form, width=35, state="readonly")
        self.bill_admission_combo.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(form, text="Total Amount:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.bill_amount_entry = tk.Entry(form, width=37)
        self.bill_amount_entry.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(form, text="Payment Status:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.bill_status_combo = ttk.Combobox(form, width=35, state="readonly",
                                               values=["Paid", "Unpaid", "Partial"])
        self.bill_status_combo.grid(row=3, column=1, padx=5, pady=3)

        tk.Label(form, text="Payment Method:").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        self.bill_method_combo = ttk.Combobox(form, width=35, state="readonly",
                                               values=["Cash", "Card", "Mobile Banking", "Insurance"])
        self.bill_method_combo.grid(row=4, column=1, padx=5, pady=3)
        self.refresh_billing_dropdowns()
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", width=10, bg="#3B8BD4", fg="white",
                  command=self.handle_add_billing).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, bg="#EF9F27", fg="white",
                  command=self.handle_update_billing).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, bg="#E24B4A", fg="white",
                  command=self.handle_delete_billing).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10,
                  command=self.clear_billing_fields).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Refresh Lists", width=12,
                  command=self.refresh_billing_dropdowns).grid(row=0, column=4, padx=5)

        columns = ("bill_id", "patient_name", "admission_id", "total_amount",
                   "bill_date", "payment_status", "payment_method")
        self.billing_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.billing_table.heading(col, text=col)
            self.billing_table.column(col, width=100)
        self.billing_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.billing_table.bind("<<TreeviewSelect>>", self.on_billing_row_select)
        self.load_billings()
    def refresh_billing_dropdowns(self):
        self.bill_patient_pairs = get_patient_pairs()
        self.bill_admission_pairs = get_admission_pairs()
        self.bill_patient_combo["values"] = [name for (_id, name) in self.bill_patient_pairs]
        self.bill_admission_combo["values"] = [text for (_id, text) in self.bill_admission_pairs]

    def load_billings(self):
        for row in self.billing_table.get_children():
            self.billing_table.delete(row)
        for record in get_all_billings():
            self.billing_table.insert("", "end", values=record[:7])

    def on_billing_row_select(self, event):
        selected = self.billing_table.selection()
        if not selected:
            return
        values = self.billing_table.item(selected[0])["values"]
        self.selected_bill_id = values[0]

        self.bill_patient_combo.set(values[1] if values[1] else "")
        admission_id = values[2]
        for aid, text in self.bill_admission_pairs:
            if aid == admission_id:
                self.bill_admission_combo.set(text)
                break
        else:
            self.bill_admission_combo.set("")
        self.bill_amount_entry.delete(0, tk.END)
        self.bill_amount_entry.insert(0, values[3])
        self.bill_status_combo.set(values[5] if values[5] else "")
        self.bill_method_combo.set(values[6] if values[6] else "")

    def get_bill_selected_patient_id(self):
        selected_name = self.bill_patient_combo.get()
        for pid, name in self.bill_patient_pairs:
            if name == selected_name:
                return pid
        return None

    def get_bill_selected_admission_id(self):
        selected_text = self.bill_admission_combo.get()
        for aid, text in self.bill_admission_pairs:
            if text == selected_text:
                return aid
        return None
    def handle_add_billing(self):
        patient_id = self.get_bill_selected_patient_id()
        admission_id = self.get_bill_selected_admission_id()
        amount = self.bill_amount_entry.get().strip()
        status = self.bill_status_combo.get().strip() or "Unpaid"
        method = self.bill_method_combo.get().strip()

        if patient_id is None:
            messagebox.showwarning("Missing info", "Please select a patient.")
            return
        if not amount or not is_valid_number(amount):
            messagebox.showwarning("Invalid amount", "Total amount must be a number.")
            return

        if add_billing(patient_id, admission_id, amount, status, method):
            messagebox.showinfo("Success", "Bill created successfully.")
            self.clear_billing_fields()
            self.load_billings()

    def handle_update_billing(self):
        if not hasattr(self, "selected_bill_id"):
            messagebox.showwarning("No selection", "Please select a bill from the table first.")
            return
        patient_id = self.get_bill_selected_patient_id()
        admission_id = self.get_bill_selected_admission_id()
        amount = self.bill_amount_entry.get().strip()
        status = self.bill_status_combo.get().strip()
        method = self.bill_method_combo.get().strip()

        if not amount or not is_valid_number(amount):
            messagebox.showwarning("Invalid amount", "Total amount must be a number.")
            return

        if update_billing(self.selected_bill_id, patient_id, admission_id, amount, status, method):
            messagebox.showinfo("Success", "Bill updated successfully.")
            self.clear_billing_fields()
            self.load_billings()
    def handle_delete_billing(self):
        if not hasattr(self, "selected_bill_id"):
            messagebox.showwarning("No selection", "Please select a bill from the table first.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            if delete_billing(self.selected_bill_id):
                messagebox.showinfo("Deleted", "Bill deleted successfully.")
                self.clear_billing_fields()
                self.load_billings()
    def clear_billing_fields(self):
        self.bill_patient_combo.set("")
        self.bill_admission_combo.set("")
        self.bill_amount_entry.delete(0, tk.END)
        self.bill_status_combo.set("")
        self.bill_method_combo.set("")
        if hasattr(self, "selected_bill_id"):
            del self.selected_bill_id
# SECTION 6: APP START
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()