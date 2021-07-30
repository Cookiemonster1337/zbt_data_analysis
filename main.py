import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import tkinter.filedialog
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
from matplotlib.figure import Figure
import matplotlib.gridspec

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

version, year = 0.1, 2021
author = 'JKP'


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
        self.foot = tk.Label(self.bot, text=self.footnote, bg='grey25',
                             fg='snow')
        self.foot.grid(row=0, column=0, sticky='e')

class ZBTtoplevel(tk.Toplevel):

    def __init__(self, name, rows, columns, x_dim=1000, y_dim=800, canvas=False, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.config(bg='grey20')
        self.title(name)
        self.geometry('{}x{}'.format(x_dim, y_dim))
        self.iconbitmap('zbt_logo.ico')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)



        if canvas is True:

            self.rowconfigure(2, weight=1)
            self.sub_top = ZBTframe(rows, columns, height=(y_dim-20)/4*1, width=x_dim, master=self)
            self.sub_top.grid_propagate(0)
            self.sub_left = ZBTframe(rows, 3, height=(y_dim-20)/4*3, width=x_dim/4*1, master=self)
            self.sub_left.grid_propagate(0)
            self.sub_canvas = ZBTframe(rows, 7, height=(y_dim-20)/4*3, width=x_dim/4*3, master=self, bg='blue')
            self.sub_canvas.grid_propagate(0)
            self.sub_bot = ZBTframe(1, 1, height=20, width=x_dim, bg='grey25', master=self)
            self.sub_bot.grid_propagate(0)

            self.sub_top.grid(row=0, column=0, columnspan=4, sticky='news')
            self.sub_left.grid(row=1, column=0, sticky='news')
            self.sub_canvas.grid(row=1, column=1, columnspan=3, sticky='news')
            self.sub_bot.grid(row=2, column=0, columnspan=4, sticky='news')

        else:
            self.sub_top = ZBTframe(rows, columns, height=(y_dim - 20), width=x_dim, master=self)
            self.sub_top.grid_propagate(0)
            self.sub_bot = ZBTframe(1, 1, height=20, width=x_dim, bg='grey25', master=self)
            self.sub_bot.grid_propagate(0)
            self.sub_top.grid(row=0, column=0, columnspan=4, sticky='news')
            self.sub_bot.grid(row=1, column=0, columnspan=4, sticky='news')

        self.sub_footnote = 'Ver.: ' + str(version) + ' (' + str(year) + ') by ' + \
                        author
        self.sub_foot = tk.Label(self.sub_bot, text=self.sub_footnote, bg='grey25',
                             fg='snow')
        self.sub_foot.grid(row=0, column=0, sticky='e')

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


main = ZBTwindow('Data Analysis', rows=10, columns=3)
rootpath = Path('C:/Users/Kapp/Desktop/database/')

def buttonevent(subwindow, plotter=None):
    analysis = ZBTtoplevel(master=main, canvas=True, name=subwindow, rows=10, columns=10)

    sub_b1 = ZBTbutton(master=analysis.sub_top, text='Import', command=lambda: get_file(analysis))
    sub_b1.grid(row=0, column=0, sticky='news', padx=10, pady=10)

    #data dropdown
    df_lib = pd.read_csv(str(rootpath) + '/database_poldata/poldata.csv', delimiter='\t')
    measurement_name = df_lib['sample'].unique()

    var = tk.StringVar(main)
    var.set(measurement_name[0])
    option = tk.OptionMenu(analysis.sub_top, var, *measurement_name, command=lambda _: plotter_pol(var, df_lib,
                                                                                                   plotter_canvas,
                                                                                                   fig_ax1))
    option.grid(row=0, column=2, columnspan=6, sticky='ew', padx=10, pady=10)

    #plotting
    plotter_fig = Figure()
    plotter_fig.set_facecolor('lightgrey')
    plotter_fig.set_edgecolor('black')
    grid = plotter_fig.add_gridspec(10, 10)

    fig_ax1 = plotter_fig.add_subplot(grid[:10, :10])
    fig_ax1.set_title('POL-Curve', pad=10, fontdict=dict(fontsize=18, weight='bold'))

    plotter_canvas = FigureCanvasTkAgg(plotter_fig, master=analysis.sub_canvas)
    plotter_canvas.get_tk_widget().configure(bg='red')
    plotter_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def plotter_pol(dropdown_var, df, canvas, subf1):
        x_values = np.asarray(df['current [A]'])
        y_values = np.asarray(df['voltage [V]'])
        y2_values = np.asarray(df['power [W]'])

        subf1.plot(x_values, y_values, 'rs--', label=str(dropdown_var))
        subf1.legend(loc='best')
        subf1.set_xlabel('Current [A]')
        subf1.set_ylabel('Voltage[V]')

        subf2 = subf1.twinx()
        subf2.plot(x_values, y2_values, 'ks--')
        subf2.set_ylabel('Power [W]')

        canvas.draw()

    analysis.mainloop()

def get_file(frame):
    filename = \
        tk.filedialog.askopenfilename(parent=frame, initialdir="C:/Users/Kapp/Desktop/exp_data", title="Select file",
                                      filetypes=(("all files", "*.*"), ("Text files", "*.txt")))
    import_poldata(filename)

