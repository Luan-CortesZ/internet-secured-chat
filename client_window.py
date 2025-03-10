import tkinter as tk
from tkinter import scrolledtext, ttk

#Graphics inteface with title
root = tk.Tk()
root.title("ISC Client")

#Text zone to display messages
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, width=50, height=15)
chat_box.pack(padx=10, pady=10)

#Combobox to chose correct message type
input_type_field = ttk.Combobox(root, width = 7, state="readonly")
input_type_field.pack(padx=10, pady=5, anchor="w", side="left")
input_type_field["values"] = ('User', 'Server', 'Image')
input_type_field.current(0)

#Input text
input_text_field = tk.Entry(root, width=40)
input_text_field.pack(padx=10, pady=5, anchor="w", side="left")

#Sending buttons
send_button = tk.Button(root, text="Send")
send_button.pack(pady=5, side="left")

def get_input_value():
    """
    Get user value in input text
    """
    return input_text_field.get()

def set_input_value(text):
    """
    Set input value by text in parameter
    """
    input_text_field.insert(0,text)

def get_type_value():
    """
    Get type selected by user
    """
    return input_type_field.get()

def show_window(send_callback):
    """
    Show window to user
    """
    input_text_field.bind("<Return>", send_callback)
    send_button.config(command=send_callback)
    root.mainloop()

def reset_field():
    """
    Reset field 
    """
    input_text_field.delete(0, tk.END) 

def write_in_box(user, text):
    """
    Write data in box with prefix 'user' and message 'text'
    """
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"{user} {text}\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)