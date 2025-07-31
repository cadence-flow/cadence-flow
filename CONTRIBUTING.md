# Contributing to Cadence Flow

First off, thank you for considering contributing to Cadence Flow! We're excited to have you here. This project is in its early stages, and every contribution, from a small typo fix to a new feature, is incredibly valuable.

This document provides guidelines for contributing to the project.

## How Can I Contribute?

There are many ways to contribute:

*   **Reporting Bugs:** If you find a bug, please open an issue and provide as much detail as possible.
*   **Suggesting Enhancements:** Have an idea for a new feature or an improvement to an existing one? Open an issue to start a discussion.
*   **Writing Documentation:** Great documentation is key. If you find something unclear or think a section is missing, let us know or submit a pull request.
*   **Submitting Pull Requests:** If you want to fix a bug or implement a new feature, we welcome pull requests.

## Setting Up Your Development Environment

To get started with development, you'll need to set up both the Python backend and the SvelteKit frontend.

### Prerequisites
*   Python 3.9+
*   Node.js and npm

### 1. Fork & Clone the Repository

First, fork the repository to your own GitHub account. Then, clone your fork to your local machine:

```bash
git clone https://github.com/YourUsername/cadence-flow.git
cd cadence-flow
```

### 2. Backend Setup (Python)

We recommend using a Python virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install the package in "editable" mode
pip install -e .
```
The `-e` flag is important. It installs the package in a way that allows you to make changes to the source code and have them immediately reflected without needing to reinstall.

### 3. Frontend Setup (SvelteKit)

Navigate to the `frontend` directory and install the necessary npm packages.

```bash
cd frontend
npm install
```

## Running the Project Locally

You will need two terminals running simultaneously.

*   **Terminal 1: Run the Backend**
    From the project root (`cadence-flow/`), run the example script:
    ```bash
    python examples/hello_world.py
    ```
    This will start the Python server on `http://127.0.0.1:8501`.

*   **Terminal 2: Run the Frontend Dev Server**
    From the `frontend/` directory, run the SvelteKit development server:
    ```bash
    npm run dev
    ```
    This will start the frontend server, usually on `http://localhost:5173`.

Now, open your browser and navigate to **`http://localhost:5173`** to see the UI in action. The frontend will connect to the backend server running on port 8501.

## Submitting a Pull Request

1.  Create a new branch for your changes: `git checkout -b feature/my-new-feature` or `git checkout -b fix/bug-fix-description`.
2.  Make your changes and commit them with a clear, descriptive message.
3.  Push your branch to your fork: `git push origin feature/my-new-feature`.
4.  Open a pull request from your fork to the `main` branch of the `cadence-flow/cadence-flow` repository.
5.  In your pull request description, explain the changes you've made and link to any relevant issues.

We'll review your PR as soon as we can. Thank you again for your contribution!