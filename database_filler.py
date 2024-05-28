import pymysql
import random
from faker import Faker
from datetime import timedelta, datetime

fake = Faker()

def random_date(start, end):
    """Generate a random date between `start` and `end`."""
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def connect_db():
    """ Establishes a connection to the database. """
    return pymysql.connect(
        host="localhost",
        user="root",
        password="KkEeVv@3141592653$",
        db="Library",
        cursorclass=pymysql.cursors.DictCursor
    )

def populate_employees(cursor, num=10):
    """ Populates the Employee table. """
    for _ in range(num):
        emp_id = fake.unique.bothify(text='EMP######')
        first_name = fake.first_name()
        last_name = fake.last_name()
        joining_date = fake.date_between(start_date='-5y', end_date='today')
        manager_id = random.choice([None, emp_id])  # Randomly assign self or none as manager
        job_desc = fake.sentence(nb_words=6)
        cursor.execute("""
            INSERT INTO Employee (emp_ID, first_name, last_name, joining_date, manager, job_desc)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (emp_id, first_name, last_name, joining_date, manager_id, job_desc))

def populate_members(cursor, num=10):
    """ Populates the Member table. """
    cursor.execute("SELECT emp_ID FROM Employee")
    employee_ids = [item['emp_ID'] for item in cursor.fetchall()]
    for _ in range(num):
        member_id = fake.unique.bothify(text='MEM######')
        assigned_emp = random.choice(employee_ids)
        family_members = random.randint(1, 5)
        city = fake.city()
        mobile_no = fake.unique.bothify(text='##########')  # Assuming 10-digit mobile number
        joining_date = fake.date_between(start_date='-5y', end_date='today')
        fine = random.randint(0, 50)
        expiry = random_date(joining_date, joining_date + timedelta(days=365))
        first_name = fake.first_name()
        last_name = fake.last_name()
        cursor.execute("""
            INSERT INTO Member (member_ID, assigned_emp, family_members, city, mobile_no, joining_date, fine, expiry, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (member_id, assigned_emp, family_members, city, mobile_no, joining_date, fine, expiry, first_name, last_name))

def populate_publishers(cursor, num=5):
    """ Populates the Publisher table. """
    for _ in range(num):
        pub_id = fake.unique.bothify(text='PUB######')
        address = fake.address()
        name = fake.company()
        cursor.execute("""
            INSERT INTO Publisher (pub_ID, address, name)
            VALUES (%s, %s, %s)
        """, (pub_id, address, name))

def populate_suppliers(cursor, num=5):
    """ Populates the Supplier table. """
    for _ in range(num):
        supplier_id = fake.unique.bothify(text='SUP######')
        name = fake.company()
        address = fake.address()
        cursor.execute("""
            INSERT INTO Supplier (supplier_ID, name, address)
            VALUES (%s, %s, %s)
        """, (supplier_id, name, address))

def populate_books(cursor, num=20):
    """ Populates the Books table. """
    cursor.execute("SELECT pub_ID FROM Publisher")
    publisher_ids = [item['pub_ID'] for item in cursor.fetchall()]
    cursor.execute("SELECT supplier_ID FROM Supplier")
    supplier_ids = [item['supplier_ID'] for item in cursor.fetchall()]
    for _ in range(num):
        book_id = fake.unique.bothify(text='BK###')
        author = fake.name()
        pub_id = random.choice(publisher_ids)
        title = fake.sentence(nb_words=4)
        genre = random.choice(['Fiction', 'Non-fiction', 'Science', 'History', 'Biography'])
        supplier_id = random.choice(supplier_ids)
        cursor.execute("""
            INSERT INTO Books (book_ID, author, pub_ID, title, genre, supplier_ID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (book_id, author, pub_id, title, genre, supplier_id))

def main():
    db_conn = connect_db()
    cursor = db_conn.cursor()
    try:
        populate_employees(cursor, 10)
        populate_members(cursor, 15)
        populate_publishers(cursor, 5)
        populate_suppliers(cursor, 5)
        populate_books(cursor, 20)
        db_conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        db_conn.rollback()
    finally:
        cursor.close()
        db_conn.close()

if __name__ == "__main__":
    main()
