import base64
import numbers
from wsgiref.util import request_uri
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
import mysql.connector
import bcrypt
from werkzeug.security import gen_salt
from datetime import datetime
import bcrypt
import ssl
import smtplib
import certifi
from email.message import EmailMessage
import threading

app = Flask(__name__)

app.secret_key = "secret_key"


@app.route("/", methods=["GET", "POST"])
def index():





    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    username_input = request.form.get("user_input")






    if username_input != "":
        password_input = request.form.get("password_input")
        c.execute("SELECT password FROM users WHERE username = %s", (username_input,))
        try:
            checking_pass = c.fetchone()[0]

        except TypeError:   return render_template("index.html", details_correct=False, username_input=username_input)


        try:
            password_correct = bcrypt.checkpw(password_input.encode(),checking_pass)

            if password_correct:

                username_input2 = request.form.get("user_input")
                session["username"] = username_input2





                conn = mysql.connector.connect(
                    host="localhost",  # or "127.0.0.1"
                    user="root",  # Your MySQL username
                    password="Password1298!",  # Your MySQL password
                    database="tickets"  # Your MySQL database name
                )
                c = conn.cursor()
                c.execute("SELECT level FROM users WHERE username = %s ", (username_input2,))
                session["level"] = c.fetchone()[0]




                c.execute("SELECT company_name FROM users WHERE username = %s ", (username_input2,))
                session["company"] = c.fetchone()[0]

                session["full_name"] = f"{session["username"]} [{session["company"]}]"

                c.execute("""
                    SELECT partner
                    FROM (
                        SELECT 
                            CASE 
                                WHEN `from` = %s THEN `to`
                                ELSE `from`
                            END AS partner,
                            MAX(STR_TO_DATE(CONCAT(date, ' ', timestamp), '%Y-%m-%d %H:%i')) AS latest_message_time
                        FROM messages
                        WHERE `from` = %s OR `to` = %s
                        GROUP BY partner
                    ) AS conversation_partners
                    ORDER BY latest_message_time DESC
                """, (username_input2, username_input2, username_input2))



                chat_partners = [row[0] for row in c.fetchall()]





                c.execute("SELECT username FROM users WHERE username != %s ", (username_input2,))
                options = [row[0] for row in c.fetchall()]
                session["users_beside_own"] = options

                c.execute("SELECT created_by FROM users WHERE username = %s",(username_input2,))
                session["created_by"] = c.fetchone()[0]


                c.execute("SELECT * FROM messages WHERE `to` = %s and seen = %s ",(username_input2,"no"))
                all_unread_messages = len(c.fetchall())

                user_unread = None
                if all_unread_messages > 0:
                    c.execute("SELECT `from` FROM messages WHERE `to` = %s and seen = %s",(username_input2,"no"))
                    all_users_with_unread_messages = [row[0] for row in c.fetchall()]

                    user_unread = all_users_with_unread_messages
                    print(user_unread)














                conn.close()

                if username_input2 != "" and all_unread_messages > 0:
                    return render_template("index3.html",created_by = session["created_by"] ,level=session["level"], username=session["username"], company=session["company"], chat_partners=chat_partners, options=options, unread_messages=all_unread_messages,all_users_with_unread_messages=user_unread)

                if username_input2 != "" and all_unread_messages == 0:
                         return render_template("index3.html",created_by = session["created_by"] ,level=session["level"], username=session["username"], company=session["company"], chat_partners=chat_partners, options=options, unread_messages=all_unread_messages)


            else: return render_template("index.html")




        except AttributeError:
            return render_template("index.html", details_correct=True, username_input=username_input)





@app.route("/run", methods=["POST"])
def run():
    level = session.get("level")

    severity = request.form.get("severity")
    customer = request.form.get("customer")
    equipment = request.form.get("Equipment")
    description = request.form.get("description")
    allocated_to = request.form.get("allocated_to")
    file = request.files.get('file')
    username = session.get("username")

    file_data = file.read()

    today = datetime.now().strftime("%d/%m/%y")

    if not allocated_to or allocated_to == "None":
        default_status = "open"
    else:
        default_status = "allocated"

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute("""INSERT INTO ticketCreationNEW1 (severity, customer, equipment, description, allocated_to, status, date, files)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
              (severity, customer, equipment, description, allocated_to, default_status, today, file_data))

    conn.commit()

    c.execute("SELECT id FROM ticketCreationNEW1")
    amount_tickets = c.fetchall()
    ticket_number = len(amount_tickets)









    conn.close()


    return render_template("index1.html", ticket_number=ticket_number, allocated_to=allocated_to, level=level)

@app.route("/customer_run", methods=["POST"])
def customer_run():
    level = session.get("level")
    username = session.get("username")
    company_name = session.get("company")
    file = request.files.get('file')
    file_data = file.read()



    severity = request.form.get("severity")
    customer = f"{username}  [{company_name}]"
    equipment = request.form.get("Equipment")
    description = request.form.get("description")
    allocated_to = 'default allocation'

    today = datetime.now().strftime("%d/%m/%y")

    if not allocated_to or allocated_to == "None":
        default_status = "open"
    else:
        default_status = "allocated"

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute("""INSERT INTO ticketCreationNEW1 (severity, customer, equipment, description, allocated_to, status, date, files)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
              (severity, customer, equipment, description, allocated_to, default_status, today, file_data))

    conn.commit()

    c.execute("SELECT id FROM ticketCreationNEW1")
    amount_tickets = c.fetchall()
    ticket_number = len(amount_tickets)


    conn.close()


    return render_template("index1.html", ticket_number=ticket_number, allocated_to=allocated_to, level=level)




def get_tickets():

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute("SELECT id, severity, customer, equipment, description, allocated_to, status, date FROM ticketCreationNEW1")


    tickets = c.fetchall()
    conn.close()
    return tickets




