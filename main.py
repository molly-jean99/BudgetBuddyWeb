import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
import json
import os

# ------------------------------
# Setup
# ------------------------------
root = tk.Tk()
root.title("BudgetBuddy")
root.geometry("950x700")
root.configure(bg="#f2f2f2")

DATA_FILE = "budget_data.json"

# ------------------------------
# Data
# ------------------------------

users = {}
current_user = "guest"

# ------------------------------
# Save / Load
# ------------------------------

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)
        json.dump(data, f)

def load_data():
    global users

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            users = json.load(f)
    else:
        users = {}

    if current_user not in users:
        users[current_user] = []

def get_transactions():
    return users[current_user]

def change_user(event=None):
    global current_user

    current_user = user_var.get()

    if current_user not in users:
        users[current_user] = []

    update_ui()

# ------------------------------
# Add Transaction
# ------------------------------

def add_transaction():
    t_type = type_var.get()
    category = category_var.get().strip()
    amount = amount_entry.get()
    group = group_var.get()
    date = date_entry.get().strip()

    if not date:
        date = datetime.now().strftime("%m/%d/%Y")

    if not category:
        messagebox.showerror("Error", "Enter a category")
        return
    try:
        amount = float(amount)

        if amount <= 0:
            messagebox.showerror("Error", "Amount must be greater than 0")
            return
    
    except:
        messagebox.showerror("Error", "Invalid amount")
        return

    get_transactions().append({
        "date": date,
        "type": t_type,
        "category": category,
        "amount": amount,
        "group": group
    })

    date_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_box.set("")

    save_data()
    update_ui()

# ------------------------------
# Update UI
# ------------------------------
def delete_transaction():
    selected = listbox.curselection()

    if not selected:
        messagebox.showerror("Error", "Select a transaction to delete")
        return

    index = selected[0]
    transaction = get_transactions()[index]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Delete this transaction?\n\n"
        f"{transaction.get('date', 'No Date')} | {transaction['category']} | ${transaction['amount']}"
    )

    if confirm:
        del get_transactions()[index]
        save_data()
        update_ui()

def edit_transaction():
    selected = listbox.curselection()

    if not selected:
        messagebox.showerror("Error", "Select a transaction to edit")
        return

    index = selected[0]
    transaction = get_transactions()[index]

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Transaction")
    edit_window.geometry("300x300")

    # Fields
    tk.Label(edit_window, text="Date").pack()
    date_e = tk.Entry(edit_window)
    date_e.insert(0, transaction.get("date", ""))
    date_e.pack()

    tk.Label(edit_window, text="Category").pack()
    cat_e = tk.Entry(edit_window)
    cat_e.insert(0, transaction["category"])
    cat_e.pack()

    tk.Label(edit_window, text="Amount").pack()
    amt_e = tk.Entry(edit_window)
    amt_e.insert(0, str(transaction["amount"]))
    amt_e.pack()

    tk.Label(edit_window, text="Type (Income/Expense)").pack()
    type_var_edit = tk.StringVar(value=transaction["type"])
    ttk.Combobox(
        edit_window,
        textvariable=type_var_edit,
        values=["Income", "Expense"],
        state="readonly"
    ).pack()

    tk.Label(edit_window, text="Group (Savings/Spending)").pack()
    group_var_edit = tk.StringVar(value=transaction["group"])
    ttk.Combobox(
        edit_window,
        textvariable=group_var_edit,
        values=["Savings", "Spending"],
        state="readonly"
    ).pack()

    def save_edit():
        try:
            new_amount = float(amt_e.get())
            if new_amount <= 0:
                messagebox.showerror("Error", "Amount must be > 0")
                return
        except:
            messagebox.showerror("Error", "Invalid amount")
            return

        transaction["date"] = date_e.get().strip() or datetime.now().strftime("%m/%d/%Y")
        transaction["category"] = cat_e.get().strip()
        transaction["amount"] = new_amount
        transaction["type"] = type_var_edit.get()
        transaction["group"] = group_var_edit.get()

        save_data()
        update_ui()
        edit_window.destroy()

    tk.Button(edit_window, text="Save Changes", command=save_edit, bg="green", fg="white").pack(pady=10)

