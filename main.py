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
import os
from pymongo import MongoClient
from tkinter import ttk


matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

version, year = 0.1, 2021
author = 'JKP'

#pymongo
client = MongoClient('172.16.134.6')
db = client.testDB
db.authenticate('mdb_LFD', 'zbtMongo!', source='testDB')
current_collection = db['NMT_TestCollection']

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
            self.sub_left = ZBTframe(rows, 2, height=(y_dim-20)/4*3, width=x_dim/5*1, master=self)
            self.sub_left.grid_propagate(0)
            self.sub_canvas = ZBTframe(rows, 8, height=(y_dim-20)/4*3, width=x_dim/5*4, master=self, bg='blue')
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
# rootpath = Path('C:/Users/inrel/Desktop/database/')
rootpath = Path('data/database/')
plot_list = []
plot_df = []
plot_dict = {}


def buttonevent(subwindow, plotter=None):
    analysis = ZBTtoplevel(master=main, canvas=True, name=subwindow, rows=10, columns=10)

    sub_b1 = ZBTbutton(master=analysis.sub_top, text='Import', command=lambda: get_file(analysis))
    sub_b1.grid(row=0, column=0, sticky='news', padx=10, pady=10)

    sub_b2 = ZBTbutton(master=analysis.sub_top, text='Delete', command=lambda: delete_file(analysis, var.get()))
    sub_b2.grid(row=1, column=0, sticky='news', padx=10, pady=10)

    sub_b3 = ZBTbutton(master=analysis.sub_top, text='Edit', command=lambda: edit_file(analysis, var.get()))
    sub_b3.grid(row=2, column=0, sticky='news', padx=10, pady=10)

    style = ttk.Style()
    style.theme_use('default')
    style.configure('Treeview', background='silver', foreground='#0063b4', rowheight=25, fieldbackground='silver')
    style.configure('Treeview.Heading', font=('Arial', 8, 'bold'), background='steelblue')
    style.map('Treeview', background=[('selected', 'blue')])

    columns = list(range(10))
    data_table = ttk.Treeview(master=analysis.sub_top, columns=columns, show='headings', height=5)
    data_table.tag_configure('odd', background='grey30')
    data_table.tag_configure('even', background='grey50')
    for i in columns:
        data_table.column(i, width=60, anchor='e')

    data_table.grid(row=1, column=2, rowspan=3, sticky='news', padx=10, pady=10)

    # df_lib = pd.read_csv('database/database_poldata/poldata.csv', delimiter='\t')
    # measurement_name = df_lib['sample'].unique()

    #files = [x for x in os.listdir('database/database_poldata/') if x.endswith(".csv")]
    files = current_collection.find({}, {'_id': 0, 'name': 1})
    var = tk.StringVar(analysis.sub_top)
    var.set(files[0])
    option = tk.OptionMenu(analysis.sub_top, var, *files, command=lambda _: plotter_pol(var.get(), plotter_canvas,
                                                                                        fig_ax1, fig_ax2, data_table))

    option.grid(row=0, column=2, columnspan=6, sticky='ew', padx=10, pady=10)

    #plotter
    plotter_fig = Figure()
    plotter_fig.set_facecolor('lightgrey')
    plotter_fig.set_edgecolor('black')
    grid = plotter_fig.add_gridspec(10, 10)

    fig_ax1 = plotter_fig.add_subplot(grid[:10, :10])
    fig_ax1.set_title('POL-Curve', pad=10, fontdict=dict(fontsize=18, weight='bold'))
    fig_ax1.set_xlabel('current density [A/cm^2]')
    fig_ax1.set_ylabel('voltage [V]')

    fig_ax2 = fig_ax1.twinx()
    fig_ax2.set_ylabel('power density [W/cm^2]')

    plotter_canvas = FigureCanvasTkAgg(plotter_fig, master=analysis.sub_canvas)
    plotter_canvas.get_tk_widget().configure(bg='red')
    plotter_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def plotter_pol(dropdown_var, canvas, subf1, subf2, data_table):

        subf1.cla()
        subf2.cla()
        data_table.delete(*data_table.get_children())

        if dropdown_var in plot_list:
            plot_list.remove(dropdown_var)
            del plot_dict[dropdown_var]
        else:
            plot_list.append(dropdown_var)


        for i in plot_list:
            entry = current_collection.find_one({'name': i[10:-2]}, {'_id': 0})
            pol_data = pd.DataFrame.from_dict(entry.get('pol_data'))
            table_data = [entry.get('name'), entry.get('date'), entry.get('area [cm^2]'), \
                          entry.get('flowrate_cathode [ml/min]'), entry.get('flowrate_anode [ml/min]'), \
                          entry.get('temperature [°C]')]

            x_values = np.asarray(pol_data['current density [A/cm^2]'])
            y_values = np.asarray(pol_data['voltage [V]'])
            y2_values = np.asarray(pol_data['power density [W/cm^2]'])

            # df_sample = pd.read_csv('database/database_poldata/' + dropdown_var, delimiter='\t')
            # x_values = np.asarray(df_sample['current density [A/cm^2]'])
            # y_values = np.asarray(df_sample['voltage [V]'])
            # y2_values = np.asarray(df_sample['power density [W/cm^2]'])

            plot1 = subf1.plot(x_values, y_values, 's-', label=str(i[10:-2]))
            subf1.legend(loc='best')

            plot2 = subf2.plot(x_values, y2_values, '^--', color=plot1[0].get_color())

            pd.set_option('display.max_columns', None)

            plot_dict[i] = table_data

        samples, dates, areas, flow_c, flow_a, temp = ['sample'], ['date'], ['area'], ['flow_c'], ['flow_a'], ['temp']

        i = 1
        data_table.heading(column=0, text='sample')

        for key, value in plot_dict.items():
            print(key)
            data_table.heading(column=i, text=value[0])
            i += 1

            samples.append(value[0])
            dates.append(value[1])
            areas.append(value[2])
            flow_c.append(value[3])
            flow_a.append(value[4])
            temp.append(value[5])

        data_table.insert('', 'end', values=dates, tag=('odd',))
        data_table.insert('', 'end', values=areas, tag=('even',))
        data_table.insert('', 'end', values=flow_c, tag=('odd',))
        data_table.insert('', 'end', values=flow_a, tag=('even',))
        data_table.insert('', 'end', values=temp, tag=('odd',))
        data_table.insert('', 'end', values=('add. info', ''), tag=('even',))

        canvas.draw()

    analysis.mainloop()

