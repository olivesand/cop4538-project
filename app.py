from flask import Flask, render_template, request, redirect, url_for
import os
import time

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

class Queue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def size(self):
        return len(self.items)
    
    def clear(self):
        self.items = []



# --- IN-MEMORY DATA STRUCTURES (Students will modify this area) ---
# Phase 1: A simple Python List to store contacts
contacts = LinkedList()
contacts.append("Alice", "alice@email.com")
contacts.append("Bob", "bob@email.com")


current_contacts = [{'name' : 'Alice', 'email': 'alice@email.com'},
                    {'name' : 'Bob', 'email': 'bob@email.com'}]

deleted_contacts = []
actions = []
redo_queue = Queue()

status = 0

# quick sort functions
# edited partition function to work with list of dicts - allows for sorting by hash value
def partition(arr, low, high):
    pivot = arr[high]
    pivotNum = list(pivot.keys())[0]
    i = low - 1
    for j in range(low, high):
        numCheck = list(arr[j].keys())[0]
        if int(numCheck) <= int(pivotNum): # int() is used here so that the hash values are compared as numbers rather than strings
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
def quick_sort(arr, low, high):
    if low < high:

        pi = partition(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)
    return arr



# hash function that takes a name and returns a hash value
# (hopefully) guarantees no duplicates UNLESS there are two contacts w the same name
def name_hash(name):
    hash = ""
    for char in name:
        num = ord(char.lower()) - 96
        if num < 10:
            hash = hash + "0" + str(num)
        else:
            hash = hash + str(num)

    return hash


#Searches for a contact by its hash using binary search
#Returns the contact if found, else None
def find_contact_by_id(name):
    test_hash = name_hash(name)
    left, right = 0, len(contacts_by_hash) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        mid_hash = list(contacts_by_hash[mid].keys())[0]
        
        if mid_hash == test_hash:
            return contacts_by_hash[mid][mid_hash] 
        elif int(mid_hash) < int(test_hash): # because the hashes are sorted by their int values, we need to compare their int values instead of their strings
            left = mid + 1
        else:
            right = mid - 1
            
    return None

contacts_by_hash = []
for contact in contacts:
    contacts_by_hash.append({name_hash(contact.name) : contact})



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
    start_time = time.time()
    filtered_contacts = LinkedList()
    quick_sort(contacts_by_hash, 0, len(contacts_by_hash) - 1)

    exists = find_contact_by_id(query)

    end_time = time.time()
    time_elapsed = end_time - start_time
    print(f"Search for '{query}' took {time_elapsed:.10f} seconds")
    
    if exists:
        status = 1
        filtered_contacts.append(exists.name, exists.email)
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

    current_contacts.append({'name': name, 'email': email})

    contacts_by_hash.append({name_hash(name) : Node(name, email)})

    actions.append('A')

    redo_queue.clear()
    
    return redirect(url_for('index'))


# delete contact route
@app.route('/delete', methods=['POST'])
def delete_contact():
    name = request.form.get('name')
    # Phase 1 Logic: Remove from list
    quick_sort(contacts_by_hash, 0, len(contacts_by_hash) - 1)
    contact_to_delete = find_contact_by_id(name)

    if contact_to_delete:
        # Remove from linked list
        current = contacts.head
        prev = None
        while current:
            if current.name.lower() == name.lower():
                if prev:
                    prev.next = current.next
                else:
                    contacts.head = current.next
                break
            prev = current
            current = current.next
        
        # Remove from current_contacts
        for contact in current_contacts:
            if contact['name'].lower() == name.lower():
                current_contacts.remove(contact)
                deleted_contacts.append(contact)
                break

        # Remove from hash table
        i = 0
        for contact in contacts_by_hash:
            if name_hash(name) in contact:
                del contacts_by_hash[i]
                break
            i += 1

    actions.append('D')
    redo_queue.clear()

    return render_template('index.html', contacts=contacts, status=status, title=app.config['FLASK_TITLE'])
    


# undo route
@app.route('/undo', methods=['POST'])
def undo():
    if actions:
        last_action = actions.pop()
        if last_action == 'A':
            added_contact = current_contacts.pop()
            quick_sort(contacts_by_hash, 0, len(contacts_by_hash) - 1)
            contact_to_delete = find_contact_by_id(added_contact['name'])

            if contact_to_delete:
                # Remove from linked list
                current = contacts.head
                prev = None 
                while current:
                    if current.name.lower() == added_contact['name'].lower():
                        if prev:
                            prev.next = current.next
                        else:
                            contacts.head = current.next
                        break
                    prev = current
                    current = current.next

                # Remove from hash table
                i = 0
                for contact in contacts_by_hash:
                    if name_hash(added_contact['name']) in contact:
                        del contacts_by_hash[i]
                        break
                    i += 1

                redo_queue.enqueue(('A', added_contact))
        
            
        elif last_action == 'D':
            if deleted_contacts:
                last_deleted = deleted_contacts.pop()
                contacts.append(last_deleted['name'], last_deleted['email'])
                current_contacts.append(last_deleted)
                contacts_by_hash.append({name_hash(last_deleted['name']) : Node(last_deleted['name'], last_deleted['email'])})

                redo_queue.enqueue(('D', last_deleted))
                
    return redirect(url_for('index'))


# redo route
@app.route('/redo', methods=['POST'])
def redo():
    if not redo_queue.is_empty():
        action, contact = redo_queue.dequeue()
        if action == 'A':
            contacts.append(contact['name'], contact['email'])
            current_contacts.append(contact)
            actions.append('A')
            contacts_by_hash.append({name_hash(contact['name']) : Node(contact['name'], contact['email'])})  
        elif action == 'D':
            quick_sort(contacts_by_hash, 0, len(contacts_by_hash) - 1)
            contact_to_delete = find_contact_by_id(contact['name'])
            if contact_to_delete:
                # Remove from linked list
                current = contacts.head
                prev = None
                while current:
                    if current.name.lower() == contact['name'].lower():
                        if prev:
                            prev.next = current.next
                        else:
                            contacts.head = current.next
                        break
                    prev = current
                    current = current.next

                # Remove from current_contacts
                for c in current_contacts:
                    if c['name'].lower() == contact['name'].lower():
                        current_contacts.remove(c)
                        deleted_contacts.append(c)
                        break

                # Remove from hash table
                i = 0
                for c in contacts_by_hash:
                    if name_hash(contact['name']) in c:
                        del contacts_by_hash[i]
                        break
                    i += 1

                actions.append('D')

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