def update_ui():
    update_transactions()
    update_balance()


def update_transactions():
    listbox.delete(0, tk.END)

    for t in get_transactions():
        symbol = "+" if t["type"] == "Income" else "-"

        date = t.get("date", "No Date")
        t_type = t["type"]
        category = t["category"]
        group = t["group"]
        amount = f"{symbol}${t['amount']:.2f}"

        text = f"{date:<12} {t_type:<8} {category:<15} {group:<10} {amount:>10}"

        listbox.insert(tk.END, text)


def update_balance():
    income = 0
    expense = 0
    savings = 0

    for t in get_transactions():

        if t["type"] == "Income":
            income += t["amount"]
        else:
            expense += t["amount"]

        if t.get("group") == "Savings":
            if t["type"] == "Income":
                savings += t["amount"]
            else: 
                savings -= t["amount"]

    balance = income - expense

    balance_label.config(text=f"Balance: ${balance:.2f}")

    income_label.config(text=f"Income: ${income:.2f}")
    expense_label.config(text=f"Expenses: ${expense:.2f}")
    savings_label.config(text=f"Savings: ${savings:.2f}")

# ------------------------------
# UI
# ------------------------------

title = tk.Label(root, text="BudgetBuddy", font=("Arial", 24, "bold"), bg="#f2f2f2")
title.pack(pady=10)

frame = tk.Frame(root, bg="#f2f2f2")
frame.pack(pady=10)

# User Selection

tk.Label(frame, text="User:", bg="#f2f2f2").grid(row=0, column=0)

user_var = tk.StringVar(value=current_user)

user_box = ttk.Combobox(
    frame,
    textvariable=user_var,
    values=list(users.keys()),
    width=12
)

user_box.grid(row=0, column=1)
user_box.bind("<<ComboboxSelected>>", change_user)

# Type

type_var = tk.StringVar(value="Expense")
tk.Label(frame, text="Type:", bg="#f2f2f2").grid(row=0, column=0)

ttk.Combobox(
    frame, 
    textvariable=type_var, 
    values=["Income", "Expense"], 
    width=10,
    state="readonly"
).grid(row=0, column=3)

# Category

category_var = tk.StringVar()
tk.Label(frame, text="Category:", bg="#f2f2f2").grid(row=0, column=2)

category_box = ttk.Combobox(
    frame,
    textvariable=category_var,
    values=[],
    width=18
)
category_box.grid(row=0, column=5)

# Date
tk.Label(frame, text="Date:", bg="#f2f2f2").grid(row=0, column=4)

date_entry = tk.Entry(frame, width=12)
date_entry.grid(row=0, column=7)

# Amount
tk.Label(frame, text="Amount:", bg="#f2f2f2").grid(row=0, column=6)

amount_entry = tk.Entry(frame, width=10)
amount_entry.grid(row=0, column=9)

# Group
tk.Label(frame, text="Group:", bg="#f2f2f2").grid(row=0, column=8)

group_var = tk.StringVar(value="Spending")
ttk.Combobox(
    frame, 
    textvariable=group_var, 
    values=["Savings","Spending"], 
    width=10
).grid(row=0, column=11)

# Button

add_btn = tk.Button(root, text="Add", command=add_transaction, bg="green", fg="white")
add_btn.pack(pady=5)

delete_btn = tk.Button(root, text="Delete Selected", command=delete_transaction, bg="red", fg="white")
delete_btn.pack(pady=5)

edit_btn = tk.Button(root, text="Edit Selected", command=edit_transaction, bg="orange", fg="black")
edit_btn.pack(pady=5)

# Balance
balance_label = tk.Label(root, text="Balance: $0", font=("Arial", 16), bg="#f2f2f2")
balance_label.pack()

income_label = tk.Label(root, text="Income: $0.00", bg="#f2f2f2")
income_label.pack()

expense_label = tk.Label(root, text="Expenses: $0.00", bg="#f2f2f2")
expense_label.pack()

savings_label = tk.Label(root, text="Savings: $0.00", bg="#f2f2f2")
savings_label.pack()

# Transactions
listbox = tk.Listbox(root, width=80)
listbox.pack(pady=10)

load_data()
root.mainloop()