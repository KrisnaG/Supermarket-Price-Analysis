# Supermarket Price Analysis

A Python application to track and analyse supermark products.

## Setup

1. Clone the repository
2. Navigate to the project directory
3. Create a virtual environment
4. Activate the virtual environment
5. Install the required packages

```commandline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the application

To run the application, use the following command:

```commandline
python3 src/main/py
```

## Building

To build the application as a standalone executable, you can use PyInstaller.

```commandline
pyinstaller --onefile --name "Supermarket Price Analysis" src/main.py --add-data "resources/database/products.db:resources/database"
```
