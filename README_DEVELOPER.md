# Terminal-to-Gemini Bridge

Control your system terminal using natural language powered by Google Gemini. This tool bridges the gap between conversational AI and your local shell, allowing you to execute commands, manage files, and automate tasks using plain English.

## Features

*   **Natural Language Command Execution**: Translate English requests into shell commands (e.g., "Find all large files in my Downloads folder").
*   **Safety First**: Built-in risk classification for generated commands (Red/Yellow/Green) to prevent accidental data loss.
*   **GUI Interface**: User-friendly graphical interface built with Tkinter.
    *   **File Editor**: Integrated editor with diff viewing to modify files.
    *   **Project Explorer**: Visual file tree to navigate your working directory.
    *   **Live Output**: Real-time streaming of command stdout/stderr.
*   **Cross-Platform**: Works on macOS, Windows, and Linux.
*   **Auto-Dependency Management**: Automatically installs required Python packages on the first run.

## Installation

### Prerequisites
*   **Python 3.8** or higher installed.

### Setup

1.  **Get an API Key**:
    *   Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Create a new API Key.

2.  **Run the Application**:
    *   **Windows**: Double-click `Launch_Windows.bat`.
    *   **macOS**: Double-click `Launch_macOS.command`.
    *   **Linux**: Run `./Launch_Linux.sh`.

    *Alternatively, you can run the python script directly:*
    ```bash
    python gui_bridge.py
    ```

3.  **Enter Key**:
    *   On the first run, the app will ask for your API Key. Enter it in the GUI and click "Apply API Key". The key will be saved to a `.env` file for future use.

## Usage

1.  **Enter a Request**: Type your request in the bottom text area (e.g., "List all python files in the src directory").
2.  **Review Commands**: The AI will propose commands. In the GUI, you can see the proposed commands and their risk level.
3.  **Execution**: The commands are executed in the integrated terminal.
4.  **Feedback**: The output is fed back to the AI, allowing for multi-step tasks (e.g., "Read the error log and fix the syntax error in main.py").

## Architecture "Dissection"

For developers interested in how this works:

### 1. `gemini_terminal_bridge.py` (The Backend)
*   **Core Logic**: This module handles the communication with the Gemini API.
*   **Protocol**: It enforces a STRICT JSON protocol (`SYSTEM_PROMPT`) to ensure Gemini returns machine-readable commands, not just chat.
*   **Session Management**: Maintains a `GeminiBridgeSession` that keeps a transcript of executed commands to provide context for subsequent turns.
*   **Execution**: Uses `subprocess` to run shell commands and capture `stdout`/`stderr`.

### 2. `gui_bridge.py` (The Frontend)
*   **Tkinter GUI**: A robust wrapper around the backend.
*   **Threading**: usage of `threading` to keep the UI responsive while waiting for API calls or long-running shell commands.
*   **Stream Handling**: Uses a `queue.Queue` and `TeeWriter` to capture stdout in real-time and display it in the "Live Summary Stream" pane.
*   **File System Watcher**: Periodically polls the working directory (`_poll_workdir_changes`) to update the file tree automatically.
*   **Safety Checks**: `classify_command_risk` analyzes strings for dangerous patterns (like `rm -rf`) and color-codes them in the UI.

### 3. Dependencies
*   `google-generativeai`: Official Gemini SDK (optional usage in this bridge, currently using direct HTTP or SDK).
*   `requests`: For HTTP calls to the Gemini API.
*   `python-dotenv`: For loading the API key securely from `.env`.

## Troubleshooting

*   **API Key Errors**: Ensure you have a valid key from Google AI Studio and it is pasted correctly without extra spaces.
*   **Permission Denied**: On macOS/Linux, you might need to make the launch scripts executable: `chmod +x Launch_macOS.command`.
*   **Dependencies**: If imports fail, the script tries to auto-install them. Ensure you have internet access on the first run.
