# Let's attempt to load the newly uploaded Excel file to access the user's to-do list.
import pandas as pd

# Load the data from the Excel file
todo_list_new = pd.read_excel("tasks.xlsx")
print(todo_list_new.columns)
# Display the first few rows of the dataframe to understand its structure and contents
print(todo_list_new.head())

print("YES")
