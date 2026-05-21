from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "budget_data.json"

transactions = []

# -------------------------
# Load / Save
# -------------------------
def load_data():
    global transactions

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            transactions = data.get("transactions", [])

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"transactions": transactions}, f)

# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    load_data()

    income = sum(t["amount"] for t in transactions if t["type"] == "Income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "Expense")

    balance = income - expense

    return render_template(
        "index.html",
        transactions=transactions,
        balance=balance,
        income=income,
        expense=expense
    )

@app.route("/add", methods=["POST"])
def add():
    t_type = request.form["type"]
    category = request.form["category"]
    amount = float(request.form["amount"])
    group = request.form["group"]

    date = request.form["date"]
    if not date:
        date = datetime.now().strftime("%m/%d/%Y")

    transactions.append({
        "date": date,
        "type": t_type,
        "category": category,
        "amount": amount,
        "group": group
    })

    save_data()
    return redirect("/")

@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(transactions):
        del transactions[index]
        save_data()

    return redirect("/")

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