@app.route('/get_filter_values')
def get_filter_values():
    category = request.args.get("category")

    # Ensure the category exists in valid columns
    valid_columns = ["severity","customer", "equipment", "allocated_to", "status"]
    if category not in valid_columns:
        return jsonify({"values": []})  # Return empty list if invalid category

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute(f"SELECT DISTINCT {category} FROM ticketCreationNEW1")
    values = [row[0] for row in c.fetchall()]
    conn.close()

    return jsonify({"values": values})  # Send data to frontend



@app.route('/filter', methods=['GET','POST'])
def filter_data():

    category = request.form.get("filter_category")
    filter_value = request.form.get("filter_value")
    level = session.get("level")
    username = session.get("username")
    company_name = session.get("company")

    session['selected_filter_category'] = request.form.get('filter_category')
    session['selected_filter_value'] = request.form.get('filter_value')

    selected_filter_category = session.get('selected_filter_category')
    selected_filter_value = session.get('selected_filter_value')

    customer = f"{username}  [{company_name}]"

    if not category or not filter_value:
        return redirect(url_for("show_tickets"))

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()

    # Fetch all columns from ticketCreationNEW1 where the selected filter matches the filter value
    query = f"""
        SELECT id, severity, customer, equipment, description, allocated_to, status, date
        FROM ticketCreationNEW1
        WHERE {category} = %s
    """
    c.execute(query, (filter_value,))
    ticket_data = c.fetchall()

    # Fetch ticket IDs for notes (same filtering as above)
    c.execute(f"SELECT id FROM ticketCreationNEW1 WHERE {category} = %s", (filter_value,))
    ticket_ids = [row[0] for row in c.fetchall()]
    conn.close()

    # Process tickets to include notes
    ticket_notes_data = []
    for i, ticket in enumerate(ticket_data):
        ticket_id = ticket_ids[i]

        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()
        c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
        every_note = c.fetchall()
        conn.close()

        valid_notes = [note for note in every_note if note is not None and not isinstance(note, (int, float))]
        amount_valid_notes = len(valid_notes) if every_note else 0

        ticket_notes_data.append({
            'ticket': ticket,
            'ticket_id': ticket_id,
            'amount_valid_notes': amount_valid_notes
        })

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Password1298!",
            database="tickets"
        )
        c = conn.cursor()

        c.execute("SELECT * FROM allocated_to")
        supporters = c.fetchall()

        c.execute("SELECT id FROM ticketCreationNEW1 WHERE status != %s", ("closed",))
        t_count_admin1 = c.fetchall()

        t_count_admin = len(t_count_admin1)
        page_amount_admin_number = 0
        page_amount_admin = ""

        for i in range(0, t_count_admin, 20):
            page_amount_admin_number += 1
            page_amount_admin += f"{page_amount_admin_number}"

        c.execute("SELECT id FROM ticketCreationNEW1 WHERE allocated_to = %s", (username,))
        t_count_supporter1 = c.fetchall()
        t_count_supporter = len(t_count_supporter1)

        page_amount_supporter_number = 0
        page_amount_supporter = ""

        for i in range(0, t_count_supporter, 20):
            page_amount_supporter_number += 1
            page_amount_supporter = f"{page_amount_supporter_number}"

        c.execute("SELECT id FROM ticketCreationNEW1 WHERE customer = %s", (customer,))
        t_count_customer1 = c.fetchall()

        t_count_customer = len(t_count_customer1)

        page_amount_customer_number = 0
        page_amount_customer = ""
        for i in range(0, t_count_customer, 20):
            page_amount_customer_number += 1
            page_amount_customer = f"{page_amount_customer_number}"

    if level == 'Admin':

    # Render the template with the necessary variables
     return render_template("index2.html", ticket_notes_data=ticket_notes_data, level=level, username=username, full_name=customer, selected_filter_value=selected_filter_value, selected_filter_category=selected_filter_category, supporters=supporters, t_count_admin=t_count_admin, page_amount_admin=page_amount_admin)

    if level == "Customer":

     return render_template("index2ForCustomer.html", ticket_notes_data=ticket_notes_data, level=level, username=username, full_name=customer, selected_filter_value=selected_filter_value, selected_filter_category=selected_filter_category, t_count_customer=t_count_customer, page_amount_customer=page_amount_customer)

    if level == "Supporter":
     return render_template("index2ForSupporter.html", ticket_notes_data=ticket_notes_data, level=level, username=username, full_name=customer, selected_filter_value=selected_filter_value, selected_filter_category=selected_filter_category, t_count_supporter=t_count_supporter, page_amount_supporter=page_amount_supporter)




@app.route('/remove_filter')
def remove_filter():
    return redirect(url_for("show_tickets"))  # Reset to default view



