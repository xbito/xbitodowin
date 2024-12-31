# Xbitodowin

Xbitodowin is a desktop application for managing Google Tasks. It provides a user-friendly interface to view, search, filter, and manage tasks from multiple Google Task lists. The application also includes features for exporting tasks to various formats and displaying motivational phrases.

## Features

- **Task Management**: View and manage tasks from multiple Google Task lists.
- **Search and Filter**: Search tasks by title and filter tasks by different criteria (e.g., Today, Next Days, Overdue, Recently Completed, All).
- **Task Details**: View and edit task details in a dedicated panel.
- **Export**: Export tasks to CSV, Excel, and Google Sheets.
- **Motivational Phrases**: Display random motivational phrases to keep you inspired.
- **User Profile**: Display user profile information including avatar and name.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/xbitodowin.git
    cd xbitodowin
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up Google API credentials:
    - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
    - Enable the Google Tasks API, Google Sheets API, and Google OAuth2 API.
    - Create OAuth 2.0 credentials and download the `credentials.json` file.
    - Place the `credentials.json` file in the `credentials` directory.

## Usage

1. Run the application:
    ```sh
    python main.py
    ```

2. Log in with your Google account to authorize access to your Google Tasks.

3. Use the sidebar to select a task list and view tasks.

4. Use the search bar to search for tasks by title.

5. Use the filter options to filter tasks by different criteria.

6. View and edit task details in the details panel.

7. Export tasks to CSV, Excel, or Google Sheets using the Export menu.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Developed by Fernando (Xbito) Gutierrez with assistance from multiple AIs: GitHub Copilot, Llama, qwen, gpt, and Gemini.