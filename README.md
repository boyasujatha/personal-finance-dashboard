Personal Finance Dashboard
A web-based interactive Personal Finance Dashboard built using **Python**, **Pandas**, and **Streamlit** to help you track, analyze, and visualize your spending habits.
## 🌟 Features
* **Automated Categorization**: Uses keyword heuristics to automatically categorize your transactions into `Groceries`, `Subscriptions`, `Transportation`, or `Other`.
* **High-Level Financial Metrics**: Instantly displays Total Spending, Top Expense Category, and Total Transaction Count.
* **Interactive Data Visualizations**:
  - **Spending Trend**: Timeline bar/line chart displaying monthly or daily transaction flow.
  - **Spending Breakdown**: Clean donut/pie chart displaying spending allocation by category.
* **Dynamic Sidebar Filters**: Filter transaction data on-the-fly by Date Range and Categories.
* **Searchable Transactions Table**: Easily search through merchant descriptions or categories, and download your filtered data back to CSV.
* **Built-in Mock Data Generator**: Test and explore the dashboard immediately with the built-in mock data button without needing an actual bank statement CSV.
---
## 🛠️ Tech Stack
* **Frontend & UI**: [Streamlit](https://streamlit.io/)
* **Data Processing**: [Pandas](https://pandas.pydata.org/)
* **Visualizations**: [Plotly Express](https://plotly.com/python/)
---
## 🚀 Getting Started
Follow these steps to run the project locally on your machine:
### 1. Prerequisites
Ensure you have Python installed (Python 3.8 or higher is recommended).
### 2. Clone/Open the Project Directory
Navigate to the folder containing the project files:
```bash
cd C:\Users\SUJATHA\.gemini\antigravity\scratch\personal_finance_dashboard
```
### 3. Install Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```
### 4. Run the Application
Start the Streamlit development server:
```bash
python -m streamlit run app.py
```
*Note: If you are running it inside your custom virtual environment folder, you can run:*
```bash
.\Scripts\streamlit.exe run app.py
```
After running the command, your default browser will open the dashboard automatically at `http://localhost:8501`.
---
## 📂 Project Structure
```text
personal_finance_dashboard/
├── app.py                     # Main Streamlit application
├── generate_sample_data.py    # Utility script to generate test data
├── sample_transactions.csv    # Pre-generated sample transactions dataset
├── requirements.txt           # Python dependencies list
├── .gitignore                 # Files to exclude from Git uploads
└── README.md                  # Project documentation (this file)
```
