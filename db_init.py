import sqlite3

# Define the schema for the task lists table
task_lists_table = """
CREATE TABLE task_lists (
    kind TEXT,
    id TEXT PRIMARY KEY,
    etag TEXT,
    title TEXT NOT NULL,
    updated DATETIME,
    selfLink TEXT
);
"""

# Define the schema for the tasks table
tasks_table = """
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    etag TEXT,
    title TEXT NOT NULL,
    updated DATETIME,
    selfLink TEXT,
    parent TEXT,
    position INTEGER,
    notes TEXT,
    status TEXT,
    due DATETIME,
    completed DATETIME,
    deleted INTEGER,
    hidden INTEGER,
    webViewLink TEXT
    task_list_id TEXT REFERENCES task_lists(id),
    FOREIGN KEY (task_list_id) REFERENCES task_lists(id)
);
"""

# Create a connection to the database
conn = sqlite3.connect("tasks.db")

# Create the tables
with conn:
    cursor = conn.cursor()
    cursor.execute(task_lists_table)
    cursor.execute(tasks_table)

# Close the connection
conn.close()
