# GPT CLI Utilities

This project is a collection of GPT scripts that help with software development tasks. The scripts can be run easily with the command-line interface (CLI).

## Setup Instructions

### 1. Create a Virtual Environment

First, create a virtual environment in the project directory. This helps manage dependencies and isolate them from other projects.

For macOS and Linux:

```bash
python3 -m venv venv
```

For Windows:
```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
Activate the virtual environment to start using it.

For macOS and Linux:
```bash
source venv/bin/activate
```

For Windows:
```bash
venv\Scripts\activate
```

### 3. Install Dependencies
Install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

### 4. Add OpenAI Key to .env
Create a .env file in the project directory and add your OpenAI API key. This key will be used by the script to make requests to OpenAI's API.

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run Setup Script
Run the appropriate setup script to add the CLI command gcu to your PATH.

For macOS and Linux:
```bash
./setup.sh
```

For Windows:
```bash
setup.bat
```

## Usage
After completing the setup, you can use the gcu command to invoke the script from anywhere in your terminal.

```bash
gcu [util_name] <arguments>
```

For example:

```bash
gcu merge-conflicts --merge-from="a branch containing the payment refactor" --merge-to="the main branch"
```


## Available Utilities

### 1. Merge Conflicts
This utility helps resolve merge conflicts by generating a new version of the file with the conflicts resolved. It takes two arguments: the branch containing the changes you want to merge and the branch you want to merge the changes into.
```bash
merge-conflicts
```

-----

- Ensure you are in a Git repository when running the script, as it relies on Git commands to detect merge conflicts.

-----


## Notes
- If you encounter issues with the PATH not updating immediately, try restarting your terminal or running the following command:


For macOS and Linux (depending on your shell):
```bash
  source ~/.zshrc  # For zsh
  source ~/.bashrc # For bash
```

For Windows, restart the command prompt.
