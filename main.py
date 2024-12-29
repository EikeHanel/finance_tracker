from helper_database import Tracker
from helper_plot import bar_plot, graph
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
import datetime

COLORS = {
    "background": "#f0f0f0",  # Light Gray
    "button_background": "#d9d9d9",  # Slightly Darker Gray
    "label_background": "#f0f0f0",  # Light Gray
    "entry_background": "#ffffff",  # White
    "highlight": "#0078D7",  # Blue for selected states
    "highlight_press": "#ff9900",
    "text": "#000000"  # Dark purple text for a rich contrast
}

FONTS = {
    "heading": ("Arial", 20, "bold"),
    "subheading": ("Arial", 14, "bold"),
    "button": ("Arial", 12, "bold"),
    "small": ("Arial", 10)
}


def main():
    tracker = Tracker()
    gui(tracker)


def gui(tracker):
    root = tk.Tk()
    root.title("Finance Tracker")
    root.config(bg=COLORS["background"])

    '''
        Applying ttk.Style for the whole GUI. 
    '''
    style = ttk.Style()
    style.theme_use('alt')
    style.configure(
        "TNotebook",
        background=COLORS["background"],
        padding=5
    )
    style.configure(
        "TNotebook.Tab",
        padding=[10, 5],
        focuscolor='none',
        background=COLORS["background"]
    )
    style.map(
        "TNotebook.Tab",
        relief=[('selected', 'flat')],
        focuscolor=[("focus", "none")],
        background=[('selected', COLORS["background"])]
    )
    style.configure(
        "CustomFrame.TFrame",
        background=COLORS["background"]
    )
    style.configure(
        "TButton",
        padding=10,
        relief="solid",  # Remove raised effect to make the background more prominent
        background=COLORS["button_background"],  # Button background color
        foreground=COLORS["text"],  # Text color for button
        borderwidth=2,  # Increase border width for visibility
        focusthickness=0  # Remove focus border
    )
    style.configure(
        "Custom.TButton",
        font=FONTS["button"],
    )
    style.map(
        "Custom.TButton",
        background=[("active", COLORS["highlight"]), ("pressed", COLORS["highlight_press"])],
        relief=[("pressed", "flat"), ("active", "flat")],
        focuscolor='none'
    )
    style.configure(
        "TLabel",
        padding=5,
        background=COLORS["label_background"],
        foreground=COLORS["text"],
    )
    style.configure(
        "TEntry",
        padding=10,
        background=COLORS["entry_background"],
        foreground=COLORS["text"],
    )
    # Style for TCombobox widget (input field of combobox)
    style.configure(
        "TCombobox",
        padding=10,
        fieldbackground=COLORS["entry_background"],  # Set background of the combobox input field
        foreground=COLORS["text"],  # Set text color in the combobox input field
    )

    # Custom style for the TCombobox to apply font
    style.configure(
        "Custom.TCombobox",
        font=FONTS["button"],  # Use a consistent font for the combobox
    )

    # Map the combobox style to handle focus behavior and dropdown appearance
    style.map(
        "Custom.TCombobox",
        background=[("focus", COLORS["entry_background"])],  # Set white background when focused
        foreground=[("focus", COLORS["text"])],  # Set black text when focused
        selectbackground=[("active", COLORS["entry_background"])],
        # Ensure the background matches when an item is selected
        selectforeground=[("active", COLORS["text"])],  # Set text color for selected item in dropdown
    )

    # Additional mapping for the dropdown background color to match the input field
    style.map(
        "Custom.TCombobox",
        fieldbackground=[("focus", COLORS["entry_background"])],  # Ensure the input field stays the same color
        selectbackground=[("active", COLORS["entry_background"])],
        # Set drop down's selected item background to match input field
        selectforeground=[("active", COLORS["text"])]  # Ensure text color is black for selected item
    )

    # For the actual dropdown list background
    style.configure(
        "Custom.TCombobox",
        selectbackground=COLORS["entry_background"],  # Set background for selected item in the dropdown
        selectforeground=COLORS["text"]  # Set text color for selected item in the dropdown
    )
    style.configure(
        "TRadiobutton",
        padding=5,
        background=COLORS["background"],
        foreground=COLORS["text"],
        focuscolor="none"
    )

    '''
        Creating a Notebook (container for tabs)
    '''
    notebook = ttk.Notebook(root)
    notebook.grid(row=0, column=0, padx=10, pady=10)

    # Define the frames (tabs) without pre-populating them
    tab1 = ttk.Frame(notebook, style="CustomFrame.TFrame")
    tab2 = ttk.Frame(notebook, style="CustomFrame.TFrame")
    tab3 = ttk.Frame(notebook, style="CustomFrame.TFrame")
    tab4 = ttk.Frame(notebook, style="CustomFrame.TFrame")
    tab5 = ttk.Frame(notebook, style="CustomFrame.TFrame")

    # Add the tabs to the notebook
    notebook.add(tab1, text='Balance')
    notebook.add(tab2, text='Graph')
    notebook.add(tab3, text='Expenses')
    notebook.add(tab4, text='Table')
    notebook.add(tab5, text='Edit Data')

    '''
        Functionality for the GUI
        Some functions only get initialized when a tab is opened. 
        Thus, ignore error's, test via program to validate functionality.
    '''
    def populate_table(tree, dataframe):
        for _, row in dataframe.iterrows():
            tree.insert("", "end", values=(row["date"], row["category_name"], f"{row['amount']:.2f}", row["comment"]))

    def sort_by(tree, column, descending):
        # Retrieve data to sort
        data = [(tree.set(child, column), child) for child in tree.get_children("")]

        # Convert data to the appropriate type for sorting
        try:
            data.sort(reverse=descending, key=lambda item: float(item[0]))  # Try to sort as float
        except ValueError:
            data.sort(reverse=descending, key=lambda item: item[0])  # Sort as string if conversion fails

        # Rearrange items in sorted order
        for index, (_, child) in enumerate(data):
            tree.move(child, "", index)

        # Reverse the sorting order for next click
        tree.heading(column, command=lambda: sort_by(tree, column, not descending))

    def delete_transaction(tree):
        # Get the selected row
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a transaction to delete.")
            return

        # Get the 'id' of the selected transaction (assuming it's in the dataframe)
        selected_transaction = tree.item(selected_item)["values"]
        transaction_date = selected_transaction[0]  # Assuming first column is 'Date'
        transaction_category = selected_transaction[1]  # Assuming second column is 'Category'
        transaction_amount = selected_transaction[2]  # Assuming third column is 'Amount'
        transaction_comment = selected_transaction[3]  # Assuming fourth column is 'Comment'

        # Find the corresponding row in the dataframe using these values
        transaction_row = table_data[
            (table_data["date"] == transaction_date) &
            (table_data["category_name"] == transaction_category) &
            (table_data["amount"] == float(transaction_amount)) &
            (table_data["comment"] == transaction_comment)
            ]
        if transaction_row.empty:
            messagebox.showerror("Error", "Transaction not found in the database.")
            return
        # Call the delete function from the tracker
        transaction_id = transaction_row.iloc[0]["id"]
        print(transaction_id)

        # Delete transaction
        tracker.del_transaction(transaction_id)

        # Remove the row from the treeview
        tree.delete(selected_item)

    def add_transaction():
        # Create a new window for adding transaction
        add_window = tk.Toplevel(root)
        add_window.title("Add Transaction")
        add_window.config(padx=30, pady=20, bg=COLORS["background"])  # Padding for the window

        # Variables for the entry fields
        transaction_type = tk.StringVar(value="Expense")  # Set default value to "Expense"
        category_var = tk.StringVar()
        categories = list(tracker.read_categories()["name"])
        placeholder = "Select a category"
        amount_var = tk.DoubleVar()
        comment_var = tk.StringVar()
        date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))

        sign = False  # Default to False

        # Function to update category and sign based on the selected transaction type
        def on_transaction_type_change():
            nonlocal sign  # Use the outer sign variable

            if transaction_type.get() == "Income":
                category_combobox.set("Income")  # Set category to "Income"
                sign = True  # Set sign to True for "Income"
            else:
                category_combobox.set("")  # Clear the category combobox
                sign = False  # Set sign to False for "Expense"

        # Label for Transaction Type (on top)
        trans_label = ttk.Label(add_window, text="Transaction:", font=FONTS["heading"])
        trans_label.grid(row=0, column=1, columnspan=2, pady=5, sticky="n")

        # Label and radio button for "Expense"
        expense_label = ttk.Label(add_window, text="Expense", font=FONTS["button"])
        expense_label.grid(row=1, column=1, pady=5, sticky="n")

        income_radio = ttk.Radiobutton(add_window, variable=transaction_type,
                                       value="Expense", command=on_transaction_type_change)
        income_radio.grid(row=2, column=1, pady=5, sticky="n")  # Place radio button next to label

        # Label and radio button for "Income"
        income_label = ttk.Label(add_window, text="Income", font=FONTS["button"])
        income_label.grid(row=1, column=2, pady=5, sticky="n")
        expense_radio = ttk.Radiobutton(add_window, variable=transaction_type,
                                        value="Income", command=on_transaction_type_change)
        expense_radio.grid(row=2, column=2, pady=5, sticky="n")  # Place radio button next to label

        # Dropdown for selecting the category
        category_label = ttk.Label(add_window, text="Category:", font=FONTS["subheading"])
        category_label.grid(row=3, column=0, pady=5, sticky="w")

        category_combobox = ttk.Combobox(add_window, textvariable=category_var,
                                         values=categories, state="readonly", style="Custom.TCombobox")
        category_combobox.set(placeholder)
        category_combobox.grid(row=3, column=1, columnspan=2, pady=5, sticky="n")

        # Entry for the amount
        amount_label = ttk.Label(add_window, text="Amount:", font=FONTS["subheading"])
        amount_label.grid(row=4, column=0, pady=5, sticky="w")
        amount_entry = ttk.Entry(add_window, textvariable=amount_var)
        amount_entry.grid(row=4, column=1, columnspan=2, pady=5, sticky="n")

        # Entry for the comment
        comment_label = ttk.Label(add_window, text="Comment:", font=FONTS["subheading"])
        comment_label.grid(row=5, column=0, pady=5, sticky="w")
        comment_entry = ttk.Entry(add_window, textvariable=comment_var)
        comment_entry.grid(row=5, column=1, columnspan=2, pady=5, sticky="n")

        # Calendar widget for selecting the date
        date_label = ttk.Label(add_window, text="Date:", font=FONTS["subheading"])
        date_label.grid(row=6, column=0, pady=5, sticky="w")
        cal = Calendar(add_window, textvariable=date_var, date_pattern='yyyy-mm-dd')
        cal.grid(row=6, column=1, columnspan=3, pady=5, sticky="w")

        # Submit Button to save the transaction
        def submit_transaction():
            category_value = category_var.get()
            amount_value = amount_var.get()
            comment_value = comment_var.get() if comment_var.get() else ""
            date_value = date_var.get()

            # Error Checks
            try:
                # Try to convert the amount to float
                amount_value = float(amount_value)
            except ValueError:
                # If conversion fails, show an error message and return
                messagebox.showerror("Invalid Input", "Please enter a valid amount.")
                return
            if not category_value or not amount_value or not date_value:
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            all_categories = categories.copy()
            all_categories.append("Income")
            if category_value not in all_categories:
                messagebox.showerror("Error", "Please choose a category. "
                                              "You can add categories in another window.")
                return

            # Save the transaction to the database (adjust according to your database schema)
            if not sign:
                amount_value = amount_value * (-1)
            tracker.add_transaction(category_value, amount_value, date_value, comment_value)

            # Close the add transaction window
            add_window.destroy()

        # Add submit button
        submit_button = ttk.Button(add_window, text="Submit Transaction", command=submit_transaction, style="Custom.TButton")
        submit_button.grid(row=7, column=1, columnspan=2, pady=20)

    def add_category():
        # Create a new window for adding transaction
        add_window = tk.Toplevel(root)
        add_window.title("Add Transaction")
        add_window.config(padx=30, pady=20, bg=COLORS["background"])  # Padding for the window

        category_var = tk.StringVar()

        category_title = ttk.Label(add_window, text="New Category:", font=FONTS["heading"])
        category_title.grid(row=0, column=1, columnspan=2, padx=25, pady=25, sticky="n")

        category_entry = ttk.Entry(add_window, textvariable=category_var)
        category_entry.grid(row=2, column=2, padx=25, pady=25, sticky="w")

        def submit_category():
            category_name = category_var.get()

            if not category_name:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            tracker.add_category(category_name)
            add_window.destroy()

        submit_button = ttk.Button(add_window, text="Create", command=submit_category, style="Custom.TButton")
        submit_button.grid(row=4, column=1, columnspan=2, padx=25, pady=25,)

    def del_category():
        # Create a new window for adding transaction
        add_window = tk.Toplevel(root)
        add_window.title("Delete Category")
        add_window.config(padx=30, pady=20, bg=COLORS["background"])  # Padding for the window

        category_var = tk.StringVar()
        categories = list(tracker.read_categories()["name"])
        placeholder = "Select a category"
        del_header = ttk.Label(add_window, text="Delete Category:", font=FONTS["heading"])
        del_header.grid(row=0, column=0, padx=25, pady=25, sticky="n")
        category_combobox = ttk.Combobox(add_window, textvariable=category_var,
                                         values=categories, state="readonly", style="Custom.TCombobox")
        category_combobox.set(placeholder)
        category_combobox.grid(row=1, column=0, padx=25, pady=25, sticky="n")

        def delete_category():
            category_name = category_var.get()
            if category_name == "Select an option":
                messagebox.showerror("Error", "Please select a valid option.")
            else:
                if not category_name:
                    messagebox.showerror("Error", "Please fill in all fields.")
                    return

                tracker.del_category(category_name)
                add_window.destroy()

        delete_button = ttk.Button(add_window, text="Delete", command=delete_category, style="Custom.TButton")
        delete_button.grid(row=2, column=0, padx=25, pady=25)

    def on_close():
        tracker.close_db()  # Close the database connection
        root.quit()

    '''
        Adding static widgets
    '''
    graph(tab2, tracker.calculate_daily_balance())
    label5 = ttk.Label(tab5, text="Edit Data", font=FONTS["heading"])
    label5.pack(pady=10)
    add_button = ttk.Button(tab5, text="Add Transaction", command=add_transaction, style="Custom.TButton")
    add_button.pack(pady=20)
    add2_button = ttk.Button(tab5, text="Add Category", command=add_category, style="Custom.TButton")
    add2_button.pack(pady=20)
    del_category_button = ttk.Button(tab5, text="Delete Category", command=del_category, style="Custom.TButton")
    del_category_button.pack(pady=20)

    '''
        Adding Dynamically changing widgets.
        Balance, Line-Plot, Bar-Plot, Table
    '''
    # Bind the event to update tabs when switched
    def on_tab_change(event):
        selected_tab = notebook.index(notebook.select())

        # Finance Overview tab index
        if selected_tab == 0:
            # Clear previous graph
            for widget in tab1.winfo_children():
                widget.destroy()

            # Create and pack a title label for the Balance section
            tab1_title = ttk.Label(tab1, text="Balance:", font=FONTS["heading"])
            tab1_title.pack(pady=50)

            # Create and pack a label that displays the current balance, retrieved from the tracker object
            balance = ttk.Label(tab1, text=f"{tracker.balance()} €", font=FONTS["subheading"])
            balance.pack(pady=10)

            # Create and pack a footer label with version information at the bottom of the tab
            footer = ttk.Label(tab1, text="Finance Tracker - Version 1.0", font=FONTS["small"])
            footer.pack(side="bottom", pady=10)

        # Finance Overview tab index
        if selected_tab == 1:
            # Clear previous graph
            for widget in tab2.winfo_children():
                widget.destroy()

            # Draw updated graph
            graph(tab2, tracker.calculate_daily_balance())

        # Expenses tab index
        elif selected_tab == 2:
            # Clear previous graph
            for widget in tab3.winfo_children():
                widget.destroy()

            # Draw updated bar plot
            bar_plot(tab3, tracker.read_expenses())

        # Table tab index
        elif selected_tab == 3:
            # Clear any existing widgets from tab4
            for widget in tab4.winfo_children():
                widget.destroy()

            # Read the transactions data
            table_data = tracker.read_transactions()

            # Create the Treeview widget for displaying the transactions
            columns = ("Date", "Category", "Amount", "Comment")
            table = ttk.Treeview(tab4, columns=columns, show="headings", height=10)

            # Define column headings and setup sort functionality
            for col in columns:
                table.heading(col, text=col, command=lambda _col=col: sort_by(table, _col, False))
                table.column(col, anchor="center", width=100)  # Adjust width as needed

            # Add a vertical scrollbar
            scrollbar = ttk.Scrollbar(tab4, orient="vertical", command=table.yview)
            table.configure(yscrollcommand=scrollbar.set)

            # Pack the table and scrollbar
            table.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            scrollbar.grid(row=0, column=1, sticky="ns")

            # Configure grid weights for proper resizing
            tab4.grid_columnconfigure(0, weight=1)
            tab4.grid_rowconfigure(0, weight=1)

            # Add the 'Delete Selected Transaction' button
            delete_button = ttk.Button(tab4, text="Delete Selected Transaction",
                                       command=lambda: delete_transaction(table), style="Custom.TButton")
            delete_button.grid(row=1, column=0, pady=10, padx=10)

            # Populate the table with data
            populate_table(table, table_data)
    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    # Properly closing the program
    root.protocol("WM_DELETE_WINDOW", on_close)
    # Run the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()
