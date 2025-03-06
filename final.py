import tkinter as tk
from tkinter import messagebox
import psycopg2
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import smtplib
from email.message import EmailMessage
from io import BytesIO
import re  # For email validation

matplotlib.use("TkAgg")  # Force use of Tkinter backend for Matplotlib

# Database connection
conn = psycopg2.connect(
    dbname="tnvote",
    user="postgres",
    password="     ",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create tables if they do not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    party VARCHAR(100) NOT NULL
);
""")
conn.commit()

# Function to validate email format
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email)

# Function to send a "Thank you for voting" email
def send_thank_you_email(user_email):
    sender_email = "electioncommission12345@gmail.com"  # Replace with your Gmail
    sender_password = "ehateainwevfpeug" # Use your generated App Password

    # Create the email
    msg = EmailMessage()
    msg.set_content("Thank you for voting! Your vote has been recorded. Results will be announced on 04-03-2025.")

    msg["Subject"] = "Thank You for Voting"
    msg["From"] = sender_email
    msg["To"] = user_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Thank you email sent successfully!")  # For debugging purposes
    except Exception as e:
        print(f"Failed to send thank you email: {e}")  # For debugging purposes

# Function to send email with election results
def send_results_email():
    sender_email = "electioncommission12345@gmail.com"  # Replace with your Gmail
    sender_password = "ehateainwevfpeug"  # Use your generated App Password
    recipient_email = "ulaganathank38@gmail.com"  # Replace with recipient's email

    # Fetch election results
    cursor.execute("SELECT party, COUNT(*) FROM votes GROUP BY party")
    results = cursor.fetchall()

    if not results:
        messagebox.showerror("Error", "No votes have been cast yet!")
        return

    # Create a pie chart
    parties = [row[0] for row in results]
    counts = [row[1] for row in results]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts, labels=parties, autopct='%1.1f%%', startangle=140, colors=['red', 'blue', 'green', 'yellow'])
    ax.set_title("Election Results")

    # Save the pie chart to a BytesIO object
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png')
    plt.close(fig)
    chart_buffer.seek(0)

    # Create the email
    msg = EmailMessage()
    msg.set_content("Here are the election results!")

    msg["Subject"] = "Election Results"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    # Attach the pie chart image
    msg.add_attachment(chart_buffer.getvalue(), maintype="image", subtype="png", filename="election_results.png")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        messagebox.showinfo("Success", "Email sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")

# Function to count votes and display in pie chart
def show_results():
    # Check if the result window is already open
    if hasattr(root, 'result_window') and root.result_window.winfo_exists():
        return

    cursor.execute("SELECT party, COUNT(*) FROM votes GROUP BY party")
    results = cursor.fetchall()

    if not results:
        messagebox.showinfo("Results", "No votes have been cast yet!")
        return

    # Create a new window for results
    root.result_window = tk.Toplevel(root)
    root.result_window.title("Election Results")
    root.result_window.geometry("1000x800")
    root.result_window.resizable(False, False)  # Prevent maximizing the window

    # Load background image
    bg_image_path = "C:\\Users\\ulaganathan\\OneDrive\\Desktop\\arith\\rbg.jpg"  # Change this to your actual image path
    bg_image = Image.open(bg_image_path)
    bg_image = bg_image.resize((1000, 800))
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Create a canvas for the background image
    canvas = tk.Canvas(root.result_window, width=1000, height=800)
    canvas.pack(fill="both", expand=True)  # Fill the entire window
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Keep a reference to the background image to prevent garbage collection
    root.result_window.bg_photo = bg_photo

    # Extract data for the pie chart
    parties = [row[0] for row in results]
    counts = [row[1] for row in results]

    # Calculate total votes
    total_votes = sum(counts)

    # Find the winning party
    winning_party = parties[counts.index(max(counts))]

    # Create a pie chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts, labels=parties, autopct='%1.1f%%', startangle=140, colors=['red', 'blue', 'green', 'yellow'])
    ax.set_title("Election Results")

    # Embed the pie chart into the Tkinter window
    chart_canvas = FigureCanvasTkAgg(fig, master=root.result_window)
    chart_canvas.draw()
    chart_canvas.get_tk_widget().place(relx=0.5, rely=0.4, anchor="center")  # Center the pie chart

    # Display total votes and winning party
    result_text = f"Total Votes: {total_votes}\n\n"
    for party, count in zip(parties, counts):
        result_text += f"{party}: {count} votes\n"
    result_text += f"\nWinning Party: {winning_party}"

    result_label = tk.Label(root.result_window, text=result_text, font=("Arial", 16), bg="white")
    result_label.place(relx=0.5, rely=0.75, anchor="center")  # Position the label below the chart

    # Add a button to send results via email
    send_button = tk.Button(root.result_window, text="Send Results via Email", font=("Arial", 16), command=send_results_email)
    send_button.place(relx=0.5, rely=0.9, anchor="center")  # Position the button below the chart

    # Close the matplotlib figure to free memory
    plt.close(fig)

# Voting Window Function
def voting_window(username):
    vote_win = tk.Toplevel(root)  # Use Toplevel to avoid multiple root windows
    vote_win.title("Vote for your Party")
    vote_win.geometry("800x800")
    vote_win.resizable(False, False)  # Prevent maximizing the window

    # Load background image
    bg_image_path = "C:\\Users\\ulaganathan\\OneDrive\\Desktop\\arith\\voting.jpg"  # Change this to your actual background image path
    bg_image = Image.open(bg_image_path)
    bg_image = bg_image.resize((800, 800))
    bg_photo = ImageTk.PhotoImage(bg_image)

    canvas = tk.Canvas(vote_win, width=800, height=800)
    canvas.pack(fill="both", expand=True)  # Fill the entire window
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    parties = ["TVK", "DMK", "ADMK", "NOTA"]
    party_images = ["C:\\Users\\ulaganathan\\Downloads\\tvk.jpg",
                    "C:\\Users\\ulaganathan\\Downloads\\dmk.png",
                    "C:\\Users\\ulaganathan\\Downloads\\admk.png",
                    "C:\\Users\\ulaganathan\\Downloads\\nota.jpg"]

    images = []  # Store image references to prevent garbage collection

    def cast_vote(party):
        cursor.execute("SELECT * FROM votes WHERE username=%s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "You have already voted!")
            return

        cursor.execute("INSERT INTO votes (username, party) VALUES (%s, %s)", (username, party))
        conn.commit()
        messagebox.showinfo("Success", "Vote Cast Successfully")

        # Fetch the user's email from the database
        cursor.execute("SELECT email FROM users WHERE username=%s", (username,))
        user_email = cursor.fetchone()[0]

        # Send a thank you email to the user
        send_thank_you_email(user_email)

        vote_win.destroy()

    # Vertical positioning of buttons
    for i, party in enumerate(parties):
        img = Image.open(party_images[i])
        img = img.resize((100, 100))  # Resize image
        img = ImageTk.PhotoImage(img)

        images.append(img)  # Keep reference to prevent garbage collection

        btn = tk.Button(vote_win, image=img, text=party, compound="top",
                        font=("Arial", 18), command=lambda p=party: cast_vote(p))
        btn_window = canvas.create_window(350, 100 + i * 150, anchor="nw", window=btn)  # Adjusted y-coordinate for vertical layout

    # Keep a reference to the background image to prevent garbage collection
    vote_win.bg_photo = bg_photo

    vote_win.mainloop()

# Login Function
def login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "admin" and password == "result2025":
        messagebox.showinfo("Admin Login", "Admin login successful")
        show_results()
        return

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Login", "Login Successful")
        voting_window(username)
    else:
        messagebox.showerror("Error", "Invalid Credentials")

# Register Function
def register():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    email = email_entry.get().strip()

    if not username or not password or not email:
        messagebox.showerror("Error", "All fields are required!")
        return

    if not is_valid_email(email):
        messagebox.showerror("Error", "Invalid email format!")
        return

    try:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        conn.commit()
        messagebox.showinfo("Registration", "Registered Successfully!")
        login_page()  # Redirect to login page after registration
    except psycopg2.IntegrityError:
        conn.rollback()
        messagebox.showerror("Error", "Username or email already exists!")

# Function to create the registration page
def registration_page():
    for widget in right_frame.winfo_children():
        widget.destroy()

    tk.Label(right_frame, text="Username", font=("Arial", 18), bg="snow3").pack(pady=10)
    global username_entry
    username_entry = tk.Entry(right_frame, font=("Arial", 18))
    username_entry.pack(pady=10)

    tk.Label(right_frame, text="Password", font=("Arial", 18), bg="snow3").pack(pady=10)
    global password_entry
    password_entry = tk.Entry(right_frame, show="*", font=("Arial", 18))
    password_entry.pack(pady=10)

    tk.Label(right_frame, text="Email", font=("Arial", 18), bg="snow3").pack(pady=10)
    global email_entry
    email_entry = tk.Entry(right_frame, font=("Arial", 18))
    email_entry.pack(pady=10)

    tk.Button(right_frame, text="Register", font=("Arial", 15),bg="snow2", command=register).pack(pady=10)
    tk.Button(right_frame, text="Already have an account? Login",bg="snow2", font=("Arial", 14), command=login_page).pack(pady=10)

# Function to create the login page
def login_page():
    for widget in right_frame.winfo_children():
        widget.destroy()

    tk.Label(right_frame, text="Username", font=("Arial", 18), bg="snow3").pack(pady=10)
    global username_entry
    username_entry = tk.Entry(right_frame, font=("Arial", 18))
    username_entry.pack(pady=10)

    tk.Label(right_frame, text="Password", font=("Arial", 18), bg="snow3").pack(pady=10)
    global password_entry
    password_entry = tk.Entry(right_frame, show="*", font=("Arial", 18))
    password_entry.pack(pady=10)

    tk.Button(right_frame, text="Login", font=("Arial", 12),bg="snow2", command=login).pack(pady=10)
    tk.Button(right_frame, text="Admin Login", font=("Arial", 12),bg="snow2", command=admin_login).pack(pady=10)
    tk.Button(right_frame, text="Don't have an account? Register",bg="snow2", font=("Arial",14), command=registration_page).pack(pady=10)

# Admin Login Function
def admin_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "admin" and password == "result2025":
        messagebox.showinfo("Admin Login", "Admin login successful")
        show_results()
    else:
        messagebox.showerror("Error", "Invalid Admin Credentials")

# Main Window
root = tk.Tk()
root.title("Voting System")
root.geometry("1000x600")
root.resizable(False, False)  # Prevent maximizing the window

# Load background image
bg_image_path = "C:\\Users\\ulaganathan\\OneDrive\\Desktop\\arith\\registration.jpg"  # Change this to your actual image path
bg_image = Image.open(bg_image_path)
bg_image = bg_image.resize((700, 700))  # Resize image to fit the left half of the window
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a canvas for the background image and place it on the left side
left_canvas = tk.Canvas(root, width=700, height=700)
left_canvas.pack(side="left", fill="both", expand=True)
left_canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Create a frame for the login/register form and place it on the right side
right_frame = tk.Frame(root, bg="snow3")  # Set background color for the right frame
right_frame.pack(side="right", fill="both", expand=True)

# Start with the login page
login_page()

# Keep a reference to the background image to prevent garbage collection
root.bg_photo = bg_photo

root.mainloop()