@app.route('/sort', methods=['GET', 'POST'])
def sort_data():


    level = session.get("level")

    if level != None:
        username = session.get("username")
        company_name = session.get("company")
        customer = f"{username}  [{company_name}]"
        # Get the sorting option from the form submission, default to 'id low to high' if not selected
        selected_sorting_option = request.form.get("sorting_option", "id low to high")

        ticket_notes_data = []  # Initialize ticket_notes_data

        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()

        # Sorting based on selected option
        if selected_sorting_option == "id low to high":
            c.execute(
                "SELECT id, severity, customer, equipment, description, allocated_to, status, date FROM ticketCreationNEW1")
            ticket_data = c.fetchall()

            c.execute("SELECT id FROM ticketCreationNEW1")
            ticket_ids = [id[0] for id in c.fetchall()]

            for i, ticket in enumerate(ticket_data):
                ticket_id = ticket_ids[i]

                c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
                every_note = c.fetchall()

                if every_note:
                    valid_notes = [note for note in every_note if note is not None and not isinstance(note, (int, float))]
                    amount_valid_notes = len(valid_notes)
                else:
                    amount_valid_notes = 0

                ticket_notes_data.append({
                    'ticket': ticket,
                    'ticket_id': ticket_id,
                    'amount_valid_notes': amount_valid_notes
                })

        elif selected_sorting_option == "id high to low":
            c.execute(
                "SELECT id, severity, customer, equipment, description, allocated_to, status, date FROM ticketCreationNEW1 ORDER BY id DESC;")
            ticket_data = c.fetchall()

            c.execute("SELECT id FROM ticketCreationNEW1 ORDER BY id DESC")
            ticket_ids = [id[0] for id in c.fetchall()]

            for i, ticket in enumerate(ticket_data):
                ticket_id = ticket_ids[i]

                c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
                every_note = c.fetchall()

                if every_note:
                    valid_notes = [note for note in every_note if note is not None and not isinstance(note, (int, float))]
                    amount_valid_notes = len(valid_notes)
                else:
                    amount_valid_notes = 0

                ticket_notes_data.append({
                    'ticket': ticket,
                    'ticket_id': ticket_id,
                    'amount_valid_notes': amount_valid_notes

                })

        elif selected_sorting_option == "severity high to low":
            c.execute(
                "SELECT * FROM ticketCreationNEW1 ORDER BY severity ASC;")
            ticket_data = c.fetchall()

            c.execute("SELECT id FROM ticketCreationNEW1 ORDER BY severity ASC")
            ticket_ids = [id[0] for id in c.fetchall()]

            for i, ticket in enumerate(ticket_data):
                ticket_id = ticket_ids[i]

                c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
                every_note = c.fetchall()

                if every_note:
                    valid_notes = [note for note in every_note if note is not None and not isinstance(note, (int, float))]
                    amount_valid_notes = len(valid_notes)
                else:
                    amount_valid_notes = 0

                ticket_notes_data.append({
                    'ticket': ticket,
                    'ticket_id': ticket_id,
                    'amount_valid_notes': amount_valid_notes
                })

        elif selected_sorting_option == "severity low to high":
            c.execute(
                "SELECT * FROM ticketCreationNEW1 ORDER BY severity DESC;")
            ticket_data = c.fetchall()

            c.execute("SELECT id FROM ticketCreationNEW1 ORDER BY severity DESC")
            ticket_ids = [id[0] for id in c.fetchall()]

            for i, ticket in enumerate(ticket_data):
                ticket_id = ticket_ids[i]

                c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
                every_note = c.fetchall()

                if every_note:
                    valid_notes = [note for note in every_note if note is not None and not isinstance(note, (int, float))]
                    amount_valid_notes = len(valid_notes)
                else:
                    amount_valid_notes = 0

                ticket_notes_data.append({
                    'ticket': ticket,
                    'ticket_id': ticket_id,
                    'amount_valid_notes': amount_valid_notes
                })

        elif selected_sorting_option == "customer":
            c.execute(
                "SELECT * FROM ticketCreationNEW1 ORDER BY customer DESC;")
            ticket_data = c.fetchall()

            c.execute("SELECT id FROM ticketCreationNEW1 ORDER BY customer DESC")
            ticket_ids = [id[0] for id in c.fetchall()]

            for i, ticket in enumerate(ticket_data):
                ticket_id = ticket_ids[i]

                c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
                every_note = c.fetchall()

                if every_note:
                    valid_notes = [note for note in every_note if note is not None and not isinstance(note, (int, float))]
                    amount_valid_notes = len(valid_notes)
                else:
                    amount_valid_notes = 0

                ticket_notes_data.append({
                    'ticket': ticket,
                    'ticket_id': ticket_id,
                    'amount_valid_notes': amount_valid_notes
                })

        elif selected_sorting_option == "allocation":
            c.execute(
                "SELECT * FROM ticketCreationNEW1 ORDER BY allocated_to DESC;")
            ticket_data = c.fetchall()

            c.execute("SELECT id FROM ticketCreationNEW1 ORDER BY allocated_to DESC")
            ticket_ids = [id[0] for id in c.fetchall()]

            for i, ticket in enumerate(ticket_data):
                ticket_id = ticket_ids[i]

                c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
                every_note = c.fetchall()

                if every_note:
                    valid_notes = [note for note in every_note if note is not None and not isinstance(note, (int, float))]
                    amount_valid_notes = len(valid_notes)
                else:
                    amount_valid_notes = 0

                ticket_notes_data.append({
                    'ticket': ticket,
                    'ticket_id': ticket_id,
                    'amount_valid_notes': amount_valid_notes
                })




        conn.close()

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Password1298!",
            database="tickets"
        )
        c = conn.cursor()

        c.execute("SELECT * FROM allocated_to")
        supporters = c.fetchall()

        c.execute("SELECT id FROM ticketCreationNEW1 WHERE status != %s", ("closed",))
        t_count_admin1 = c.fetchall()

        t_count_admin = len(t_count_admin1)
        page_amount_admin_number = 0
        page_amount_admin = ""

        for i in range(0, t_count_admin, 20):
            page_amount_admin_number += 1
            page_amount_admin += f"{page_amount_admin_number}"

        c.execute("SELECT id FROM ticketCreationNEW1 WHERE allocated_to = %s", (username,))
        t_count_supporter1 = c.fetchall()
        t_count_supporter = len(t_count_supporter1)

        page_amount_supporter_number = 0
        page_amount_supporter = ""

        for i in range(0, t_count_supporter, 20):
            page_amount_supporter_number += 1
            page_amount_supporter = f"{page_amount_supporter_number}"

        c.execute("SELECT id FROM ticketCreationNEW1 WHERE customer = %s", (customer,))
        t_count_customer1 = c.fetchall()

        t_count_customer = len(t_count_customer1)

        page_amount_customer_number = 0
        page_amount_customer = ""
        for i in range(0, t_count_customer, 20):
            page_amount_customer_number += 1
            page_amount_customer = f"{page_amount_customer_number}"

        if level == 'Admin':

        # Render the template with the necessary variables
            return render_template("index2.html", ticket_notes_data=ticket_notes_data, level=level, username=username, full_name=customer,  selected_sorting_option=selected_sorting_option, supporters=supporters, t_count_admin=t_count_admin, page_amount_admin=page_amount_admin)

        if level == 'Customer':

            return render_template("index2ForCustomer.html", ticket_notes_data=ticket_notes_data, level=level, username=username,
                                   full_name=customer, selected_sorting_option=selected_sorting_option, t_count_customer=t_count_customer, page_amount_customer=page_amount_customer)


        if level == 'Supporter':

            return render_template("index2ForSupporter.html", ticket_notes_data=ticket_notes_data, level=level, username=username,
                                   full_name=customer, selected_sorting_option=selected_sorting_option, t_count_supporter=t_count_supporter, page_amount_supporter=page_amount_supporter)

    else: return redirect(url_for("index"))





