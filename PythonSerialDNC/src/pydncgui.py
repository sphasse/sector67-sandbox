#$Id: interface.py,v 1.1 2004/03/18 05:44:21 mandava Exp $
#This is a program which combines  menubar, text area and file browser  
#into a single interface.
#

from Tkinter import *

from tkFileDialog import askopenfilename
class mywidgets:
    def __init__(self,root):
        frame=Frame(root)
        self.makeMenuBar(frame)
        self.txtfr(frame)
        frame.pack()
        return
    #defines the text area
    def txtfr(self,frame):
        textfr = Frame(frame)
        self.text = Text(textfr,height = 10,width = 50,background='white')
        scroll = Scrollbar(textfr)
        self.text.configure(yscrollcommand = scroll.set)
        self.text.pack(side = LEFT)
        scroll.pack(side = RIGHT,fill = Y)
        textfr.pack(side = TOP)
        return
    #defines menubar
    def makeMenuBar(self,frame):
        menubar = Frame(frame,relief = RAISED,borderwidth = 1)
        menubar.pack()
        mb_file = Menubutton(menubar,text = 'file')
        mb_file.pack(side = LEFT)
        mb_file.menu = Menu(mb_file)
        mb_file.menu.add_command(label = 'open',command = self.file_open)
        mb_edit = Menubutton(menubar,text = 'edit')
        mb_edit.pack(side = LEFT)
        mb_edit.menu = Menu(mb_edit)
        mb_edit.menu.add_command(label = 'copy')
        mb_help = Menubutton(menubar,text = 'help')
        mb_help.pack(padx = 25,side = RIGHT)
        mb_file['menu'] = mb_file.menu
        mb_edit['menu'] = mb_edit.menu
        return
    #defines file_open which is called when file option openis choosen
    #displays the files giving the user choice to choose  file
    def file_open(self):
        filename =askopenfilename(filetypes=[("allfiles","*"),("pythonfiles","*.py")])
        print filename
        


def main():
    root = Tk()
    k = mywidgets(root)
    root.title('interface')
    root.mainloop()
main()
