  
from flask import Flask, request, jsonify
import pymysql.cursors

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

# Create stored procedures and triggers
def create_procedures_and_triggers():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='KkEeVv@3141592653$',
        db='Library',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    try:
        # Create procedures
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

        # Create triggers
        cursor.execute("DROP TRIGGER IF EXISTS check_book_availability;")
        cursor.execute("""
        CREATE TRIGGER check_book_availability
        BEFORE INSERT ON Issues
        FOR EACH ROW
        BEGIN
            DECLARE book_count INT;

            SELECT COUNT(*) INTO book_count
            FROM book_copies
            WHERE book_ID = NEW.book_ID AND availability = 'Yes';

            IF book_count = 0 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book is not available';
            END IF;
        END;
        """)

        cursor.execute("DROP TRIGGER IF EXISTS check_member_fine;")
        cursor.execute("""
        CREATE TRIGGER check_member_fine
        BEFORE INSERT ON Issues
        FOR EACH ROW
        BEGIN
            DECLARE member_fine INT;

            SELECT SUM(fine_amount) INTO member_fine
            FROM Fines
            WHERE member_ID = NEW.member_ID AND paid = 'No';

            IF member_fine > 0 THEN
                SIGNAL SQLSTATE '45001' SET MESSAGE_TEXT = 'Member has pending fine';
            END IF;
        END;
        """)

        cursor.execute("DROP TRIGGER IF EXISTS change_book_availability;")
        cursor.execute("""
        CREATE TRIGGER change_book_availability
        AFTER INSERT ON Issues
        FOR EACH ROW
        BEGIN
            UPDATE book_copies
            SET availability = 'No'
            WHERE issue_id = NEW.issue_ID;
        END;
        """)

        connection.commit()
    
    except Exception as e:
        print("Error creating procedures and triggers: ", e)
    finally:
        cursor.close()
        connection.close()

create_procedures_and_triggers()

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
        JOIN Issues i on bc.issue_id = issue_ID
        where i.member_ID = %s
        """, (member_id,))
        books = cursor.fetchall()
        return jsonify({"books": books})
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
