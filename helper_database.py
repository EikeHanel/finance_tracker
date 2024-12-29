import sqlite3
import pandas as pd
from tkinter import messagebox
import datetime


class Tracker:
    def __init__(self):
        self.connection = sqlite3.connect('example.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            category_id INTEGER NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            date DATE NOT NULL,
            comment TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
        ''')
        self.connection.commit()

        if self.read_categories().empty:
            self.add_category('Income')
            self.add_category('Rent')
            self.add_category('Food')
            self.add_category('Coffee')
        if self.read_expenses().empty:
            self.add_transaction('Income', 0, str(datetime.date.today()), 'Start Value')
            self.add_transaction('Rent', 0, str(datetime.date.today()), 'Start Value')
            self.add_transaction('Food', 0, str(datetime.date.today()), 'Start Value')
            self.add_transaction('Coffee', 0, str(datetime.date.today()), 'Start Value')

    def find_id_of_category(self, category_name):
        self.cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        category_id = self.cursor.fetchone()
        if not category_id[0]:
            messagebox.showerror("Error", "Unknown Category")
            return
        else:
            return category_id[0]

    def add_transaction(self, category_name, amount, date, comment=""):
        category_id = self.find_id_of_category(category_name)
        self.cursor.execute('INSERT INTO transactions (category_id, amount, date, comment)'
                            'VALUES (?, ?, ?, ?)', (category_id, amount, date, comment))
        self.connection.commit()

    def del_transaction(self, trans_id):
        trans_id = int(trans_id)
        self.cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))
        self.connection.commit()

    def add_category(self, category_name):
        self.cursor.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
        self.connection.commit()

    def del_category(self, category_name):
        category_id = self.find_id_of_category(category_name)
        self.cursor.execute('SELECT * FROM transactions WHERE category_id = ?', (category_id,))
        transaction = self.cursor.fetchone()
        if not transaction:
            self.cursor.execute('DELETE FROM categories WHERE name = ?', (category_name,))
            self.connection.commit()
        else:
            messagebox.showerror("Error", "Category is still in use!")

    def read_categories(self):
        """
        Reads the categories table.
        :return: DataFrame
        """
        query = '''
            SELECT * FROM categories
            WHERE id != 1
        '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        column_names = [desc[0] for desc in self.cursor.description]
        df = pd.DataFrame(rows, columns=column_names)
        return df

    def read_transactions(self):
        """
        Fetch all transactions joined with categories and return as a pandas DataFrame.
        :return: DataFrame
        """
        query = '''
                    SELECT 
                        t.id, 
                        c.name AS category_name, 
                        t.amount AS amount,
                        t.date, 
                        t.comment
                    FROM 
                        transactions t
                    JOIN 
                        categories c ON t.category_id = c.id
                '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        # Get column names from the query result
        column_names = [desc[0] for desc in self.cursor.description]
        # Create a pandas DataFrame
        df = pd.DataFrame(rows, columns=column_names)
        return df

    def read_expenses(self):
        """
        Fetch all transactions (except Income) joined with categories and return as a pandas DataFrame.
        Columns: transaction_id, category_name, amount, date, comment
        :return: DataFrame
        """
        query = '''
            SELECT 
                t.id, 
                c.name AS category_name, 
                ABS(t.amount) AS amount,
                t.date, 
                t.comment
            FROM 
                transactions t
            JOIN 
                categories c ON t.category_id = c.id
            WHERE 
                c.name != 'Income';
        '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        # Get column names from the query result
        column_names = [desc[0] for desc in self.cursor.description]
        # Create a pandas DataFrame
        df = pd.DataFrame(rows, columns=column_names)
        return df

    def fetch_transactions_last_n_days(self, n_days=30):
        """
        Gets the transactions for the last n_days
        :param n_days: variable to change span of transactions
        :return: list
        """
        # Fetch all transactions within the last n_days
        query = f'''
        SELECT date, SUM(amount) as daily_amount
        FROM transactions
        WHERE date >= DATE('now', '-{n_days} day')
        GROUP BY date
        ORDER BY date;
        '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def balance_before_n_days(self, n_days=30):
        """
        Sums all transactions before n_days
        :param n_days: variable to change span of transactions
        :return: int
        """
        query = f'''
                SELECT SUM(amount) AS balance
                FROM transactions
                WHERE date <= DATE('now', '-{n_days} days');
                '''
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        balance = result[0] if result[0] is not None else 0  # Handle NULL case
        return balance

    def calculate_daily_balance(self, n_days=30):
        """
        Calculates the daily balance for last n_days counting from today
        :param n_days: variable to change span of transactions
        :return: DataFrame
        """
        transactions = self.fetch_transactions_last_n_days(n_days)
        if not transactions:
            return pd.DataFrame(columns=['date', 'balance'])

        # Start calculating the cumulative balance
        balance = self.balance_before_n_days(n_days)
        balances = []

        for date, daily_amount in transactions:
            balance += daily_amount  # Cumulative sum of daily transactions
            balances.append((date, balance))

        # Convert to a pandas DataFrame for easy plotting
        df = pd.DataFrame(balances, columns=['date', 'balance'])
        return df

    def balance(self):
        """
        Sum all transactions to get current balance
        :return: int
        """
        query = '''
            SELECT SUM(amount) FROM transactions
        '''
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        balance = round(result[0], 2) if result[0] is not None else 0  # Handle NULL case
        return balance

    def close_db(self):
        self.connection.close()