def save_poldata(file, frame, entries):
    df_input = pd.read_csv(file, sep='\t', decimal='.', encoding='cp1252', error_bad_lines=False)
    pol_data = {'sample': entries[0], 'date': entries[1], 'info': entries[6], 'current [A]': df_input['I [A]'],
                'voltage [V]': df_input['U [V]'], 'area [cm^2]': int(entries[2]), 'flow_rate_C [l/min]': entries[3],
                'flow_rate_A [l/min]': entries[4], 'Temperature [Cel.]': entries[5]}
    df_pol_data = pd.DataFrame(pol_data)
    df_pol_data['current density [A/cm^2]'] = df_pol_data['current [A]'] / df_pol_data['area [cm^2]']
    df_pol_data['power [W]'] = df_pol_data['voltage [V]'] * df_pol_data['current [A]']
    df_pol_data['power density [W]'] = df_pol_data['voltage [V]'] * df_pol_data['current density [A/cm^2]']
    pd.set_option('display.max_columns', None)

    filename = str(entries[0]) + '.csv'
    df_pol_data.to_csv(str(rootpath) + '/database_poldata/' + filename, mode='w', header=True, index=False, sep='\t')
    df_pol_data.to_csv(str(rootpath) + '/database_poldata/poldata.csv', mode='a', index=False, sep='\t')
    # # save eis data to excel
    # wb_path = str(rootpath) + '/QMS_data/qms_data_library.xlsx'
    # book = load_workbook(wb_path)
    # writer = pd.ExcelWriter(wb_path, engine='openpyxl')
    # writer.book = book
    # df_qms.to_excel(writer, sheet_name=filename, index=False)
    # writer.save()
    # writer.close()

    frame.destroy()

    verify_import(df_pol_data, entries)

def verify_import(df, entries):

    x_values = np.asarray(df['current [A]'])
    y_values = np.asarray(df['voltage [V]'])
    y2_values = np.asarray(df['power [W]'])

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, 'rs--')

    # plt.plot(x_values, y_values, 'rs--')
    # plt.plot(x_values, y2_values, 'ks--')
    title = 'POL-Curve - ' + str(entries[0]) + ' (C: ' + str(entries[3]) +  ' / A: ' + \
            str(entries[4]) + '/ T: ' + str(entries[5]) + ')'
    ax.set_title(title)
    ax.set_xlabel('Current [A]')
    ax.set_ylabel('Voltage [V]')
    ax2 = ax.twinx()
    ax2.plot(x_values, y2_values, 'ks--')
    ax2.set_ylabel('Power [W]')

    plt.show()



def data_check(frame, file, e1, e2, e3, e4, e5, e6, e7):

    entries = [e1, e2, e3, e4, e5, e6, e7]

    if '' in entries:
            messagebox.showinfo(parent=frame, title="Data Error", message="Incomplete Data!!!")
    else:
        save_poldata(file, frame, entries)


