from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

app.config['FLASK_TITLE'] = ""

#create a node class with data and next attributes
class Node:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.next = None

#create a head class for linked list of type Node
class LinkedList(Node):
    def __init__(self):
        self.head = None

    #append a new node to the end of the linked list
    def append(self, name, email):
        new_node = Node(name, email)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node

    #iterate through the linked list
    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next



# --- IN-MEMORY DATA STRUCTURES (Students will modify this area) ---
# Phase 1: A simple Python List to store contacts
contacts = LinkedList()
contacts.append("Alice", "alice@email.com")
contacts.append("Bob", "bob@email.com")

status = 0

#Searches for a contact by name, ignoring case
#Returns the contact if found, else None
def find_contact_by_name(name):
    for contact in contacts:
        if contact.name.lower() == name.lower():
            return contact
    return None

# --- ROUTES ---

@app.route('/')
def index():
    """
    Displays the main page.
    Eventually, students will pass their Linked List or Tree data here.
    """
    # change the flask html title to my name
    app.config['FLASK_TITLE'] = "Olivia Sanchez "
    return render_template('index.html', 
                         contacts=contacts, 
                         status=status,
                         title=app.config['FLASK_TITLE'])


@app.route('/search')
def search_contact():
    query = request.args.get('query')
    filtered_contacts = LinkedList()
    exists = find_contact_by_name(query)

    #if there are multiple contacts with the same name, this displays all of them
    for contact in contacts:
        if contact.name.lower() == query.lower():
            filtered_contacts.append(contact.name, contact.email)
    
    if exists:
        status = 1
        return render_template('index.html', contacts=filtered_contacts, status=status, title=app.config['FLASK_TITLE'])
    else:
        status = 2
        return render_template('index.html', contacts=filtered_contacts, status=status, title=app.config['FLASK_TITLE'])
    


@app.route('/add', methods=['POST'])
def add_contact():
    """
    Endpoint to add a new contact.
    Students will update this to insert into their Data Structure.
    """
    name = request.form.get('name')
    email = request.form.get('email')
    
    # Phase 1 Logic: Append to list
    contacts.append(name, email)
    
    return redirect(url_for('index'))

# --- DATABASE CONNECTIVITY (For later phases) ---
# Placeholders for students to fill in during Sessions 5 and 27
def get_postgres_connection():
    pass

def get_mssql_connection():
    pass

if __name__ == '__main__':
    # Run the Flask app on port 5000, accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
