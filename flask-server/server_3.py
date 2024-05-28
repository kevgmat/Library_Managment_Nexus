# from flask import Flask, request, jsonify
# import pymysql.cursors

# app = Flask(__name__) 

# # Database connection function
# def get_db_connection():
#     connection = pymysql.connect(
#         host='localhost',
#         user='root',
#         password='KkEeVv@3141592653$',
#         db='Library',
#         cursorclass=pymysql.cursors.DictCursor
#     )
#     return connection



# # Members API Route to get members
# @app.route("/members", methods=['GET'])
# def get_members():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM Member")
#     members = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify({"members": members})

# # API route to add a new member
# @app.route("/members", methods=['POST'])
# def add_member():
#     new_member = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO Member (member_ID, first_name, last_name, city) VALUES (%s, %s, %s, %s)",
#                    (new_member['member_ID'], new_member['first_name'], new_member['last_name'], new_member['city']))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return {"message": "Member added successfully"}, 201


# # API route to add new book
# @app.route("/members", methods = ['POST'])
# def add_book():
#     new_book = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO Books (book_ID, author, title, genre) VALUES (%s, %s, %s, %s) ",
#                    (new_book['book_ID'], new_book['author'], new_book['title'], new_book['genre']))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return {"message": "Book added successfully"}, 201

# # API route to get books
# @app.route("/members", methods = ['GET'])
# def get_books():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM Books")
#     books = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify({"books": books})


# if __name__ == "__main__":
#     app.run(debug = True)


# from flask import Flask, request, jsonify
# import pymysql.cursors

# app = Flask(__name__)

# # Database connection function
# def get_db_connection():
#     connection = pymysql.connect(
#         host='localhost',
#         user='root',
#         password='KkEeVv@3141592653$',
#         db='Library',
#         cursorclass=pymysql.cursors.DictCursor
#     )
#     return connection

# # Members API Route to get members
# @app.route("/members", methods=['GET'])
# def get_members():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM Member")
#     members = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify({"members": members})

# # API route to add a new member
# @app.route("/members", methods=['POST'])
# def add_member():
#     new_member = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO Member (member_ID, first_name, last_name, city) VALUES (%s, %s, %s, %s)",
#                    (new_member['member_ID'], new_member['first_name'], new_member['last_name'], new_member['city']))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return {"message": "Member added successfully"}, 201

# # API route to add new book
# @app.route("/books", methods=['POST'])
# def add_book():
#     new_book = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO Books (book_ID, author, title, genre) VALUES (%s, %s, %s, %s)",
#                    (new_book['book_ID'], new_book['author'], new_book['title'], new_book['genre']))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return {"message": "Book added successfully"}, 201

# # API route to get books
# @app.route("/books", methods=['GET'])
# def get_books():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM Books")
#     books = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify({"books": books})

# if __name__ == "__main__":
#     app.run(debug=True)




## Test1

from flask import Flask, request, jsonify
import pymysql.cursors
from datetime import datetime
from dateutil.relativedelta import relativedelta


app = Flask(__name__)

# Database connection function
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='KkEeVv@3141592653$',
        db='Library',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def create_procedures_and_triggers():
    connection = pymysql.connect(
        host = 'localhost',
        user = 'root',
        password = 'KkEeVv@3141592653$',
        db = 'Library',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    try:
        #create procedures
        cursor.execute("DROP PROCEDURE IF EXISTS AddNewMember;")
        cursor.execute("""
        CREATE PROCEDURE AddNewMember(IN memID char(10), IN fName varchar(50), IN lName varchar(50), IN cty varchar(50))
        BEGIN
            INSERT INTO Member (member_ID, first_name, last_name, city)
            VALUES (memID, fName, lName, cty);
        END;
        """)

        cursor.execute("DROP PROCEDURE IF EXISTS AddNewBook;")
        cursor.execute("""
        CREATE PROCEDURE AddNewBook(IN bID char(5),IN auth varchar(50), IN ttl varchar(200), IN gnr varchar(50))
        BEGIN
            INSERT INTO Books (book_ID, author, title, genre)
            VALUES (bID, auth, ttl, gnr);
        END;
        """)

        ##create triggers
        cursor.execute("DROP TRIGGER IF EXISTS check_book_availability;")
        cursor.execute("""
        CREATE TRIGGER check_book_availability               
        BEFORE INSERT ON Issues
        FOR EACH ROW
        BEGIN
            DECLARE available_status VARCHAR(3);
            SELECT available INTO available_status FROM book_copies WHERE copy_ID = NEW.copy_ID;
            IF available_status != 'YES' THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This book is not available for issuing.';
            END IF;
        END;
        """)

        connection.commit()
    
    except Exception as e:
        print("Error creating procedures: ", e)
    finally:
        cursor.close()
        connection.close()

create_procedures_and_triggers()


# update availability of status
@app.route("/issue_book", methods=['POST'])
def issue_book():
    data = request.json
    member_id = data['member_id']
    copy_id = data['copy_id']
    current_date = datetime.now()
    borrow_date = current_date.strftime('%Y-%m-%d')  # format date
    return_date = current_date + relativedelta(months =+1) 
    return_date = return_date.strftime('%Y-%m-%d')# You might want to calculate this based on the borrow_date
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the book copy is available
        cursor.execute("SELECT available FROM book_copies WHERE copy_ID = %s", (copy_id,))
        availability = cursor.fetchone()
        print(availability['available'])
    
        if availability['available'] == 'YES':
            # Insert into Issues table

            original_string = copy_id
            last_three = original_string[-3:]
            new_string = "ISD0000" + last_three
            cursor.execute("""
                INSERT INTO Issues (issue_ID, copy_ID, member_ID, borrow_date, return_date, fine)
                VALUES (%s, %s, %s, %s, %s, 0)
            """, (new_string,copy_id, member_id, borrow_date, return_date))
            # Update the book_copies table to mark the book as not available
            cursor.execute("UPDATE book_copies SET available = 'No' WHERE copy_ID = %s", (copy_id,))
            conn.commit()
            return {"message": "Book issued successfully"}, 201
        else:
            return {"message": "Book not available"}, 400
    finally:
        cursor.close()
        conn.close()

# Members API Route to get members
@app.route("/members", methods=['GET'])
def get_members():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Member")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"members": members})

# API route to add a new member
@app.route("/members", methods=['POST'])
def add_member():
    new_member = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('AddNewMember', [new_member['member_ID'], new_member['first_name'], new_member['last_name'], new_member['city']])
        conn.commit()
        return {"message": "Member added successfully"}, 201
    
    finally:
        cursor.close()
        conn.close()


# API route to add new book
@app.route("/books", methods=['POST'])
def add_book():
    new_book = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('AddNewBook', [new_book['book_ID'], new_book['author'], new_book['title'], new_book['genre']])
        conn.commit()
        return {"message": "Book added successfully"}, 201
    
    finally:
        cursor.close()
        conn.close()

# API route to get books
@app.route("/books", methods=['GET'])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"books": books})

# API route to get the books of the members
@app.route("/members/books/<member_id>", methods= ['GET'])
def get_member_books(member_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT b.title, b.author, i.borrow_date, i.return_date
        from Books b
        JOIN book_copies bc ON b.book_ID = bc.book_ID
        JOIN Issues i on bc.copy_ID = i.copy_ID
        where i.member_ID = %s
        """, (member_id,))
        books = cursor.fetchall()
        return jsonify({"books": books})
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)