@app.route('/show-tickets', methods=["POST", "GET"])
def show_tickets():
    level = session.get("level")
    if level is None:
        return redirect(url_for("index"))

    username = session.get("username")
    company_name = session.get("company")
    customer = f"{username}  [{company_name}]"

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password1298!",
        database="tickets"
    )
    c = conn.cursor()

    page_number = request.form.get("page_button")

    if page_number is not None:
        offset_number = (int(page_number) - 1) * 30  # <-- fix here
        print(offset_number)

        c.execute("SELECT * FROM ticketCreationNEW1 ORDER BY id LIMIT 30 OFFSET %s", (offset_number,))

    else:
        c.execute("SELECT * FROM ticketCreationNEW1 ORDER BY id LIMIT 30")




    ticket_data = c.fetchall()



    # Fetch notes
    c.execute("SELECT id, note FROM notes")
    notes_data = c.fetchall()
    notes_dict = {}
    for note_id, note in notes_data:
        if note_id in notes_dict:
            notes_dict[note_id].append(note.encode("utf-8") if isinstance(note, str) else note)
        else:
            notes_dict[note_id] = [note.encode("utf-8") if isinstance(note, str) else note]

    ticket_notes_data = []
    for ticket in ticket_data:
        ticket_id = ticket[0]
        image_blob = ticket[9]
        valid_notes = notes_dict.get(ticket_id, [])
        amount_valid_notes = len(valid_notes)
        image_base64 = base64.b64encode(image_blob).decode("utf-8") if isinstance(image_blob, (bytes, bytearray)) else None

        ticket_notes_data.append({
            'ticket': ticket,
            'ticket_id': ticket_id,
            'amount_valid_notes': amount_valid_notes,
            'image': image_base64
        })

    # Pagination setup
    c.execute("SELECT id FROM ticketCreationNEW1 WHERE status != %s", ("closed",))
    t_count_admin = len(c.fetchall())
    page_amount_admin_number = 0
    page_amount_admin = ""

    # Use a for loop with steps of 30
    for i in range(0, t_count_admin, 30):
        page_amount_admin_number += 1
        page_amount_admin += f"{page_amount_admin_number}"

    # If there are leftover tickets (less than 30), it will run one more time





    c.execute("SELECT id FROM ticketCreationNEW1 WHERE allocated_to = %s", (username,))
    t_count_supporter = len(c.fetchall())
    page_amount_supporter_number = 0
    page_amount_supporter = ""

    # Loop through tickets in chunks of 20
    for i in range(0, t_count_supporter, 30):
        page_amount_supporter_number += 1
        page_amount_supporter += f"{page_amount_supporter_number}"


    # If there are leftover tickets (less than 20), it will run one more time
    if t_count_supporter % 30 != 0:
        page_amount_supporter_number += 1
        page_amount_supporter += f"{page_amount_supporter_number}"


    c.execute("SELECT id FROM ticketCreationNEW1 WHERE customer = %s", (customer,))
    t_count_customer = len(c.fetchall())
    page_amount_customer_number = 0
    page_amount_customer = ""

    # Loop through tickets in chunks of 20
    # Loop through tickets in chunks of 20
    for i in range(0, t_count_customer, 30):
        page_amount_customer_number += 1
        page_amount_customer += f"{page_amount_customer_number}"

    # If there are leftover tickets (less than 20), it will run one more time
    if t_count_customer % 30 != 0:
        page_amount_customer_number += 1
        page_amount_customer += f"{page_amount_customer_number}"

    # Fetch supporters
    c.execute("SELECT * FROM allocated_to")
    supporters = c.fetchall()
    conn.close()


    if level == "Admin":
        return render_template("index2.html", ticket_notes_data=ticket_notes_data, level=level, username=username,
                               full_name=customer, supporters=supporters, t_count_admin=t_count_admin,
                               page_amount_admin=page_amount_admin)

    if level == "Customer":
        return render_template("index2ForCustomer.html", ticket_notes_data=ticket_notes_data, level=level,
                               username=username, full_name=customer, t_count_customer=t_count_customer,
                               page_amount_customer=page_amount_customer)

    if level == "Supporter":
        return render_template("index2ForSupporter.html", ticket_notes_data=ticket_notes_data, level=level,
                               username=username, full_name=customer, t_count_supporter=t_count_supporter,
                               page_amount_supporter=page_amount_supporter)





