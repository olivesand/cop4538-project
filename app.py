from flask import Flask, render_template, request, redirect, url_for
import os
import time

app = Flask(__name__)

app.config['FLASK_TITLE'] = ""

#create a node class with data and next attributes
class Node:
    def __init__(self, name, email, tags=["All Contacts"], priority=99):
        self.name = name
        self.email = email
        self.tags = tags
        self.priority = priority
        self.next = None

#create a head class for linked list of type Node
class LinkedList(Node):
    def __init__(self):
        self.head = None

    #append a new node to the end of the linked list
    def append(self, name, email, tags=["All Contacts"], priority=99):
        new_node = Node(name, email, tags, priority)
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

#min heap for contact priority
class MinHeap:
    def __init__(self):
        self.heap = []

    # function to insert a new node into the heap
    def insert(self, contact):
        self.heap.append(contact)
        self._heapify_up(len(self.heap) - 1)

    # function to maintain the heap property after insertion
    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        if index > 0 and self.heap[index].priority < self.heap[parent_index].priority:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            self._heapify_up(parent_index)

    def _heapify_down(self, index):
        smallest = index
        left_child = 2 * index + 1
        right_child = 2 * index + 2

        if left_child < len(self.heap) and self.heap[left_child].priority < self.heap[smallest].priority:
            smallest = left_child
        if right_child < len(self.heap) and self.heap[right_child].priority < self.heap[smallest].priority:
            smallest = right_child
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def remove_min(self):
        if not self.heap:
            return None
        min_node = self.heap[0]
        last_node = self.heap.pop()
        if self.heap:
            self.heap[0] = last_node
            self._heapify_down(0)
        return min_node
    
    def get_top_10(self):
        top_10 = MinHeap()
        temp_heap = MinHeap()
        temp_heap.heap = self.heap.copy()
        i = 0
        while i < 10 and len(temp_heap.heap) != 0:
            important = temp_heap.remove_min()
            top_10.insert(important)
            i += 1
        return top_10.heap
    

    def remove_contact(self, name):
        for i in range(len(self.heap)):
            if self.heap[i].name == name:
                last_node = self.heap.pop()
                if i < len(self.heap):
                    self.heap[i] = last_node
                    self._heapify_down(i)
                return True
        return False

#trees for contact category storage
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.left = None
        self.right = None

    def add_child(self, child_node):
        if not self.left:
            self.left = child_node
        elif not self.right:
            self.right = child_node
        self.children.append(child_node)

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = TreeNode(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, currentNode, value):
        if currentNode is None:
            return TreeNode(value)
        if value < currentNode.value:
            currentNode.left = self._insert_recursive(currentNode.left, value)
        else:
            currentNode.right = self._insert_recursive(currentNode.right, value)
        return currentNode

# --- IN-MEMORY DATA STRUCTURES (Students will modify this area) ---
# contact category tree
root = TreeNode("All Contacts")

work = TreeNode("Work")
tech = TreeNode("Tech")
marketing = TreeNode("Marketing")
eng = TreeNode("Engineering")
prog = TreeNode("Programming")

personal = TreeNode("Personal")
family = TreeNode("Family")
friends = TreeNode("Friends")

root.add_child(personal)
root.add_child(work)

work.add_child(tech)
work.add_child(marketing)

tech.add_child(eng)
tech.add_child(prog)

personal.add_child(family)
personal.add_child(friends)

contact_categories = BinarySearchTree()

contact_categories.insert("Marketing")
contact_categories.insert("Family")
contact_categories.insert("Programming")
contact_categories.insert("Engineering")
contact_categories.insert("Friends")
contact_categories.insert("Personal")
contact_categories.insert("Tech")
contact_categories.insert("Work")
contact_categories.insert("All Contacts")

# Phase 1: A simple Python List to store contacts
contacts = LinkedList()
contacts.append("Alice", "alice@email.com", ["All Contacts", "Work", "Tech", "Engineering"])
contacts.append("Bob", "bob@email.com", ["All Contacts", "Personal", "Friends"])

priority_contacts = MinHeap()
priority_contacts.insert(Node("Alice", "alice@email.com", ["All Contacts", "Work", "Tech", "Engineering"],  priority=99))
priority_contacts.insert(Node("Bob", "bob@email.com", ["All Contacts", "Personal", "Friends"], priority=99))

