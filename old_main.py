# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import tkinter as tk
from tkinter import ttk
import os.path
import datetime

import numpy as np
from langchain_community.llms import Ollama
from openai import OpenAI

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]
default_font_size = 12
model_name = "llama3"
openai_model_name = "gpt-3.5-turbo-0125"


def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    return dot_product / (norm_a * norm_b)


def openai_read_api_key(filepath="credentials/openai.key"):
    """Read and return the API key from a specified file."""
    try:
        with open(filepath, "r") as file:
            api_key = file.read().strip()  # Read the key and strip any extra whitespace
        return api_key
    except FileNotFoundError:
        print("API key file not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


class TaskTable:
    def __init__(self, root, data):
        """ data will look like this
        data [{'title': 'title a', 'update': datetime_string},...] """
        self.frame = tk.LabelFrame(root, text="Tasks")  # Create a new frame to hold the entries
        self.frame.pack(
            fill=tk.BOTH, expand=True
        )  # Pack the frame with both x and y directions

        for i in range(len(data)):
            row_frame = tk.Frame(self.frame)  # Create a new frame for each row
            row_frame.pack(fill=tk.X)  # Pack the row frame horizontally
            for j in range(2):
                self.e = tk.Entry(
                    row_frame, width=20, fg="blue", font=("Arial", 16, "bold")
                )
                self.e.grid(row=i, column=j)
                if j == 0:
                    self.e.insert(tk.END, data[i]["title"])
                elif j == 1:
                    self.e.insert(tk.END, data[i]["updated"])


class GoogleTasks:
    def __init__(self):
        self.creds = None
        self.service = None
        self.current_font_size = default_font_size
        # Load the LLM
        self.ollama = Ollama(model=model_name)
        openai_api_key = openai_read_api_key()
        if openai_api_key:
            self.openai = OpenAI(api_key=openai_api_key)
        else:
            self.openai = None
        print("LLM Loaded")
        # Initialize the Tkinter GUI components
        self.root = tk.Tk()
        self.root.title("Xbitodowin | Google Tasks")
        self.root.resizable(True, True)
        self.root.geometry(self.get_default_geometry())
        # Initialize font buttons
        self.setup_font_frame()

        # Create a frame to hold the task listbox and scrollbars
        self.task_frame = tk.Frame(self.root)
        self.task_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize the task listbox and scrollbars
        self.task_listbox = ttk.Combobox(self.task_frame, width=60, height=15)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Create a button to load tasks
        self.load_tasks_button = tk.Button(
            self.task_frame,
            text="Load Tasks",
            command=self.load_tasks,
        )
        self.load_tasks_button.pack(side=tk.LEFT)

        # Create horizontal and vertical scrollbars
        # Initialize the task listbox scrollbars
        self.scrollbar_x = tk.Scrollbar(self.task_frame, orient=tk.HORIZONTAL)
        self.scrollbar_y = tk.Scrollbar(self.task_frame, orient=tk.VERTICAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a button to evaluate duplicate tasks
        self.duplicate_button = tk.Button(
            self.font_frame,
            text="Evaluate Duplicate Tasks",
            command=self.evaluate_duplicate_tasks,
        )
        self.duplicate_button.pack(side=tk.LEFT)

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about_popup)
        menubar.add_cascade(label="Help", menu=about_menu)

    def main(self):
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        self.service = build("tasks", "v1", credentials=self.creds)

        self.update_font_size()

        self.get_task_lists()

        self.root.bind("<<ListboxSelect>>", lambda event: self.load_tasks(event))
        self.root.mainloop()

    def setup_font_frame(self):
        # Create a frame to hold the font size controls
        self.font_frame = tk.Frame(self.root)
        self.font_frame.pack(fill=tk.X)

        # Initialize the font size buttons
        self.increase_button = tk.Button(
            self.font_frame,
            text="Increase Font Size",
            command=self.increase_font_size,
        )
        self.increase_button.pack(side=tk.LEFT)

        self.decrease_button = tk.Button(
            self.font_frame,
            text="Decrease Font Size",
            command=self.decrease_font_size,
        )
        self.decrease_button.pack(side=tk.LEFT)

    def get_task_lists(self):
        try:
            results = self.service.tasklists().list(maxResults=10).execute()
            items = results.get("items", [])
            if not items:
                print("No task lists found.")
            task_list_values = []
            for item in items:
                task_list_values.append(f"{item['title']} ({item['id']})")
            self.task_listbox["values"] = task_list_values
        except Exception as e:
            print("An error occurred: " + str(e))

    def load_tasks(self):
        try:
            selected_item = self.task_listbox.get()
            if selected_item:
                for item in (
                    self.service.tasklists().list(maxResults=10).execute()["items"]
                ):
                    if f"{item['title']} ({item['id']})" == selected_item:
                        tasks_response = (
                            self.service.tasks()
                            .list(tasklist=item["id"], maxResults=100)
                            .execute()
                        )
                        tasks_list = []
                        for task in tasks_response["items"]:
                            tasks_list.append(
                                {
                                    "title": task["title"],
                                    "updated": datetime.datetime.strptime(
                                        task["updated"], "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ).strftime("%Y-%m-%d %H:%M:%S"),
                                }
                            )
                        t = TaskTable(self.root, tasks_list)
        except Exception as e:
            print("An error occurred: " + str(e))

    def get_all_tasks(self):
        """Retrieve all tasks from all tasklists."""
        all_tasks = []
        try:
            # List all tasklists
            tasklists = self.service.tasklists().list().execute()
            # Iterate over each tasklist and collect tasks
            for tasklist in tasklists.get("items", []):
                tasks = self.service.tasks().list(tasklist=tasklist["id"]).execute()
                for task in tasks.get("items", []):
                    all_tasks.append(
                        {
                            "title": task["title"],
                            "id": task["id"],
                            "updated": task["updated"],
                        }
                    )
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        return all_tasks

    def get_default_geometry(self):
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the window size (35% of the screen)
        window_width = int(screen_width * 0.35)
        window_height = int(screen_height * 0.35)

        # Center the window on the screen
        x_pos = int((screen_width - window_width) / 2)
        y_pos = int((screen_height - window_height) / 2)
        return f"{window_width}x{window_height}+{x_pos}+{y_pos}"

    def show_about_popup(self):
        about_popup = tk.Toplevel(self.root)
        about_popup.title("About")
        label = tk.Label(
            about_popup, text="Author: Fernando Gutierrez with the help of Llama3"
        )
        label.pack()

    def update_font_size(self, widget=None):
        if widget is None:
            widget = self.root
        for w in widget.winfo_children():
            if (
                isinstance(w, tk.Text)
                or isinstance(w, tk.Label)
                or isinstance(w, tk.Listbox)
            ):
                print(f"Updating font size of {w} to {self.current_font_size}")
                w.config(font=f"Helvetica {self.current_font_size}")
            else:
                self.update_font_size(w)

    def increase_font_size(self):
        self.current_font_size += 2
        self.update_font_size()

    def decrease_font_size(self):
        if self.current_font_size > 6:
            self.current_font_size -= 2
            self.update_font_size()

    def evaluate_duplicate_tasks(self):

        try:
            # Assuming you have a function to get all tasks:
            tasks = self.get_all_tasks()
            response = self.openai.chat.completions.create(
                model=openai_model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You will be provided with a list of tasks from a todo system, and your task "
                        "is to find potentially duplicate tasks and report them.",
                    },
                    {
                        "role": "user",
                        "content": "%s" % tasks,
                    },
                ],
            )
            print(response)
        except Exception as e:
            print("An error occurred while evaluating duplicates:", str(e))


if __name__ == "__main__":
    app = GoogleTasks()
    app.main()