@app.route('/get-notes', methods=["POST"])
def get_notes():
    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )

    # Get the ticket_id and ticket data from the request
    ticket_id = request.json.get('ticket_id')
    ticket_data = request.json.get('ticket_data')



    # Check if ticket_id and ticket_data are available
    if not ticket_id or not ticket_data:
        return jsonify({"error": "ticket_id and ticket_data are required"}), 400

    # Prepare filtered data (exclude None and numeric values)
    filtered_data = {key: value for key, value in ticket_data.items() if not isinstance(value, (int, float)) and value != 'None'}

    # Query the database to get notes based on ticket_id

    c = conn.cursor()
    c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
    notes = c.fetchall()
    conn.close()


    notes_text = [note[0] for note in notes]

    # Send the filtered data and notes back as JSON response
    return jsonify({"filtered_data": filtered_data, "notes": notes_text})



@app.route('/create-note', methods=["POST"])
def create_note():
    data = request.get_json()  # Get the JSON data sent from the front-end
    ticket_id = data.get('ticket_id')
    notes = data.get('notes', [])
    for note in notes:
        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()
        c.execute("INSERT INTO notes (id,note) VALUES (%s,%s)",(ticket_id,note))
        conn.commit()
        conn.close()


    return render_template("index2.html")


@app.route('/changing-status', methods=["POST"])
def changing_status():
    data = request.get_json()  # Get JSON data from the frontend

    changes = []  # Store separated changes

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password1298!",
        database="tickets"
    )
    c = conn.cursor()

    for ticket_id, updates in data.items():
        for dropdown_type, value in updates.items():
            changes.append({
                "ticket_id": ticket_id,
                "dropdown": dropdown_type,
                "new_value": value
            })



            # Execute update for each change
            query = f"UPDATE ticketCreationNEW1 SET {dropdown_type} = %s WHERE id = %s"
            c.execute(query, (value, ticket_id))

    conn.commit()
    conn.close()

    if dropdown_type == "allocated_to":

        username = session.get("username")
        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()
        c.execute("SELECT gmail FROM users WHERE username = %s", (value,))
        supporter_gmail = c.fetchall()[0]
        if supporter_gmail is not None and supporter_gmail != "":
            ssl_context = ssl.create_default_context(cafile=certifi.where())

            email_sender = "probit.help@gmail.com"
            email_password = "oqcw byho hqbr rmcn"
            email_receiver = supporter_gmail

            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
            time_str = now.strftime("%H:%M")

            subject = "Probit-Support-Center"
            body = f"""
                       hello {value}, ticket number {ticket_id} is assigned to you inside probit-support-center
                       
                       

                    """

            em = EmailMessage()
            em["From"] = email_sender
            em["To"] = email_receiver
            em["Subject"] = subject
            em.set_content(body.strip())

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl_context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.send_message(em)

    return jsonify({"message": "Changes saved successfully!", "changes": changes})






@app.route('/changing-status-supporter', methods=["POST"])
def changing_status_supporter():
    data = request.get_json()

    if not data or "updates" not in data:
        return jsonify({"error": "Invalid data format"}), 400

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Password1298!",
            database="tickets"
        )
        c = conn.cursor()

        updated_rows = 0  # Counter to track successful updates

        for entry in data["updates"]:  # Iterate over list of updates
            ticket_id = entry.get("ticket_id")
            new_value = entry.get("status")  # Ensure it gets the correct field

            try:
                ticket_id = int(ticket_id)  # Convert ticket_id to int
            except (ValueError, TypeError):
                print(f"Skipping invalid ticket_id: {ticket_id}")  # Debug print
                continue  # Skip if ticket_id is not valid

            if not new_value:
                print(f"Skipping empty value for ticket_id {ticket_id}")  # Debug print
                continue  # Skip empty values

            print(f"Updating ticket {ticket_id} to status '{new_value}'")  # Debug print

            c.execute("UPDATE ticketCreationNEW1 SET status = %s WHERE id = %s", (new_value, ticket_id))
            updated_rows += c.rowcount  # Track affected rows

        conn.commit()
        c.close()
        conn.close()

        if updated_rows == 0:
            return jsonify({"message": "No rows updated, check input data"}), 400

        return jsonify({"message": "Changes saved successfully!", "updated_rows": updated_rows})

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500




@app.route('/solution', methods=["POST"])
def solution():

    user_solution = request.form.get("user_input")
    ticket_id = request.form.get("ticket_id")

    print("Solution:", user_solution)
    print("Ticket ID:", ticket_id)




    # Connect to the database and update the solution for the given ticket
    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute("UPDATE ticketCreationNEW1 SET solution = %s WHERE id = %s", (user_solution, ticket_id))
    conn.commit()
    conn.close()  # Make sure to close the connection

    show_tickets()
    return redirect(url_for('show_tickets'))



@app.route('/home')
def home():


    username = session.get("username")
    recipient = request.args.get("recipient")

    if username != None:

        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()
        c.execute("SELECT level FROM users WHERE username = %s ", (username,))
        session["level"] = c.fetchone()[0]

        c.execute("SELECT company_name FROM users WHERE username = %s ",(username,))
        session["company"] = c.fetchone()[0]

        c.execute("""
                            SELECT partner
                            FROM (
                                SELECT 
                                    CASE 
                                        WHEN `from` = %s THEN `to`
                                        ELSE `from`
                                    END AS partner,
                                    MAX(STR_TO_DATE(CONCAT(date, ' ', timestamp), '%Y-%m-%d %H:%i')) AS latest_message_time
                                FROM messages
                                WHERE `from` = %s OR `to` = %s
                                GROUP BY partner
                            ) AS conversation_partners
                            ORDER BY latest_message_time DESC
                        """, (username, username, username))

        chat_partners = [row[0] for row in c.fetchall()]

        c.execute("SELECT username FROM users WHERE username != %s ", (username,))
        options = [row[0] for row in c.fetchall()]


        c.execute("SELECT created_by FROM users WHERE username = %s",(username,))
        session["created_by"] = c.fetchone()[0]

        c.execute("SELECT * FROM messages WHERE `to` = %s and seen = %s ", (username, "no"))
        all_unread_messages = len(c.fetchall())

        user_unread = None
        if all_unread_messages > 0:
            c.execute("SELECT `from` FROM messages WHERE `to` = %s and seen = %s", (username, "no"))
            all_users_with_unread_messages = [row[0] for row in c.fetchall()]

            user_unread = all_users_with_unread_messages





        return render_template("index3.html", level=session["level"], username=session["username"], company=session["company"], created_by=session["created_by"], chat_partners=chat_partners, options=options, recipient=recipient, unread_messages=all_unread_messages,all_users_with_unread_messages=user_unread)
    else: return redirect(url_for("index"))


