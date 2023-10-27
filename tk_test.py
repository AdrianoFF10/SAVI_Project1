
import tkinter as tk
from tkinter import PhotoImage


'''
def save_input():
    global user_input
    user_input = entry.get()
    root.destroy()

user_input = ""

root = tk.Tk()

root.title("Welcome to LikeGeeks app")

root.geometry('350x100')

root.title("Input Saver")

label = tk.Label(root, text="Enter some text:")
label.pack()

entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text="Save and Close", command=save_input)
button.pack()

root.mainloop()

print("User input:", user_input)
'''
import cv2
import tkinter as tk
from PIL import Image, ImageTk

def save_input():
    global user_input
    user_input = entry.get()
    root.destroy()

user_input = ""

root = tk.Tk()
root.title("Input Saver")

# Carregar a imagem com o Pillow e convertê-la para um formato adequado
image = Image.open('Database/hh.jpg')
image = ImageTk.PhotoImage(image)

image_label = tk.Label(root, image=image)
image_label.pack()

label = tk.Label(root, text="Enter some text:")
label.pack()

entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text="Save and Close", command=save_input)
button.pack()

root.mainloop()

print("User input:", user_input)