def get_file(frame):
    filename = \
        tk.filedialog.askopenfilename(parent=frame, initialdir="exp_data/", title="Select file",
                                      filetypes=(("all files", "*.*"), ("Text files", "*.txt")))
    import_poldata(filename)

def delete_file(frame, dropdown_var):
    result = messagebox.askyesno(parent=frame, title="Data Warning", message="Delete " + str(dropdown_var) + '?')
    if result == True:
        current_collection.delete_one({'name': dropdown_var[10:-2]})
        print('deleted ' + str(dropdown_var) + 'from database!')

def edit_file(frame, dropdown_var):
    data = current_collection.find_one({'name': dropdown_var[10:-2]}, {'_id': 0})

    editor = ZBTtoplevel(master=frame, name='Edit File', rows=10, columns=3, x_dim=400, y_dim=500)

    l1_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='Sample:')
    l1_pol_edit.grid(row=0, column=0, sticky='nws')

    l2_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='Date:')
    l2_pol_edit.grid(row=1, column=0, sticky='nws')

    l3_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='Area')
    l3_pol_edit.grid(row=2, column=0, sticky='nws')

    l4_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='FlowRate (C)')
    l4_pol_edit.grid(row=3, column=0, sticky='nws')  #

    l5_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='FlowRate (A)')
    l5_pol_edit.grid(row=4, column=0, sticky='nws')

    l6_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='Temperature')
    l6_pol_edit.grid(row=5, column=0, sticky='nws')

    l7_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='Opt. Info:')
    l7_pol_edit.grid(row=6, column=0, sticky='nws')

    l02_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='dd.mm.yyyy')
    l02_pol_edit.grid(row=1, column=2, sticky='nes')

    l03_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='cm²')
    l03_pol_edit.grid(row=2, column=2, sticky='nes')

    l04_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='l/min')
    l04_pol_edit.grid(row=3, column=2, sticky='nes')

    l05_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='l/min')
    l05_pol_edit.grid(row=4, column=2, sticky='nes')

    l06_pol_edit = ZBTlabel(master=editor.sub_top, font_size=10, text='°C')
    l06_pol_edit.grid(row=5, column=2, sticky='nes')

    e1_pol_edit = ZBTentry(master=editor.sub_top)
    e1_pol_edit.grid(row=0, column=1, sticky='ew')
    e1_pol_edit.insert(0, data.get('name'))

    e2_pol_edit = ZBTentry(master=editor.sub_top)
    e2_pol_edit.grid(row=1, column=1, sticky='ew')
    e2_pol_edit.insert(0, data.get('date'))

    e3_pol_edit = ZBTentry(master=editor.sub_top)
    e3_pol_edit.grid(row=2, column=1, sticky='ew')
    e3_pol_edit.insert(0, data.get('area [cm^2]'))

    e4_pol_edit = ZBTentry(master=editor.sub_top)
    e4_pol_edit.grid(row=3, column=1, sticky='ew')
    e4_pol_edit.insert(0, data.get('flow_rate_cathode [ml/min]'))

    e5_pol_edit = ZBTentry(master=editor.sub_top)
    e5_pol_edit.grid(row=4, column=1, sticky='ew')
    e5_pol_edit.insert(0, data.get('flow_rate_anode [ml/min]'))

    e6_pol_edit = ZBTentry(master=editor.sub_top)
    e6_pol_edit.grid(row=5, column=1, sticky='ew')
    e6_pol_edit.insert(0, data.get('temperature [°C]'))

    e7_pol_edit = ZBTentry(master=editor.sub_top)
    e7_pol_edit.grid(row=6, column=1, rowspan=2, sticky='news')
    e7_pol_edit.insert(0, data.get('add_info'))

    b1_pol_edit = ZBTbutton(master=editor.sub_top, text='OK', command=lambda: data_edit(editor, dropdown_var,
                                                                                        e1_pol_edit.get(),
                                                                                        e2_pol_edit.get(),
                                                                                        e3_pol_edit.get(),
                                                                                        e4_pol_edit.get(),
                                                                                        e5_pol_edit.get(),
                                                                                        e6_pol_edit.get(),
                                                                                        e7_pol_edit.get()))

    b1_pol_edit.grid(row=7, column=1, sticky='news')