@app.route("/get_messages/<chat_partner>")
def get_messages(chat_partner):
    username = session.get("username")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password1298!",
        database="tickets"
    )
    c = conn.cursor()

    # Fetch messages sorted by date, then time
    c.execute("""
        SELECT `from`, `to`, content, timestamp, date
        FROM messages
        WHERE (`from` = %s AND `to` = %s) OR (`from` = %s AND `to` = %s)
        ORDER BY date ASC, timestamp ASC
    """, (username, chat_partner, chat_partner, username))

    messages = [{"from_user": msg[0], "to": msg[1], "content": msg[2], "timestamp": msg[3], "date": msg[4]} for msg in c.fetchall()]

    conn.close()
    return jsonify(messages)


@app.route("/send_message", methods=["POST"])
def send_message():
    message_content = request.form.get("message")
    recipient = request.form.get("recipient")
    username = session.get("username")

    print(recipient)

    if message_content and recipient:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Password1298!",
            database="tickets"
        )
        c = conn.cursor()

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
        time_str = now.strftime("%H:%M")  # Format: HH:MM

        c.execute("INSERT INTO messages (`from`, `to`, content, timestamp, date, seen) VALUES (%s, %s, %s, %s, %s, %s)",
                  (username, recipient, message_content, f" {time_str}", date_str, "no"))


        conn.commit()






        # Return the sent message as JSON
        return jsonify({
            'content': message_content,
            'timestamp': f" {time_str}"
        })


@app.route('/change-message-status', methods = ["POST"])
def change_message_status():

    req = request.get_json()

    username = session.get("username")



    conn = mysql.connector.connect(
        host= "localhost",
        user= "root",
        password = "Password1298!",
        database = "tickets"
    )

    c = conn.cursor()

    c.execute("UPDATE messages SET seen = %s WHERE `from` = %s AND `to` = %s", ("yes", req, username))

    conn.commit()

    res = make_response(jsonify({"message": "JSON received"}), 200)

    return res


@app.route('/run-function', methods=['POST'])
def run_function():
    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    customer_name = request.form['customer_name']
    c.execute("DELETE FROM customers_list WHERE customer_name = %s", (customer_name,))
    conn.commit()
    c.execute("SELECT * FROM customers_list")
    all_customers = c.fetchall()
    c.execute("SELECT * FROM Allocated_to")
    all_supporters = c.fetchall()
    c.execute("SELECT * FROM equipment_list WHERE equipment != 'Other' ")
    all_equipments = c.fetchall()
    conn.close()

    return render_template("index4.html", all_customers=all_customers, all_supporters=all_supporters,
                           all_equipments=all_equipments)



@app.route('/run-one', methods=['POST'])
def run_function2():
    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    supporter_name = request.form['supporter_name']
    c.execute("DELETE FROM Allocated_to WHERE supporter = %s", (supporter_name,))
    conn.commit()
    c.execute("SELECT * FROM customers_list")
    all_customers = c.fetchall()
    c.execute("SELECT * FROM Allocated_to")
    all_supporters = c.fetchall()
    c.execute("SELECT * FROM equipment_list WHERE equipment != 'Other' ")
    all_equipments = c.fetchall()
    conn.close()

    return render_template("index4.html", all_customers=all_customers, all_supporters=all_supporters,
                           all_equipments=all_equipments)



@app.route('/run-two', methods=['POST'])
def run_function3():
    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    equipment_name = request.form['equipment_name']
    c.execute("DELETE FROM equipment_list WHERE equipment = %s", (equipment_name,))
    conn.commit()
    c.execute("SELECT * FROM customers_list")
    all_customers = c.fetchall()
    c.execute("SELECT * FROM Allocated_to")
    all_supporters = c.fetchall()
    c.execute("SELECT * FROM equipment_list WHERE equipment != 'Other' ")
    all_equipments = c.fetchall()
    conn.close()

    return render_template("index4.html", all_customers=all_customers, all_supporters=all_supporters, all_equipments=all_equipments)



@app.route('/edit-lists')
def edit_lists():
    username = session.get("username")
    if username != None:
        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()
        c.execute("SELECT * FROM customers_list")
        all_customers = c.fetchall()
        c.execute("SELECT * FROM Allocated_to")
        all_supporters = c.fetchall()
        c.execute("SELECT * FROM equipment_list WHERE equipment != 'Other' ")
        all_equipments = c.fetchall()
        username_input = request.form.get("user_input")

        conn.close()
        return render_template('index4.html', all_customers=all_customers, all_supporters=all_supporters, all_equipments=all_equipments)

    else: return redirect(url_for("index"))



@app.route('/add-customer', methods=['POST'])
def add_customer():
    customer_name = request.form['customer_name']

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute("INSERT INTO customers_list (customer_name) VALUES (%s)", (customer_name,))
    conn.commit()


    c.execute("SELECT * FROM customers_list")
    all_customers = c.fetchall()

    conn.close()

    return jsonify(all_customers)

