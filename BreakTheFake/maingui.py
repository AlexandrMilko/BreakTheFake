#!/usr/bin/python
import tkinter
from tkinter import *
from main import check_fake, installJ


if __name__ == "__main__":
    installJ()

root = Tk()
root.title("Break the Fake")
root.configure(background="white")
root.geometry('1920x1080')

window = Tk()

label = Label(text='FAKE CHECKER BY KAKOWY CHLEBICHEK',foreground='#000000', background='#FFFFFF', font='Times 45 bold')

label.place(relx=0.5, rely=0.1, anchor=N)
entry = Entry(width=150)
entry.place(relx=0.5, rely=0.3, anchor=N)
link = ''
def openNewWindow():
    link = entry.get()
    new_windows = Toplevel(root)
    new_windows.title('info')
    new_windows.configure(background="white")
    new_windows.geometry('1920x1080')
    label = Label(new_windows, text = "Chance of fake: "+str(check_fake(link)),  foreground='#000000', background='#FFFFFF',
                  font='Times 35 bold')
    label.place(relx=0.5, rely=0.1, anchor=N)
btn = Button(root, text='CHEKER', bg='white', fg='black', foreground='#000000', background='#FFFFFF', font='Times 20 bold', command=openNewWindow)
btn.place(relx=0.5, rely=0.5, anchor=CENTER)




out = Label(height=2, width=25)



root.mainloop()
