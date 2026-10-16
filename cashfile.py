import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

# File configurations
TRANSACTIONS_FILE = "home_cashbook.csv"
PRODUCTS_FILE = "products_list.csv"
ACCOUNTS_FILE = "accounts_list.csv"
HEADERS = ["Date", "Entity_Name", "Category", "Type", "Amount"]

# Empty default accounts so you can add them from scratch
DEFAULT_ACCOUNTS = []

# A comprehensive starter list for family expenses
DEFAULT_PRODUCTS = [
    "Clothing/Apparel", "Dining Out", "Doctor/Medical Consult",
    "Electricity Bill", "Entertainment/Movies", "Fuel/Petrol",
    "Gas/Cylinder", "Gifts/Donations", "Groceries", 
    "Home Repairs/Maintenance", "Internet/Wi-Fi", "Maid/Helper Salary",
    "Medical/Pharmacy", "Milk & Dairy", "Miscellaneous", 
    "Mobile Recharge", "Personal Care/Salon", "Public Transport",
    "Rent/Mortgage", "School/College Fees", "Stationery/Books",
    "Vegetables & Fruits", "Vehicle Maintenance", "Water Bill"
]

class CashbookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Accounting Cashbook")
        self.root.geometry("680x860")
        self.root.configure(padx=20, pady=20)

        self.init_files()

        self.family_accounts = []
        self.load_accounts()
        self.primary_options = self.family_accounts + ["Product / Expense"]
        self.product_list = [] 

        # ==========================================
        # UI: INPUT FORM
        # ==========================================
        form_frame = tk.LabelFrame(self.root, text=" Add New Entry ", padx=15, pady=15)
        form_frame.pack(fill="x", pady=(0, 15))

        tk.Label(form_frame, text="Date (DD-MM-YYYY):").grid(row=0, column=0, sticky="w", pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
        self.date_entry = ttk.Entry(form_frame, textvariable=self.date_var)
        self.date_entry.grid(row=0, column=1, sticky="ew", pady=5)

        tk.Label(form_frame, text="Account Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(form_frame, textvariable=self.account_var, values=self.primary_options, state="readonly")
        self.account_combo.grid(row=1, column=1, sticky="ew", pady=5)
        if self.primary_options:
            self.account_combo.current(0) 

        self.lbl_product = tk.Label(form_frame, text="Product Name:", fg="gray")
        self.lbl_product.grid(row=2, column=0, sticky="w", pady=5)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(form_frame, textvariable=self.product_var, state="disabled")
        self.product_combo.grid(row=2, column=1, sticky="ew", pady=5)
        self.load_products()

        tk.Label(form_frame, text="Transaction Type:").grid(row=3, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value="Receipt (Money In)")
        self.type_combo = ttk.Combobox(form_frame, textvariable=self.type_var, state="readonly", 
                                     values=["Receipt (Money In)", "Payment (Money Out)"])
        self.type_combo.grid(row=3, column=1, sticky="ew", pady=5)

        tk.Label(form_frame, text="Amount (₹):").grid(row=4, column=0, sticky="w", pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(form_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=4, column=1, sticky="ew", pady=5)

        self.save_btn = tk.Button(form_frame, text="Save Entry", command=self.add_entry, bg="#d9f2d9", height=2)
        self.save_btn.grid(row=5, column=0, columnspan=2, pady=15, sticky="ew")
        form_frame.columnconfigure(1, weight=1)

        self.account_combo.bind("<<ComboboxSelected>>", self.on_account_select)
        self.bind_enter_keys()
        self.on_account_select() 

        # ==========================================
        # UI: REPORTS & MANAGEMENT SECTION
        # ==========================================
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", pady=5)

        tk.Button(btn_frame, text="Ledger", command=self.show_ledger, width=9).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Trial Bal.", command=self.show_trial_balance, width=9).pack(side="left", padx=2)
        tk.Button(btn_frame, text="P&L", command=self.show_pnl, width=7).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Manage Acc.", command=self.open_manage_accounts_window, width=10, bg="#e6f2ff").pack(side="left", padx=2)
        tk.Button(btn_frame, text="Edit Entries", command=self.open_edit_entries_window, width=11, bg="#fff2e6").pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="Delete Data", command=self.delete_old_data, width=10, bg="#ffcccc").pack(side="right", padx=2)

        self.display_box = tk.Text(self.root, height=15, state="disabled", bg="#f4f4f4", font=("Courier", 10))
        self.display_box.pack(fill="both", expand=True, pady=10)

    # ==========================================
    # LOGIC & BINDINGS
    # ==========================================
    def init_files(self):
        if not os.path.exists(PRODUCTS_FILE) or os.path.getsize(PRODUCTS_FILE) == 0:
            with open(PRODUCTS_FILE, mode='w', encoding='utf-8') as f:
                for item in DEFAULT_PRODUCTS:
                    f.write(f"{item}\n")

        if not os.path.exists(ACCOUNTS_FILE) or os.path.getsize(ACCOUNTS_FILE) == 0:
            with open(ACCOUNTS_FILE, mode='w', encoding='utf-8') as f:
                for acc in DEFAULT_ACCOUNTS:
                    f.write(f"{acc}\n")

        if os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, mode='r', encoding='utf-8') as file:
                try:
                    existing_headers = next(csv.reader(file))
                    if existing_headers != HEADERS:
                        file.close() 
                        os.rename(TRANSACTIONS_FILE, "OLD_BACKUP_" + TRANSACTIONS_FILE)
                        with open(TRANSACTIONS_FILE, mode='w', newline='', encoding='utf-8') as new_file:
                            csv.writer(new_file).writerow(HEADERS)
                except StopIteration:
                    pass 
        else:
            with open(TRANSACTIONS_FILE, mode='w', newline='', encoding='utf-8') as file:
                csv.writer(file).writerow(HEADERS)

    def load_accounts(self):
        self.family_accounts = []
        try:
            with open(ACCOUNTS_FILE, mode='r', encoding='utf-8') as file:
                for line in file:
                    name = line.strip()
                    if name and name not in self.family_accounts:
                        self.family_accounts.append(name)
            self.family_accounts.sort()
        except FileNotFoundError:
            self.family_accounts = DEFAULT_ACCOUNTS.copy()

    def save_accounts_to_file(self):
        with open(ACCOUNTS_FILE, mode='w', encoding='utf-8') as file:
            for acc in self.family_accounts:
                file.write(f"{acc}\n")

    def update_account_dropdown(self):
        self.primary_options = self.family_accounts + ["Product / Expense"]
        self.account_combo['values'] = self.primary_options
        if self.account_var.get() not in self.primary_options:
            self.account_combo.current(0)

    def load_products(self):
        self.product_list = []
        try:
            with open(PRODUCTS_FILE, mode='r', encoding='utf-8') as file:
                for line in file:
                    name = line.strip()
                    if name and name not in self.product_list:
                        self.product_list.append(name)
            self.product_list.sort()
            self.product_combo['values'] = self.product_list
        except FileNotFoundError:
            pass

    def save_new_product(self, product_name):
        if product_name not in self.product_list:
            self.product_list.append(product_name)
            self.product_list.sort()
            self.product_combo['values'] = self.product_list 
            with open(PRODUCTS_FILE, mode='a', newline='', encoding='utf-8') as file:
                file.write(f"{product_name}\n")

    def on_account_select(self, event=None):
        account = self.account_var.get().strip()
        if account == "Product / Expense":
            self.product_combo.config(state="normal")
            self.lbl_product.config(fg="black")
            self.type_var.set("Payment (Money Out)") 
        else:
            self.product_combo.config(state="disabled")
            self.product_var.set("")
            self.lbl_product.config(fg="gray")
            self.type_var.set("Receipt (Money In)") 

    def on_account_enter(self, event):
        self.on_account_select()
        if self.account_var.get().strip() == "Product / Expense":
            self.product_combo.focus() 
        else:
            self.amount_entry.focus() 
        return "break"

    def bind_enter_keys(self):
        self.date_entry.bind("<Return>", lambda e: (self.account_combo.focus(), "break")[1])
        self.account_combo.bind("<Return>", self.on_account_enter)
        self.product_combo.bind("<Return>", lambda e: (self.amount_entry.focus(), "break")[1])
        self.type_combo.bind("<Return>", lambda e: (self.amount_entry.focus(), "break")[1])
        self.amount_entry.bind("<Return>", lambda e: (self.add_entry(), "break")[1])

    def add_entry(self):
        date_input = self.date_var.get().strip()
        account_selection = self.account_var.get().strip()
        t_type = "Receipt" if "Receipt" in self.type_var.get() else "Payment"
        amount_str = self.amount_var.get().strip()

        try:
            datetime.strptime(date_input, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please use DD-MM-YYYY format.")
            self.date_entry.focus()
            return

        if not self.family_accounts and account_selection != "Product / Expense":
            messagebox.showerror("Missing Account", "Please add at least one account using 'Manage Acc.' first.")
            return

        if account_selection == "Product / Expense":
            entity_name = self.product_var.get().strip().title()
            category = "Product/Expense"
            if not entity_name:
                messagebox.showerror("Missing Data", "Please enter a Product Name.")
                self.product_combo.focus()
                return
        else:
            if not account_selection:
                messagebox.showerror("Missing Data", "Please select an Account Name.")
                self.account_combo.focus()
                return
            entity_name = account_selection.title()
            category = "Family Account"

        if not amount_str:
            messagebox.showerror("Missing Data", "Please enter an amount.")
            self.amount_entry.focus()
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Amount must be a positive number.")
            self.amount_entry.focus()
            return

        if category == "Product/Expense":
            self.save_new_product(entity_name) 
            
        with open(TRANSACTIONS_FILE, mode='a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow([date_input, entity_name, category, t_type, amount])

        self.amount_var.set("")
        if category == "Product/Expense":
            self.product_var.set("")
            self.product_combo.focus() 
        else:
            self.account_combo.focus() 
            
        self.print_to_display(f"Saved: {date_input} | {entity_name} ({category}) | {t_type} | ₹{amount:.2f}")

    # ==========================================
    # ACCOUNT MANAGEMENT WINDOW
    # ==========================================
    def open_manage_accounts_window(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Accounts")
        win.geometry("350x400")
        win.grab_set()

        tk.Label(win, text="Current Family Accounts:", font=("Arial", 11, "bold")).pack(pady=10)

        frame_list = tk.Frame(win)
        frame_list.pack(fill="both", expand=True, padx=15)

        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side="right", fill="y")

        acc_listbox = tk.Listbox(frame_list, yscrollcommand=scrollbar.set, font=("Arial", 10))
        for acc in self.family_accounts:
            acc_listbox.insert(tk.END, acc)
        acc_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=acc_listbox.yview)

        add_frame = tk.Frame(win, padx=15, pady=10)
        add_frame.pack(fill="x")

        tk.Label(add_frame, text="New Account Name:").pack(anchor="w")
        new_acc_var = tk.StringVar()
        new_acc_entry = ttk.Entry(add_frame, textvariable=new_acc_var)
        new_acc_entry.pack(fill="x", pady=5)

        def add_account_action():
            name = new_acc_var.get().strip().title()
            if not name:
                messagebox.showerror("Error", "Account name cannot be empty.", parent=win)
                return
            if name in self.family_accounts or name == "Product / Expense":
                messagebox.showerror("Error", "Account already exists or is reserved.", parent=win)
                return
            
            self.family_accounts.append(name)
            self.family_accounts.sort()
            self.save_accounts_to_file()
            self.update_account_dropdown()

            acc_listbox.delete(0, tk.END)
            for acc in self.family_accounts:
                acc_listbox.insert(tk.END, acc)
            new_acc_var.set("")
            messagebox.showinfo("Success", f"Account '{name}' added successfully.", parent=win)

        def delete_account_action():
            try:
                selected_idx = acc_listbox.curselection()[0]
                acc_to_delete = acc_listbox.get(selected_idx)
            except IndexError:
                messagebox.showwarning("Selection Error", "Please select an account to delete.", parent=win)
                return

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete account '{acc_to_delete}'?", parent=win)
            if confirm:
                self.family_accounts.remove(acc_to_delete)
                self.save_accounts_to_file()
                self.update_account_dropdown()

                acc_listbox.delete(0, tk.END)
                for acc in self.family_accounts:
                    acc_listbox.insert(tk.END, acc)
                messagebox.showinfo("Success", f"Account '{acc_to_delete}' deleted.", parent=win)

        btn_action_frame = tk.Frame(win, padx=15, pady=10)
        btn_action_frame.pack(fill="x")

        tk.Button(add_frame, text="Add Account", command=add_account_action, bg="#d9f2d9").pack(fill="x", pady=2)
        tk.Button(btn_action_frame, text="Delete Selected Account", command=delete_account_action, bg="#ffcccc").pack(fill="x", pady=2)

    # ==========================================
    # EDIT ENTRIES WINDOW
    # ==========================================
    def open_edit_entries_window(self):
        edit_win = tk.Toplevel(self.root)
        edit_win.title("View and Edit Entries")
        edit_win.geometry("750x550")
        edit_win.grab_set()

        tk.Label(edit_win, text="All Recorded Transactions", font=("Arial", 12, "bold")).pack(pady=10)

        # Treeview Table
        columns = ("Index", "Date", "Entity Name", "Category", "Type", "Amount")
        tree = ttk.Treeview(edit_win, columns=columns, show="headings", height=15)
        
        tree.heading("Index", text="No.")
        tree.heading("Date", text="Date")
        tree.heading("Entity Name", text="Entity Name")
        tree.heading("Category", text="Category")
        tree.heading("Type", text="Type")
        tree.heading("Amount", text="Amount (₹)")

        tree.column("Index", width=40, anchor="center")
        tree.column("Date", width=90, anchor="center")
        tree.column("Entity Name", width=180, anchor="w")
        tree.column("Category", width=130, anchor="w")
        tree.column("Type", width=100, anchor="center")
        tree.column("Amount", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(edit_win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="top", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        def load_tree_data():
            for item in tree.get_children():
                tree.delete(item)
            data = self.get_all_data()
            for idx, row in enumerate(data):
                tree.insert("", "end", values=(idx, row.get("Date"), row.get("Entity_Name"), row.get("Category"), row.get("Type"), row.get("Amount")))

        load_tree_data()

        # Edit Form Frame at bottom
        form_edit = tk.LabelFrame(edit_win, text=" Edit Selected Entry ", padx=10, pady=10)
        form_edit.pack(fill="x", padx=15, pady=10)

        tk.Label(form_edit, text="Date (DD-MM-YYYY):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        e_date_var = tk.StringVar()
        e_date_entry = ttk.Entry(form_edit, textvariable=e_date_var, width=15)
        e_date_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form_edit, text="Entity Name:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        e_entity_var = tk.StringVar()
        e_entity_entry = ttk.Entry(form_edit, textvariable=e_entity_var, width=18)
        e_entity_entry.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(form_edit, text="Category:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        e_cat_var = tk.StringVar()
        e_cat_combo = ttk.Combobox(form_edit, textvariable=e_cat_var, values=["Family Account", "Product/Expense"], state="readonly", width=15)
        e_cat_combo.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(form_edit, text="Type:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        e_type_var = tk.StringVar()
        e_type_combo = ttk.Combobox(form_edit, textvariable=e_type_var, values=["Receipt", "Payment"], state="readonly", width=15)
        e_type_combo.grid(row=1, column=3, padx=5, pady=2)

        tk.Label(form_edit, text="Amount (₹):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        e_amt_var = tk.StringVar()
        e_amt_entry = ttk.Entry(form_edit, textvariable=e_amt_var, width=15)
        e_amt_entry.grid(row=2, column=1, padx=5, pady=2)

        def on_row_select(event):
            selected_item = tree.selection()
            if not selected_item:
                return
            item_values = tree.item(selected_item, "values")
            # item_values: (Index, Date, Entity Name, Category, Type, Amount)
            e_date_var.set(item_values[1])
            e_entity_var.set(item_values[2])
            e_cat_var.set(item_values[3])
            e_type_var.set(item_values[4])
            e_amt_var.set(item_values[5])

        tree.bind("<<TreeviewSelect>>", on_row_select)

        def save_edited_entry():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select a row from the table to edit.", parent=edit_win)
                return
            
            item_values = tree.item(selected_item, "values")
            row_idx = int(item_values[0])

            new_date = e_date_var.get().strip()
            new_entity = e_entity_var.get().strip().title()
            new_cat = e_cat_var.get().strip()
            new_type = e_type_var.get().strip()
            new_amt_str = e_amt_var.get().strip()

            try:
                datetime.strptime(new_date, "%d-%m-%Y")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please use DD-MM-YYYY format.", parent=edit_win)
                return

            if not new_entity:
                messagebox.showerror("Error", "Entity Name cannot be empty.", parent=edit_win)
                return

            try:
                new_amt = float(new_amt_str)
                if new_amt <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Amount", "Amount must be a positive number.", parent=edit_win)
                return

            data = self.get_all_data()
            if 0 <= row_idx < len(data):
                data[row_idx] = {
                    "Date": new_date,
                    "Entity_Name": new_entity,
                    "Category": new_cat,
                    "Type": new_type,
                    "Amount": new_amt
                }

                # Save back to file
                with open(TRANSACTIONS_FILE, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=HEADERS)
                    writer.writeheader()
                    writer.writerows(data)

                load_tree_data()
                messagebox.showinfo("Success", "Entry updated successfully.", parent=edit_win)
                self.print_to_display(f"Updated Entry: {new_date} | {new_entity} | {new_type} | ₹{new_amt:.2f}")

        def delete_selected_entry():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select a row from the table to delete.", parent=edit_win)
                return

            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete this specific entry?", parent=edit_win)
            if not confirm:
                return

            item_values = tree.item(selected_item, "values")
            row_idx = int(item_values[0])

            data = self.get_all_data()
            if 0 <= row_idx < len(data):
                deleted = data.pop(row_idx)

                with open(TRANSACTIONS_FILE, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=HEADERS)
                    writer.writeheader()
                    writer.writerows(data)

                load_tree_data()
                e_date_var.set("")
                e_entity_var.set("")
                e_amt_var.set("")
                messagebox.showinfo("Success", "Entry deleted successfully.", parent=edit_win)
                self.print_to_display(f"Deleted entry: {deleted.get('Date')} | {deleted.get('Entity_Name')}")

        btn_frame_action = tk.Frame(edit_win, padx=15, pady=5)
        btn_frame_action.pack(fill="x")

        tk.Button(form_edit, text="Save Changes", command=save_edited_entry, bg="#d9f2d9", width=15).grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="ew")
        tk.Button(btn_frame_action, text="Delete Selected Entry", command=delete_selected_entry, bg="#ffcccc").pack(side="left", pady=5)

    # ==========================================
    # DATA DELETION LOGIC (2 Verifications)
    # ==========================================
    def delete_old_data(self):
        date_str = simpledialog.askstring("Delete Old Data", "Enter the cutoff date (DD-MM-YYYY).\nAll records exactly on or older than this date will be permanently deleted:")
        
        if not date_str:
            return 

        try:
            cutoff_date = datetime.strptime(date_str.strip(), "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please use the exact DD-MM-YYYY format.")
            return

        confirm1 = messagebox.askyesno("First Verification", f"Are you absolutely sure you want to delete ALL transactions on or before {date_str}?\n\nThis cannot be undone!")
        if not confirm1:
            return

        confirm2 = simpledialog.askstring("Final Verification", "Type the word DELETE in all caps to confirm this action:")
        if confirm2 != "DELETE":
            messagebox.showinfo("Cancelled", "Action cancelled. Your data is safe.")
            return

        data = self.get_all_data()
        if not data:
            return

        rows_to_keep = []
        deleted_count = 0

        for row in data:
            try:
                row_date = datetime.strptime(row["Date"], "%d-%m-%Y")
                if row_date > cutoff_date:
                    rows_to_keep.append(row)
                else:
                    deleted_count += 1
            except ValueError:
                rows_to_keep.append(row) 

        if deleted_count == 0:
            messagebox.showinfo("Result", "No records found on or before that date.")
            return

        with open(TRANSACTIONS_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows_to_keep)

        self.print_to_display(f"CLEANUP COMPLETE: Successfully deleted {deleted_count} old records.")
        messagebox.showinfo("Success", f"Successfully deleted {deleted_count} records from the database.")

    # ==========================================
    # ACCOUNTING REPORTS
    # ==========================================
    def print_to_display(self, text):
        self.display_box.config(state="normal")
        self.display_box.delete("1.0", tk.END)
        self.display_box.insert(tk.END, text)
        self.display_box.config(state="disabled")

    def get_all_data(self):
        data = []
        try:
            with open(TRANSACTIONS_FILE, mode='r', encoding='utf-8') as file:
                for row in csv.DictReader(file):
                    if row and row.get("Amount"): 
                        data.append(row)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}\nTry deleting the CSV file and restarting.")
        return data

    def show_ledger(self):
        data = self.get_all_data()
        if not data:
            self.print_to_display("No transactions found.")
            return

        ledgers = {}
        for row in data:
            name = row.get("Entity_Name", "Unknown") 
            if name not in ledgers:
                ledgers[name] = []
            ledgers[name].append(row)

        output = "--- GENERAL LEDGER ---\n\n"
        for name, txns in ledgers.items():
            category = txns[0].get("Category", "Unknown")
            output += f"Account: {name} ({category})\n"
            output += "-" * 40 + "\n"
            total = 0.0
            for t in txns:
                try:
                    amt = float(t["Amount"])
                    if t["Type"] == "Receipt":
                        output += f"{t['Date']} | Credit (In)  | ₹{amt:.2f}\n"
                        total += amt
                    else:
                        output += f"{t['Date']} | Debit (Out) | ₹{amt:.2f}\n"
                        total -= amt
                except (ValueError, KeyError):
                    continue
            
            bal_type = "Credit" if total >= 0 else "Debit"
            output += f"Balance: ₹{abs(total):.2f} ({bal_type})\n"
            output += "=" * 40 + "\n\n"
            
        self.print_to_display(output)

    def show_trial_balance(self):
        data = self.get_all_data()
        if not data:
            self.print_to_display("No transactions found to calculate.")
            return
            
        cash_balance, total_debit, total_credit = 0.0, 0.0, 0.0
        account_balances = {}

        for row in data:
            name = row.get("Entity_Name", "Unknown")
            try:
                amt = float(row["Amount"])
            except (ValueError, KeyError):
                continue
            
            if name not in account_balances:
                account_balances[name] = {"type": row.get("Type", ""), "total": 0.0}

            if row.get("Type") == "Receipt":
                cash_balance += amt  
                account_balances[name]["total"] += amt
            else:
                cash_balance -= amt  
                account_balances[name]["total"] += amt 

        output = "--- TRIAL BALANCE ---\n\n"
        output += f"{'Account Name':<20} | {'Debit (₹)':<12} | {'Credit (₹)':<12}\n"
        output += "-" * 50 + "\n"

        if cash_balance > 0:
            output += f"{'Cash in Hand':<20} | {cash_balance:<12.2f} | {'-':<12}\n"
            total_debit += cash_balance
        elif cash_balance < 0:
             output += f"{'Cash Overdrawn':<20} | {'-':<12} | {abs(cash_balance):<12.2f}\n"
             total_credit += abs(cash_balance)

        for name, info in account_balances.items():
            if info["type"] == "Payment":
                output += f"{name:<20} | {info['total']:<12.2f} | {'-':<12}\n"
                total_debit += info['total']
            else:
                output += f"{name:<20} | {'-':<12} | {info['total']:<12.2f}\n"
                total_credit += info['total']

        output += "-" * 50 + "\n"
        output += f"{'TOTAL':<20} | {total_debit:<12.2f} | {total_credit:<12.2f}\n"
        output += f"\nStatus: {'BALANCED' if round(total_debit, 2) == round(total_credit, 2) else 'UNBALANCED'}"
        self.print_to_display(output)

    def show_pnl(self):
        data = self.get_all_data()
        if not data:
            self.print_to_display("No transactions found to calculate.")
            return
            
        income, expense = 0.0, 0.0

        for row in data:
            try:
                amt = float(row["Amount"])
                if row.get("Type") == "Receipt":
                    income += amt
                else:
                    expense += amt
            except (ValueError, KeyError):
                continue

        net = income - expense
        output = "--- PROFIT & LOSS ACCOUNT ---\n\n"
        output += f"Total Income / Capital:  ₹{income:.2f}\n"
        output += f"Total Expenses:         -₹{expense:.2f}\n"
        output += "-" * 35 + "\n"
        output += f"{'NET SURPLUS' if net >= 0 else 'NET DEFICIT'}:         ₹{abs(net):.2f}\n"
        self.print_to_display(output)

if __name__ == "__main__":
    root = tk.Tk()
    app = CashbookApp(root)
    root.mainloop()