def get_last_message_from_db():
    username = session.get("username")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password1298!",
        database="tickets"
    )
    c = conn.cursor()

    # Select all distinct chat partners
    c.execute("""
        SELECT partner FROM (
            SELECT DISTINCT `from` AS partner FROM messages WHERE `to` = %s
            UNION
            SELECT DISTINCT `to` AS partner FROM messages WHERE `from` = %s
        ) AS all_partners
        ORDER BY partner DESC
    """, (username, username))

    chat_partners = [row[0] for row in c.fetchall()]
    print("Chat partners:", chat_partners)

    all_last_messages = {}

    for partner in chat_partners:
        c.execute("""
            SELECT content
            FROM messages
            WHERE (`from` = %s AND `to` = %s) OR (`from` = %s AND `to` = %s)
            ORDER BY date DESC, timestamp DESC
            LIMIT 1
        """, (username, partner, partner, username))

        last_message = c.fetchall()
        all_last_messages[partner] = last_message[0][0] if last_message else ""  # Store each partner's last message

    conn.close()

    return all_last_messages  # Return the dictionary of last messages for all partners
    # You can now return all_last_messages or use it as needed

@app.route("/get_last_message")
def get_all_last_messages():
    all_last_messages = get_last_message_from_db()  # Get all last messages
    return jsonify({"last_messages": all_last_messages})

@app.route('/add-supporter', methods=['POST'])
def add_supporter():
    supporter_name = request.form['supporter_name']

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute("INSERT INTO Allocated_to (supporter) VALUES (%s)", (supporter_name,))
    conn.commit()


    c.execute("SELECT * FROM Allocated_to")
    all_supporters = c.fetchall()

    conn.close()

    return jsonify(all_supporters)

@app.route("/get_last_message/<partner>")
def get_last_message(partner):
    username = session.get("username")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password1298!",
        database="tickets"
    )
    c = conn.cursor()

    c.execute("""
        SELECT content
        FROM messages
        WHERE (`from` = %s AND `to` = %s) OR (`from` = %s AND `to` = %s)
        ORDER BY date DESC, timestamp DESC
        LIMIT 1
    """, (username, partner, partner, username))

    last_message = c.fetchone()
    conn.close()

    return jsonify({"last_message": last_message[0] if last_message else ""})


@app.route('/add-equipment', methods=['POST'])
def add_equipment():
    equipment_name = request.form['equipment_name']

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute("INSERT INTO equipment_list (equipment) VALUES (%s)", (equipment_name,))
    conn.commit()


    c.execute("SELECT * FROM equipment_list WHERE equipment != 'Other' ")

    all_equipment = c.fetchall()


    conn.close()

    return jsonify(all_equipment)



@app.route('/add-ticket')
def add_ticket():
    level = session.get("level")
    if level != None:
        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()
        c.execute("SELECT * FROM customers_list")
        all_customers = c.fetchall()
        c.execute("SELECT * FROM Allocated_to")
        all_supporters = c.fetchall()

        c.execute("SELECT * FROM equipment_list ORDER BY CASE WHEN equipment = 'Other' THEN 1 ELSE 0 END")
        all_equipments = c.fetchall()
        conn.close()






        if level == 'Admin':
            return render_template("index1.html", all_customers=all_customers, all_supporters=all_supporters, all_equipments=all_equipments, level=level)

        else: return render_template("index1ForCustomer.html", all_customers=all_customers, all_supporters=all_supporters, all_equipments=all_equipments, level=level)



    else: return redirect(url_for("index"))


@app.route('/search', methods=['GET', 'POST'])
def search():
    level = session.get("level")

    if level != None:

        username = session.get("username")
        company_name = session.get("company")

        customer = f"{username}  [{company_name}]"

        user_search = request.form.get('thisone')

        if user_search == "":
            return redirect(url_for("show_tickets"))

        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()
        c.execute(
            f"SELECT id, severity, customer, equipment, description, allocated_to, status, date FROM ticketCreationNEW1 WHERE id LIKE {user_search}")

        tickets = c.fetchall()
        conn.close()

        # Retrieve ticket data (assuming get_tickets() is implemented elsewhere)
        ticket_data = tickets
        amount_tickets = len(ticket_data)

        conn = mysql.connector.connect(
            host="localhost",  # or "127.0.0.1"
            user="root",  # Your MySQL username
            password="Password1298!",  # Your MySQL password
            database="tickets"  # Your MySQL database name
        )
        c = conn.cursor()

        # Get all ticket IDs from the database
        ticket_ids = [ticket[0] for ticket in tickets]

        # Prepare a list to store the amount_valid_notes for each ticket
        ticket_notes_data = []

        # Loop over the tickets and their corresponding ticket_id from ticket_ids
        for i, ticket in enumerate(ticket_data):
            # Get the corresponding ticket_id (from result_string)
            if i < len(ticket_ids):
                ticket_id = ticket_ids[i]
            else:
                ticket_id = None  # If there are more tickets than ticket_ids, stop processing

            if ticket_id:

                conn = mysql.connector.connect(
                    host="localhost",  # or "127.0.0.1"
                    user="root",  # Your MySQL username
                    password="Password1298!",  # Your MySQL password
                    database="tickets"  # Your MySQL database name
                )
                c = conn.cursor()
                c.execute("SELECT note FROM notes WHERE id = %s", (ticket_id,))
                every_note = c.fetchall()
                conn.close()
                global amount_valid_notes

                # Process the notes if available
                if every_note:
                    valid_notes = [note for note in every_note if
                                   note is not None and not isinstance(note, (int, float))]
                    amount_valid_notes = f"{len(valid_notes)}"
                else:
                    amount_valid_notes = 0
            else:
                amount_valid_notes = 0

            # Store ticket ID and amount_valid_notes for each ticket
            ticket_notes_data.append({
                'ticket': ticket,
                'ticket_id': ticket_id,
                'amount_valid_notes': amount_valid_notes
            })

            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Password1298!",
                database="tickets"
            )
            c = conn.cursor()

            c.execute("SELECT * FROM allocated_to")
            supporters = c.fetchall()

        # Render the template with the necessary variables
        if level == 'Admin':

            # Render the template with the necessary variables
            return render_template("index2.html", ticket_notes_data=ticket_notes_data, level=level,
                                   username=username,
                                   full_name=customer, supporters=supporters)

        if level == 'Customer':
            return render_template("index2ForCustomer.html", ticket_notes_data=ticket_notes_data, level=level,
                                   username=username, full_name=customer)


        if level == 'Supporter': return render_template("index2ForSupporter.html", ticket_notes_data=ticket_notes_data, level=level,
                                   username=username, full_name=customer)


    else:
        return redirect(url_for("index"))








    # Fetch ticket IDs for notes (same filtering as above)


