\# CSV Data Explorer (CLI Tool)



A command-line tool built with Python to explore and analyze CSV files without needing Excel or pandas. It lets you filter, sort, search, and export data directly from your terminal.



---



\## 🔧 Features



\- 📂 Load and preview CSV files

\- 🔍 Filter rows by column values (single or multiple)

\- ⚙️ Advanced filters using operators (`==`, `>`, `<`, etc.)

\- 📊 View column statistics and unique values

\- 📋 List all available columns

\- 🧾 Display all or limited rows

\- 📤 Export filtered data to a new CSV file

\- 📌 Interactive AND/OR condition-based filtering

\- 🧮 Sort data by any column



---



\## 🛠️ Tech Stack



\- \*\*Python 3\*\*

\- Built-in modules: `csv`, `os`, `sys`, `operator`

\- External: `tabulate` (for table-like display)



---



## 🚀 How to Run

### 1. Make sure you have Python installed

You can check this by running:


python --version


If it shows something like `Python 3.x.x`, you're ready to go.

---

### 2. Install the required module

This project uses the `tabulate` module for pretty table output. Install it using:

pip install tabulate


---

### 3. Run the tool with a CSV file

Use the terminal to run:

python main.py yourfile.csv


Replace `yourfile.csv` with the actual path or name of your CSV file. For example:

python main.py sample_data.csv


---

### 4. Interact using the menu

Once the script starts, you'll see a menu in the terminal:

- Filter data by values (single or multiple)
- Use advanced operator filters (`==`, `!=`, `>`, `<`, etc.)
- View unique column values or stats
- Sort data by any column
- Export filtered data to a new CSV
- Use AND/OR logic with multiple filters

You can type `exit` anytime to quit an input prompt.

---
