# Schaltsimulator Main buttons UI script and some side functions

from tkinter import *
from tkinter_custom_button import TkinterCustomButton

def addButtons(m, txtContent, xPos, yPos, bgC = None, fgC = "#42b029", hovC = "#377e32", txtFont = None, txtColor="black", cornerR=0, w=100, h=65, hover=True, cmdFunc=""):
    '''create buttons for upgraded design with tkintercustombutton class'''
    btn = TkinterCustomButton(
                            master=m,
                            bg_color=bgC,
                            fg_color=fgC,
                            hover_color=hovC,
                            text_font=txtFont,
                            text=txtContent,
                            text_color=txtColor,
                            corner_radius=cornerR,
                            width=w,
                            height=h,
                            hover=hover,
                            command=cmdFunc
                            )
    btn.bind_class(Button)
    btn.place(x=xPos, y=yPos)
    return btn

def addLabelPlace(master, name, text, xPos, yPos, txtFont="Century Gothic", fontSize=30, bd=0, h=0, w=0, fg="black", bg="white"):
    '''create labels for upgraded design as place function with tkintercustombutton class'''
    name = Label(
                master, 
                text=text, 
                font=(txtFont, fontSize),
                bd=bd, 
                height=h, 
                width=w, 
                fg=fg, 
                bg=bg
                )
    name.place(x = xPos, y= yPos)
    return name

def addLabelPack(master, name, text, anchor, side, txtFont="Century Gothic", fontSize=30, bd=0, h=0, w=0, fg="black", bg="white"):
    '''create labels for upgraded design as pack function with tkintercustombutton class'''
    name = Label(
                master, 
                text=text, 
                font=(txtFont, fontSize),
                bd=bd, 
                height=h, 
                width=w, 
                fg=fg, 
                bg=bg
                )
    name.pack(anchor=anchor, side=side)
    return name