current_contacts = [{'name' : 'Alice', 'email': 'alice@email.com', 'tags': ['All Contacts', 'Work', 'Tech', 'Engineering'], 'priority' : 99},
                    {'name' : 'Bob', 'email': 'bob@email.com', 'tags': ['All Contacts', 'Personal', 'Friends'], 'priority' : 99}]

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
def find_contact_by_id(test_hash):
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

    exists = find_contact_by_id(name_hash(query))

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
    

@app.route('/search_by_tag')
def search_by_tag():
    tag = request.args.get('tag')
    filtered_contacts = LinkedList()

    if tag == "Favorites":
        for contact in priority_contacts.get_top_10():
            filtered_contacts.append(contact.name, contact.email, contact.tags, contact.priority)
        status = 4
        return render_template('index.html', contacts=filtered_contacts, status=4, title=app.config['FLASK_TITLE'])
    else:
        for contact in contacts:
            if tag in contact.tags:
                filtered_contacts.append(contact.name, contact.email, contact.tags, contact.priority)

        if filtered_contacts.head is not None:
            if tag == "All Contacts":
                status = 0
            else:
                status = 3
            return render_template('index.html', contacts=filtered_contacts, status=status, tag=tag, title=app.config['FLASK_TITLE'])
        else:
            return render_template('index.html', contacts=filtered_contacts, status=2, title=app.config['FLASK_TITLE'])


@app.route('/add', methods=['POST'])
def add_contact():
    """
    Endpoint to add a new contact.
    Students will update this to insert into their Data Structure.
    """
    name = request.form.get('name')
    email = request.form.get('email')
    tag = request.form.get('tag')
    priority = int(request.form.get('prio'))

    tags = [root.value]
    
    if tag == "Family" or tag == "Friends":
        tags += [root.children[0].value, tag]
    elif tag == "Engineering" or tag == "Programming" or tag == "Marketing":
        tags += [root.children[1].value]
        if tag != "Marketing":
            tags += [root.children[1].children[0].value, tag]
        else:
            tags += [root.children[1].children[1].value]
    
    
    # Phase 1 Logic: Append to list
    new_contact = Node(name, email, tags, priority)

    contacts.append(name, email, tags, priority)

    priority_contacts.insert(new_contact)

    current_contacts.append({'name': name, 'email': email, 'tags': tags, 'priority': priority})

    contacts_by_hash.append({name_hash(name) : new_contact})

    actions.append('A')

    redo_queue.clear()
    
    return redirect(url_for('index'))


# delete contact route
@app.route('/delete', methods=['POST'])
def delete_contact():
    name = request.form.get('name')
    # Phase 1 Logic: Remove from list
    quick_sort(contacts_by_hash, 0, len(contacts_by_hash) - 1)
    contact_to_delete = find_contact_by_id(name_hash(name))

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

        # Remove from priority heap
        priority_contacts.remove_contact(name)

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
            contact_to_delete = find_contact_by_id(name_hash(added_contact['name']))

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

                # Remove from priority heap
                priority_contacts.remove_contact(added_contact['name'])

                redo_queue.enqueue(('A', added_contact))
        
            
        elif last_action == 'D':
            if deleted_contacts:
                last_deleted = deleted_contacts.pop()
                contacts.append(last_deleted['name'], last_deleted['email'], last_deleted['tags'], last_deleted['priority'])
                current_contacts.append(last_deleted)
                contacts_by_hash.append({name_hash(last_deleted['name']) : Node(last_deleted['name'], last_deleted['email'], last_deleted['tags'], last_deleted['priority'])})
                priority_contacts.insert(Node(last_deleted['name'], last_deleted['email'], last_deleted['tags'], last_deleted['priority']))

                redo_queue.enqueue(('D', last_deleted))
                
    return redirect(url_for('index'))


# redo route
@app.route('/redo', methods=['POST'])
def redo():
    if not redo_queue.is_empty():
        action, contact = redo_queue.dequeue()
        if action == 'A':
            contacts.append(contact['name'], contact['email'], contact['tags'], contact['priority'])
            priority_contacts.insert(Node(contact['name'], contact['email'], contact['tags'], contact['priority']))
            current_contacts.append(contact)
            actions.append('A')
            contacts_by_hash.append({name_hash(contact['name']) : Node(contact['name'], contact['email'], contact['tags'], contact['priority'])})  
        elif action == 'D':
            quick_sort(contacts_by_hash, 0, len(contacts_by_hash) - 1)
            contact_to_delete = find_contact_by_id(name_hash(contact['name']))
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

                # Remove from priority heap
                priority_contacts.remove_contact(contact['name'])

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