@app.route('/logout', methods = ['POST'])
def logout():

    session.clear()
    return redirect(url_for("index"))


@app.route("/getting_new", methods=["POST"])
def getting_new():
    username_input2 = session.get("username")
    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()

    selected_option = request.form.get("option")

    if selected_option:
        # Add selected user to chat_partners (if they aren't already there)
        c.execute("""
            SELECT DISTINCT `from` 
            FROM messages 
            WHERE `to` = %s
            UNION
            SELECT DISTINCT `to` 
            FROM messages 
            WHERE `from` = %s
            ORDER BY `from` DESC
        """, (username_input2, username_input2))

        chat_partners = [row[0] for row in c.fetchall()]

        if selected_option not in chat_partners:
            # Add the new chat partner
            chat_partners.append(selected_option)

            # Optionally, you could store this in the database or session if necessary
            # For example: update the session or database to reflect the new partner

        # Re-fetch the updated list of users
        c.execute("SELECT username FROM users WHERE username != %s", (username_input2,))
        options = [row[0] for row in c.fetchall()]

        conn.close()

        # Return the selected user and updated chat partners
        return jsonify({"success": True, "selected_user": selected_option, "chat_partners": chat_partners})

    return jsonify({"success": False, "error": "No user selected"})


@app.route('/accounts_management')
def accounts_management():
    level = session.get("level")
    username_current = session.get("username")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password1298!",
        database="tickets"
    )
    c = conn.cursor()

    # Fetch usernames and their respective company names
    c.execute("""
        SELECT username, company_name, level
        FROM users 
        WHERE username != %s
        ORDER BY user_id ASC
    """, (username_current,))

    accounts = c.fetchall()  # List of tuples: [(username1, company_name1), (username2, company_name2), ...]

    conn.close()

    return render_template("index5.html", level=level, accounts=accounts)


@app.route('/add_account', methods=["POST"])
def add_account():
    username = request.form.get("username")
    company = request.form.get("company")
    password = request.form.get("password")
    level2 = request.form.get("level")
    gmail = request.form.get("mail")


    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())




    user_username = session.get("username")



    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password1298!",
        database="tickets"
    )
    c = conn.cursor()

    c.execute("INSERT INTO users(username, password, level, company_name, created_by, gmail) VALUES(%s,%s,%s,%s,%s,%s)  ", (username, hashed_pw, level2, company, user_username,gmail ))

    if level2 == "Supporter": c.execute("INSERT INTO Allocated_to(supporter) VALUES(%s)",(username,))


    conn.commit()







    return redirect("accounts_management")

@app.route("/fetching-unread", methods =["POST"])
def fetching_unread():

    username_input2 = request.form.get("username2")

    conn = mysql.connector.connect(
        host="localhost",  # or "127.0.0.1"
        user="root",  # Your MySQL username
        password="Password1298!",  # Your MySQL password
        database="tickets"  # Your MySQL database name
    )
    c = conn.cursor()
    c.execute("SELECT level FROM users WHERE username = %s ", (username_input2,))
    session["level"] = c.fetchone()[0]

    c.execute("SELECT company_name FROM users WHERE username = %s ", (username_input2,))
    session["company"] = c.fetchone()[0]

    session["full_name"] = f"{session["username"]} [{session["company"]}]"

    c.execute("""
                        SELECT partner
                        FROM (
                            SELECT 
                                CASE 
                                    WHEN `from` = %s THEN `to`
                                    ELSE `from`
                                END AS partner,
                                MAX(STR_TO_DATE(CONCAT(date, ' ', timestamp), '%Y-%m-%d %H:%i')) AS latest_message_time
                            FROM messages
                            WHERE `from` = %s OR `to` = %s
                            GROUP BY partner
                        ) AS conversation_partners
                        ORDER BY latest_message_time DESC
                    """, (username_input2, username_input2, username_input2))

    chat_partners = [row[0] for row in c.fetchall()]


    c.execute("SELECT username FROM users WHERE username != %s ", (username_input2,))
    options = [row[0] for row in c.fetchall()]
    session["users_beside_own"] = options


    c.execute("SELECT created_by FROM users WHERE username = %s", (username_input2,))
    session["created_by"] = c.fetchone()[0]

    c.execute("SELECT * FROM messages WHERE `to` = %s and seen = %s ", (username_input2, "no"))
    all_unread_messages = len(c.fetchall())



    user_unread = None
    if all_unread_messages > 0:
        c.execute("SELECT `from` FROM messages WHERE `to` = %s and seen = %s", (username_input2, "no"))
        all_users_with_unread_messages = [row[0] for row in c.fetchall()]

        user_unread = all_users_with_unread_messages




    conn.close()

    if username_input2 != "":
        return render_template("index3.html", created_by=session["created_by"], level=session["level"],
                               username=session["username"], company=session["company"], chat_partners=chat_partners,
                               options=options, unread_messages=all_unread_messages,all_users_with_unread_messages=user_unread)


if __name__ == "__main__":
    app.run(debug=True, port=5002)