def data_edit(frame, dropdown_var, e1, e2, e3, e4, e5, e6, e7):

    entries = [e1, e2, e3, e4, e5, e6, e7]

    current_collection.update_one({'name': dropdown_var[10:-2]}, {'$set': {"name": entries[0], 'date': entries[1],
                                                                  'add_info': entries[6], 'area [cm^2]': entries[2],
                                                                  'flow_rate_cathode [ml/min]': entries[3],
                                                                  'flow_rate_anode [ml/min]': entries[4],
                                                                  'temperature [°C]': entries[5]}})



    frame.destroy()


def save_poldata(file, frame, entries):
    df_input = pd.read_csv(file, sep='\t', decimal='.', encoding='cp1252', error_bad_lines=False)
    pol_data = {'sample': entries[0], 'date': entries[1], 'info': entries[6], 'current [A]': df_input['I [A]'],
                'voltage [V]': df_input['U [V]'], 'area [cm^2]': int(entries[2]), 'flow_rate_C [l/min]': entries[3],
                'flow_rate_A [l/min]': entries[4], 'Temperature [Cel.]': entries[5]}
    df_pol_data = pd.DataFrame(pol_data)
    df_pol_data['current density [A/cm^2]'] = df_pol_data['current [A]'] / df_pol_data['area [cm^2]']
    df_pol_data['power [W]'] = df_pol_data['voltage [V]'] * df_pol_data['current [A]']
    df_pol_data['power density [W/cm^2]'] = df_pol_data['voltage [V]'] * df_pol_data['current density [A/cm^2]']
    pd.set_option('display.max_columns', None)

    df_pol_data_dict = df_pol_data[['current [A]', 'voltage [V]', 'power [W]', 'current density [A/cm^2]',
                                    'power density [W/cm^2]']]
    pol_data_dict = df_pol_data_dict.to_dict('records')
    db_data_dict = {"name": entries[0], 'date': entries[1], 'add_info': entries[6], 'area [cm^2]': entries[2],
                    'flow_rate_cathode [ml/min]': entries[3], 'flow_rate_anode [ml/min]': entries[4],
                    'temperature [°C]': entries[5], 'pol_data': pol_data_dict}

    current_collection.insert_one(db_data_dict)

    filename = str(entries[0]) + '.csv'
    df_pol_data.to_csv('database/database_poldata/' + filename, mode='w', header=True, index=False, sep='\t')

    # df_pol_data.to_csv('database/database_poldata/poldata.csv', mode='a', header=False, index=False, sep='\t')
    # # save eis data to excel
    # wb_path = str(rootpath) + '/QMS_data/qms_data_library.xlsx'
    # book = load_workbook(wb_path)
    # writer = pd.ExcelWriter(wb_path, engine='openpyxl')
    # writer.book = book
    # df_qms.to_excel(writer, sheet_name=filename, index=False)
    # writer.save()
    # writer.close()

    verify_import(df_pol_data, entries)

    frame.destroy()

def verify_import(df, entries):

    x_values = np.asarray(df['current density [A/cm^2]'])
    y_values = np.asarray(df['voltage [V]'])
    y2_values = np.asarray(df['power density [W/cm^2]'])

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

