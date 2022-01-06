#!/usr/bin/python
from tkinter import *
from tkinter.font import Font

from dao_classes import color
from main import read_choice, read_simple_text

""" Dungeons & Dragons font policies:
        Rellanic - Elvish/Sylvan/Undercommon
        Davek - Dwarvish/Giant/Gnomish/Goblin/Orc/Primordial
        Iokharic - Draconic
        Barazhad - Abyssal/Infernal
"""
font_policies = {'Rellanic', 'Davek', 'Iokharic', 'Barazhad'}

languages = {"Elvish/Sylvan/Undercommon": "Rellanic", "Dwarvish/Giant/Gnomish/Goblin/Orc/Primordial": "Davek", "Draconic": "Iokharic", "Abyssal/Infernal": "Barazhad"}

print(f'{color.PURPLE}-----------------------------------------------------------{color.END}')
print(f'{color.PURPLE} Font policy sample for language proficiencies DnD 5th edition {color.END}')
print(f'{color.PURPLE}-----------------------------------------------------------{color.END}')
language: str = read_choice('language', list(languages.keys()))
text: str = read_simple_text('Type text to translate: ')

top = Tk()
top.title(f'{text} translated in {language}')
top.geometry("500x500")


# Code to add widgets will go here...
my_font = Font(family=languages[language], size=64, weight='bold')
w = Text(top, height=1, borderwidth=0)
w.insert(1.0, text)
w.pack()
# w.configure(state="disabled")

# my_button = Button(top, text=text, font=my_font)
# my_button.pack(pady=20)
my_label = Label(top, text=text, font=my_font)
my_label.focus()
my_label.pack(pady=20)
#my_text.pack(pady=20)
top.mainloop()
