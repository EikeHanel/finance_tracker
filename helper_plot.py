import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def bar_plot(canvas_frame, df):
    """
    Embed a bar plot in the given tkinter frame.
    """
    df = df.groupby(by='category_name', as_index=False).sum()
    df = df.sort_values(by='amount', ascending=True)
    fig, ax = plt.subplots(figsize=(6, 4))  # Create the figure and axes
    ax.barh(y=df['category_name'], width=df['amount'], color='skyblue', edgecolor='black')
    ax.set_xlabel('Total Amount')
    ax.set_title('Total Spending by Category')
    ax.set_xlim(0)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


def graph(canvas_frame, df_trans):
    """
    Embed a line graph in the given tkinter frame.
    """
    # Change str-date into datetime-date
    df_trans['date'] = pd.to_datetime(df_trans['date'])

    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    ax.plot(df_trans["date"], df_trans["balance"], marker='o', color='orange', label='Line Graph')
    ax.set_title("Balance Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance")
    ax.tick_params(axis='x', rotation=45)
    ax.autoscale(axis='x', tight=True)
    # Format the x-axis to display the dates better
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    ax.grid(alpha=0.5)

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