def import_poldata(file):
    pol_import = ZBTtoplevel('Import POL-Data', rows=12, columns=3, x_dim=500, y_dim=400)

    l_head = ZBTlabel(master=pol_import.sub_top, font_spec='header', text='POL Data-Import')
    l_head.grid(row=0, column=0, columnspan=3, sticky='news')

    l1_pol_imp = ZBTlabel(master=pol_import.sub_top, font_spec='header', font_size=16, text='Sample:')
    l1_pol_imp.grid(row=3, column=0, sticky='nws')

    l2_pol_imp = ZBTlabel(master=pol_import.sub_top, font_spec='header', font_size=16, text='Date:')
    l2_pol_imp.grid(row=4, column=0, sticky='nws')

    l3_pol_imp = ZBTlabel(master=pol_import.sub_top, font_spec='header', font_size=16, text='Area')
    l3_pol_imp.grid(row=5, column=0, sticky='nws')

    l4_pol_imp = ZBTlabel(master=pol_import.sub_top, font_spec='header', font_size=16, text='FlowRate (C)')
    l4_pol_imp.grid(row=6, column=0, sticky='nws')#

    l5_pol_imp = ZBTlabel(master=pol_import.sub_top, font_spec='header', font_size=16, text='FlowRate (A)')
    l5_pol_imp.grid(row=7, column=0, sticky='nws')

    l6_pol_imp = ZBTlabel(master=pol_import.sub_top, font_spec='header', font_size=16, text='Temperature')
    l6_pol_imp.grid(row=8, column=0, sticky='nws')

    l7_pol_imp = ZBTlabel(master=pol_import.sub_top, font_spec='header', font_size=16, text='Opt. Info:')
    l7_pol_imp.grid(row=9, column=0, sticky='nws')

    l02_pol_imp = ZBTlabel(master=pol_import.sub_top, font_size=16, text='dd.mm.yyyy')
    l02_pol_imp.grid(row=4, column=2, sticky='nes')

    l03_pol_imp = ZBTlabel(master=pol_import.sub_top, font_size=16, text='cm²')
    l03_pol_imp.grid(row=5, column=2, sticky='nes')

    l04_pol_imp = ZBTlabel(master=pol_import.sub_top, font_size=16, text='l/min')
    l04_pol_imp.grid(row=6, column=2, sticky='nes')

    l05_pol_imp = ZBTlabel(master=pol_import.sub_top, font_size=16, text='l/min')
    l05_pol_imp.grid(row=7, column=2, sticky='nes')

    l06_pol_imp = ZBTlabel(master=pol_import.sub_top, font_size=16, text='°C')
    l06_pol_imp.grid(row=8, column=2, sticky='nes')

    e1_pol_imp = ZBTentry(master=pol_import.sub_top)
    e1_pol_imp.grid(row=3, column=1, sticky='news')

    e2_pol_imp = ZBTentry(master=pol_import.sub_top)
    e2_pol_imp.grid(row=4, column=1, sticky='news')

    e3_pol_imp = ZBTentry(master=pol_import.sub_top)
    e3_pol_imp.grid(row=5, column=1, sticky='news')

    e4_pol_imp = ZBTentry(master=pol_import.sub_top)
    e4_pol_imp.grid(row=6, column=1, sticky='news')

    e5_pol_imp = ZBTentry(master=pol_import.sub_top)
    e5_pol_imp.grid(row=7, column=1, sticky='news')

    e6_pol_imp = ZBTentry(master=pol_import.sub_top)
    e6_pol_imp.grid(row=8, column=1, sticky='news')

    e7_pol_imp = ZBTentry(master=pol_import.sub_top)
    e7_pol_imp.grid(row=9, column=1, sticky='news')

    b1_pol_imp = ZBTbutton(master=pol_import.sub_top, text='OK', command=lambda: data_check(pol_import, file,
                                                                                            e1_pol_imp.get(),
                                                                                            e2_pol_imp.get(),
                                                                                            e3_pol_imp.get(),
                                                                                            e4_pol_imp.get(),
                                                                                            e5_pol_imp.get(),
                                                                                            e6_pol_imp.get(),
                                                                                            e7_pol_imp.get()))
    b1_pol_imp.grid(row=11, column=1, sticky='news')

    pol_import.mainloop()


b1 = ZBTbutton(master=main.top, text='POL', command=lambda: buttonevent('POL-Analysis', plotter='pol'))
b2 = ZBTbutton(master=main.top, text='EIS', command=lambda: buttonevent('EIS-Analysis'))
b3 = ZBTbutton(master=main.top, text='MS', command=lambda: buttonevent('MS-Analysis'))
b4 = ZBTbutton(master=main.top, text='ECR', command=lambda: buttonevent('ECR-Analysis'))

b1.grid(row=1, column=1, sticky='news', padx=10, pady=10)
b2.grid(row=2, column=1, sticky='news', padx=10, pady=10)
b3.grid(row=3, column=1, sticky='news', padx=10, pady=10)
b4.grid(row=4, column=1, sticky='news', padx=10, pady=10)

l1 = ZBTlabel(master=main.top, font_spec='header', text='Data Analysis')
l1.grid(row=0, column=0, columnspan=3, sticky='news')

# zbt.addButton(0, 1, id='b1', text='POL', name='POL-Analysis')
# zbt.addButton(1, 1, id='b2', text='EIS', name='EIS-Analysis')
# zbt.addButton(2, 1, id='b3', text='MS', name='MS-Analysis')
# zbt.addButton(3, 1, id='b4', text='ECR', name='ECR-Analysis')

img_pol = Image.open('pol-curve.png')
img_eis = Image.open('eis-curve.png')
img_ms = Image.open('ms-spectra.png')
img_ecr = Image.open('ecr-curve.png')
img_zbt = Image.open('zbt_transparent.png')

ph_pol = ImageTk.PhotoImage(img_pol.resize((50, 50), Image.ANTIALIAS))
ph_eis = ImageTk.PhotoImage(img_eis.resize((50, 50), Image.ANTIALIAS))
ph_ms = ImageTk.PhotoImage(img_ms.resize((50, 50), Image.ANTIALIAS))
ph_ecr = ImageTk.PhotoImage(img_ecr.resize((50, 50), Image.ANTIALIAS))
ph_zbt = ImageTk.PhotoImage(img_zbt.resize((100, 50), Image.ANTIALIAS))

label_ph_pol = tk.Label(main.top, image=ph_pol, width=50, height=50, padx=10, pady=10)
label_ph_eis = tk.Label(main.top, image=ph_eis, width=50, height=50, padx=10, pady=10)
label_ph_ms = tk.Label(main.top, image=ph_ms, width=50, height=50, padx=10, pady=10)
label_ph_ecr = tk.Label(main.top, image=ph_ecr, width=50, height=50, padx=10, pady=10)
label_ph_zbt = tk.Label(main.top, image=ph_zbt, width=100, height=50, bg='grey20')

label_ph_pol.grid(row=1, column=0)
label_ph_eis.grid(row=2, column=0)
label_ph_ms.grid(row=3, column=0)
label_ph_ecr.grid(row=4, column=0)
label_ph_zbt.grid(row=0, column=2, sticky='ne')

main.mainloop()

