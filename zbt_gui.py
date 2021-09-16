import tkinter as tk
import tkinter.font as tkFont

# gui class parameters - software version
version, year = 0.1, 2021
author = 'JKP'

# gui classes
class ZBTframe(tk.Frame):

    def __init__(self, rows, columns, height=500, width=400, bg='grey20', master=None):
        tk.Frame.__init__(self, master)
        self.config(bg=bg, width=width, height=height)

        for r in range(rows):
            self.grid_rowconfigure(r, weight=1)

        for c in range(columns):
            self.grid_columnconfigure(c, weight=1)

class ZBTbutton(tk.Button):

    def __init__(self, font_spec=None, font_size=None, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self.config(bg='lightgrey', font=ZBTfont(spec=font_spec, size=font_size))

class ZBTwindow(tk.Tk):

    def __init__(self, name, rows=1, columns=1, x_dim=500, y_dim=400):
        tk.Tk.__init__(self)
        self.title(name)
        self.geometry('{}x{}'.format(x_dim, y_dim))
        self.config(bg='lightgrey')
        self.iconbitmap('zbt_logo.ico')
        self.rows = rows
        self.columns = columns
        self.y_dim = y_dim
        self.x_dim = x_dim

        # self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.top = ZBTframe(rows, columns, height=(y_dim - 20), width=x_dim, master=self)
        self.top.grid_propagate(0)
        self.bot = ZBTframe(1, 1, height=20, width=x_dim, bg='grey25', master=self)
        self.bot.grid_propagate(0)

        self.top.grid(row=0, column=0, sticky='nesw')
        self.bot.grid(row=1, column=0, sticky='nesw')

        self.footnote = 'Ver.: ' + str(version) + ' (' + str(year) + ') by ' + \
                        author
        self.sub_foot_r = tk.Label(self.bot, text=self.footnote, bg='grey25',
                             fg='snow')
        self.sub_foot_r.grid(row=0, column=0, sticky='e')

    def set_dbstatus(self, subtext, color):
        self.sub_foot_l = tk.Label(self.bot, text=subtext, bg='grey25', fg=color)
        self.sub_foot_l.grid(row=0, column=0, sticky='w')

class ZBTtoplevel(tk.Toplevel):

    def __init__(self, name, rows, columns, x_dim=1250, y_dim=1000, canvas=False, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.config(bg='grey20')
        self.title(name)
        self.geometry('{}x{}'.format(x_dim, y_dim))
        self.iconbitmap('zbt_logo.ico')

        col = 10
        for i in range(col):
            self.columnconfigure(i, weight=1)

        row = 2
        for i in range(row):
            self.rowconfigure(i, weight=1)

        if canvas is True:

            self.rowconfigure(2, weight=1)
            self.sub_top = ZBTframe(rows, columns, height=(y_dim-20)/4*1, width=x_dim, master=self)
            self.sub_top.grid_propagate(0)
            # self.sub_left = ZBTframe(rows, 3, master=self)
            # self.sub_left.grid_propagate(0)
            self.sub_canvas = ZBTframe(rows, 10, width=x_dim, master=self, bg='blue')
            self.sub_canvas.grid_propagate(0)
            self.sub_bot = ZBTframe(1, 1, height=20, width=x_dim, bg='grey25', master=self)
            self.sub_bot.grid_propagate(0)

            self.sub_top.grid(row=0, column=0, columnspan=10, sticky='news')
            # self.sub_left.grid(row=1, column=0, sticky='ns')
            self.sub_canvas.grid(row=1, column=0, columnspan=10, sticky='news')
            self.sub_bot.grid(row=2, column=0, columnspan=10, sticky='ew')

        else:
            self.sub_top = ZBTframe(rows, columns, height=(y_dim - 20), width=x_dim, master=self)
            self.sub_top.grid_propagate(0)
            self.sub_bot = ZBTframe(1, 1, height=20, width=x_dim, bg='grey25', master=self)
            self.sub_bot.grid_propagate(0)
            self.sub_top.grid(row=0, column=0, columnspan=4, sticky='news')
            self.sub_bot.grid(row=1, column=0, columnspan=4, sticky='news')

        self.sub_footnote = 'Ver.: ' + str(version) + ' (' + str(year) + ') by ' + \
                        author
        self.sub_foot_r = tk.Label(self.sub_bot, text=self.sub_footnote, bg='grey25', fg='snow')
        self.sub_foot_r.grid(row=0, column=0, sticky='e')

    def set_dbstatus(self, subtext, color):
        self.sub_foot_l = tk.Label(self.sub_bot, text=subtext, bg='grey25', fg=color)
        self.sub_foot_l.grid(row=0, column=0, sticky='w')

    def set_file(self, file):
        filename = file.split('/')[-1][:-4]
        self.sub_foot_l = tk.Label(self.sub_bot, text=filename, bg='grey25', fg='snow')
        self.sub_foot_l.grid(row=0, column=0, sticky='w')

class ZBTlabel(tk.Label):

    def __init__(self, font_size=None, font_spec=None, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.config(font=ZBTfont(spec=font_spec, size=font_size), bg='grey20', fg='#0063b4')

class ZBTfont(tkFont.Font):
    def __init__(self, spec=None, size=None, *args, **kwargs):
        tkFont.Font.__init__(self, *args, **kwargs)
        if spec == 'header':
            if size is None:
                self.config(family="Verdana", size=20, weight="bold", slant="roman")
            else:
                self.config(family="Verdana", size=size, weight="bold", slant="roman")
        if spec is None:
            if size is None:
                self.config(family="Verdana", size=10, weight="normal", slant="roman")
            else:
                self.config(family="Verdana", size=size, weight="normal", slant="roman")

class ZBTentry(tk.Entry):

    def __init__(self, text=None, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)
        self.config(bg='grey30', font=ZBTfont, bd=5)
        if text is not None:
            self.insert(0, text)