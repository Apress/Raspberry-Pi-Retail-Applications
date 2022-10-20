import tkinter as tk

win = tk.Tk()
win.resizable(width=False, height=False) # Disallow resizing of window 
win.title('Tkinter Hello World Demo') # Set title bar text 
win.geometry('320x240') # Set window size 

Label = tk.Label(win, text='Hello Tkinter',
                bg='blue', fg='white', 
                relief='raised', anchor='nw').place(x = 100, y = 60)

Button = tk.Button(win, command=win.quit, text='Quit', bg='orange', width=10).place(x = 100, y = 100)

win.bind('<Button-1>', win.quit)

win.mainloop()