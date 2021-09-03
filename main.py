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
import warnings
from zbt_gui import ZBTframe, ZBTbutton, ZBTtoplevel, ZBTwindow, ZBTfont, ZBTentry, ZBTlabel
from datetime import datetime
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

warnings.simplefilter(action='ignore', category=FutureWarning)

from pymongo import MongoClient

# initialize mongo connector object with ip adress
client = MongoClient('172.16.134.6')

# get reference to existing database testDB
db = client.testDB

# reference collection, if not existent it will be created
current_collection = db['NMT_TestCollection']

# authentication within database
db.authenticate('mdb_LFD', 'zbtMongo!', source='testDB')


# GUI - mainwindow
main = ZBTwindow('Data Analysis', rows=10, columns=3)
# rootpath = Path('C:/Users/inrel/Desktop/database/')
rootpath = Path('data/database/')
plot_list = []
plot_df = []
plot_dict = {}

#POL
def buttonevent_pol(subwindow, plotter=None):
    analysis = ZBTtoplevel(master=main, canvas=True, name=subwindow, rows=10, columns=10)

    sub_b1 = ZBTbutton(master=analysis.sub_top, text='Import', command=lambda: get_pol_file(analysis))
    sub_b1.grid(row=0, column=0, sticky='news', padx=10, pady=10)

    sub_b2 = ZBTbutton(master=analysis.sub_top, text='Delete', command=lambda: delete_pol_file(analysis, var.get()))
    sub_b2.grid(row=1, column=0, sticky='news', padx=10, pady=10)

    sub_b3 = ZBTbutton(master=analysis.sub_top, text='Edit', command=lambda: edit_pol_file(analysis, var.get()))
    sub_b3.grid(row=2, column=0, sticky='news', padx=10, pady=10)

    sub_b4 = ZBTbutton(master=analysis.sub_top, text='Export', command=lambda: export_pol_graph(plot_list))
    sub_b4.grid(row=3, column=0, sticky='news', padx=10, pady=10)

    style = ttk.Style()
    style.theme_use('default')
    style.configure('Treeview', background='silver', foreground='#0063b4', rowheight=25, fieldbackground='silver')
    style.configure('Treeview.Heading', font=('Arial', 8, 'bold'), background='steelblue')
    style.map('Treeview', background=[('selected', 'blue')])

    columns = list(range(7))
    data_table = ttk.Treeview(master=analysis.sub_top, columns=columns, show='headings', height=5)
    data_table.tag_configure('odd', background='grey30')
    data_table.tag_configure('even', background='grey50')

    for i in columns:
        data_table.column(i, width=100, anchor='e')

    data_table.column(6, width=300, anchor='e')

    data_table.heading(column=0, text='Sample')
    data_table.heading(column=1, text='Date')
    data_table.heading(column=2, text='Area [cm²]')
    data_table.heading(column=3, text='c_flow [ml/min]')
    data_table.heading(column=4, text='a_flow [ml/min')
    data_table.heading(column=5, text='Temp. [°C]')
    data_table.heading(column=6, text='Add. Info')

    data_table.grid(row=1, column=2, rowspan=3, sticky='news', padx=10, pady=10)

    try:
        analysis.set_dbstatus('PyMongo Status: Connected')
        files = current_collection.find({'measurement': 'POL'}, {'_id': 0, 'name': 1})
    except NameError:
        analysis.set_dbstatus('PyMongo Status: Disconnected')
        df_lib = pd.read_csv('database/database_poldata/poldata.csv', delimiter='\t')
        measurement_name = df_lib['sample'].unique()
        files = [x for x in os.listdir('database/database_poldata/') if x.endswith(".csv")]


    var = tk.StringVar(analysis.sub_top)
    var.set(files[0])
    option = tk.OptionMenu(analysis.sub_top, var, *files, command=lambda _: plotter_pol(var.get(), plotter_canvas,
                                                                                        data_table))

    option.grid(row=0, column=2, columnspan=6, sticky='ew', padx=10, pady=10)

    #plotter
    plotter_fig = Figure()
    plotter_fig.set_facecolor('lightgrey')
    plotter_fig.set_edgecolor('black')
    grid = plotter_fig.add_gridspec(10, 10)

    # fig_ax1 = plotter_fig.add_subplot(grid[:10, :10])
    # fig_ax2 = fig_ax1.twinx()

    plotter_canvas = FigureCanvasTkAgg(plotter_fig, master=analysis.sub_canvas)
    plotter_canvas.get_tk_widget().configure(bg='red')
    plotter_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def plotter_pol(dropdown_var, canvas, data_table):

        plotter_fig.clear()

        grid = plotter_fig.add_gridspec(10, 10)

        fig_ax1 = plotter_fig.add_subplot(grid[:10, :10])
        fig_ax2 = fig_ax1.twinx()

        fig_ax1.set_title('POL-Curve', pad=10, fontdict=dict(fontsize=18, weight='bold'))
        fig_ax1.set_xlabel('current density [A/cm^2]')
        fig_ax1.set_ylabel('voltage [V]')
        fig_ax1.grid(b=True, which='both')

        fig_ax2.set_ylabel('power density [W/cm^2]')

        data_table.delete(*data_table.get_children())

        if dropdown_var in plot_list:
            plot_list.remove(dropdown_var)
            del plot_dict[dropdown_var]
        else:
            plot_list.append(dropdown_var)


        for i in plot_list:
            try:
                entry = current_collection.find_one({'name': i[10:-2], 'measurement': 'POL'}, {'_id': 0})
                pol_data = pd.DataFrame.from_dict(entry.get('pol_data'))
                table_data = [entry.get('name'), entry.get('date'), entry.get('area [cm^2]'), \
                              entry.get('flow_rate_cathode [ml/min]'), entry.get('flow_rate_anode [ml/min]'), \
                              entry.get('temperature [°C]'), entry.get('add_info')]
            except:
                pol_data = pd.read_csv('database/database_poldata/' + i, delimiter='\t')
                table_data = [pol_data.iloc[1]['sample'], pol_data.iloc[1]['date'], pol_data.iloc[1]['area [cm^2]'],
                              pol_data.iloc[1]['flow_rate_C [l/min]'], pol_data.iloc[1]['flow_rate_A [l/min]'],
                              pol_data.iloc[1]['Temperature [Cel.]']]

            x_values = np.asarray(pol_data['current density [A/cm^2]'])
            y_values = np.asarray(pol_data['voltage [V]'])
            y2_values = np.asarray(pol_data['power density [W/cm^2]'])

            # df_sample = pd.read_csv('database/database_poldata/' + dropdown_var, delimiter='\t')
            # x_values = np.asarray(df_sample['current density [A/cm^2]'])
            # y_values = np.asarray(df_sample['voltage [V]'])
            # y2_values = np.asarray(df_sample['power density [W/cm^2]'])

            plt1 = fig_ax1.plot(x_values, y_values, 's-', label=str(i[:-4]))
            fig_ax1.legend(loc='best')

            fig_ax2.plot(x_values, y2_values, '^--', color=plt1[0].get_color())

            pd.set_option('display.max_columns', None)

            plot_dict[i] = table_data

        samples, dates, areas, flow_c, flow_a, temp = ['sample'], ['date'], ['area'], ['flow_c'], ['flow_a'], ['temp']

        i = 1

        print(plot_dict)
        for key, value in plot_dict.items():
            i += 1

            sampledata = [value[0], value[1], value[2], value[3], value[4], value[5], value[6]]

            if i % 2 == 0:
                data_table.insert('', 'end', values=sampledata, tag=('even',))
            else:
                data_table.insert('', 'end', values=sampledata, tag=('odd',))

        canvas.draw()

    analysis.mainloop()

def get_pol_file(frame):
    filename = \
        tk.filedialog.askopenfilename(parent=frame, initialdir="exp_data/", title="Select file",
                                      filetypes=(("all files", "*.*"), ("Text files", "*.txt")))
    import_poldata(filename)

def import_poldata(file):
    pol_import = ZBTtoplevel('Import POL-Data', rows=12, columns=3, x_dim=500, y_dim=400)

    pol_import.set_file(file)

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

    b1_pol_imp = ZBTbutton(master=pol_import.sub_top, text='OK', command=lambda: data_check_pol(pol_import, file,
                                                                                                e1_pol_imp.get(),
                                                                                                e2_pol_imp.get(),
                                                                                                e3_pol_imp.get(),
                                                                                                e4_pol_imp.get(),
                                                                                                e5_pol_imp.get(),
                                                                                                e6_pol_imp.get(),
                                                                                                e7_pol_imp.get()))
    b1_pol_imp.grid(row=11, column=1, sticky='news')

    pol_import.mainloop()

def data_check_pol(frame, file, e1, e2, e3, e4, e5, e6, e7):

    entries = [e1, e2, e3, e4, e5, e6, e7]

    if '' in entries:
        messagebox.showinfo(parent=frame, title="Data Error", message="Incomplete Data!!!")
    else:
        save_poldata(file, frame, entries)

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
    db_data_dict = {'measurement': 'POL', "name": entries[0], 'date': entries[1], 'add_info': entries[6], 'area [cm^2]': entries[2],
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

    verify_pol_import(df_pol_data, entries)

    frame.destroy()

def verify_pol_import(df, entries):

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

def delete_pol_file(frame, dropdown_var):
    result = messagebox.askyesno(parent=frame, title="Data Warning", message="Delete " + str(dropdown_var) + '?')
    if result == True:
        current_collection.delete_one({'name': dropdown_var[10:-2], 'measurement': 'POL'})
        print('deleted ' + str(dropdown_var) + 'from database!')

def edit_pol_file(frame, dropdown_var):
    data = current_collection.find_one({'name': dropdown_var[10:-2], 'measurement': 'POL'}, {'_id': 0})

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

    b1_pol_edit = ZBTbutton(master=editor.sub_top, text='OK', command=lambda: data_edit_pol(editor, dropdown_var,
                                                                                            e1_pol_edit.get(),
                                                                                            e2_pol_edit.get(),
                                                                                            e3_pol_edit.get(),
                                                                                            e4_pol_edit.get(),
                                                                                            e5_pol_edit.get(),
                                                                                            e6_pol_edit.get(),
                                                                                            e7_pol_edit.get()))

    b1_pol_edit.grid(row=7, column=1, sticky='news')

def data_edit_pol(frame, dropdown_var, e1, e2, e3, e4, e5, e6, e7):

    entries = [e1, e2, e3, e4, e5, e6, e7]

    current_collection.update_one({'name': dropdown_var[10:-2]}, {'$set': {"name": entries[0], 'date': entries[1],
                                                                  'add_info': entries[6], 'area [cm^2]': entries[2],
                                                                  'flow_rate_cathode [ml/min]': entries[3],
                                                                  'flow_rate_anode [ml/min]': entries[4],
                                                                  'temperature [°C]': entries[5]}})



    frame.destroy()

def export_pol_graph(plot_list):
    fig, ax = plt.subplots()

    title = 'POL-Curve'
    ax.set_title(title)
    ax.set_xlabel('Current [A]')
    ax.set_ylabel('Voltage [V]')
    ax.grid(b=True, which='both')


    ax2 = ax.twinx()
    ax2.set_ylabel('Power [W]')


    for i in plot_list:
        try:
            entry = current_collection.find_one({'name': i[10:-2], 'measurement': 'POL'}, {'_id': 0})
            pol_data = pd.DataFrame.from_dict(entry.get('pol_data'))
            table_data = [entry.get('name'), entry.get('date'), entry.get('area [cm^2]'), \
                          entry.get('flowrate_cathode [ml/min]'), entry.get('flowrate_anode [ml/min]'), \
                          entry.get('temperature [°C]')]
        except:
            pol_data = pd.read_csv('database/database_poldata/' + i, delimiter='\t')
            table_data = [pol_data.iloc[1]['sample'], pol_data.iloc[1]['date'], pol_data.iloc[1]['area [cm^2]'],
                          pol_data.iloc[1]['flow_rate_C [l/min]'], pol_data.iloc[1]['flow_rate_A [l/min]'],
                          pol_data.iloc[1]['Temperature [Cel.]']]

        x_values = np.asarray(pol_data['current density [A/cm^2]'])
        y_values = np.asarray(pol_data['voltage [V]'])
        y2_values = np.asarray(pol_data['power density [W/cm^2]'])

        plt1 = ax.plot(x_values, y_values, 's--', label=str(i[:-4]))
        ax2.plot(x_values, y2_values, 's--', color=plt1[0].get_color())

    ax.legend(loc='best')
    plt.show()


#EIS
def buttonevent_eis(subwindow):
    analysis = ZBTtoplevel(master=main, canvas=True, x_dim=1500, name=subwindow, rows=10, columns=10)

    sub_b1 = ZBTbutton(master=analysis.sub_top, text='Import', command=lambda: get_eis_file(analysis))
    sub_b1.grid(row=0, column=0, sticky='news', padx=10, pady=10)

    sub_b2 = ZBTbutton(master=analysis.sub_top, text='Delete', command=lambda: delete_eis_file(analysis, var.get()))
    sub_b2.grid(row=1, column=0, sticky='news', padx=10, pady=10)

    sub_b3 = ZBTbutton(master=analysis.sub_top, text='Edit', command=lambda: edit_eis_file(analysis, var.get()))
    sub_b3.grid(row=2, column=0, sticky='news', padx=10, pady=10)

    sub_b4 = ZBTbutton(master=analysis.sub_top, text='Export', command=lambda: export_eis_graph(plot_list))
    sub_b4.grid(row=3, column=0, sticky='news', padx=10, pady=10)

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
        data_table.column(i, width=100, anchor='e')

    data_table.column(6, width=300, anchor='e')

    data_table.heading(column=0, text='Sample')
    data_table.heading(column=1, text='Date')
    data_table.heading(column=2, text='Area [cm²]')
    data_table.heading(column=3, text='c_flow [ml/min]')
    data_table.heading(column=4, text='a_flow [ml/min')
    data_table.heading(column=5, text='Temp. [°C]')
    data_table.heading(column=6, text='Add. Info')
    data_table.heading(column=7, text='Voltage')
    data_table.heading(column=8, text='Signal Ampl.')
    data_table.heading(column=9, text='Mode')

    data_table.grid(row=1, column=2, rowspan=3, sticky='news', padx=10, pady=10)

    try:
        analysis.set_dbstatus('PyMongo Status: Connected')
        eis_files = current_collection.find({'measurement': 'EIS'}, {'_id': 0, 'name': 1})
    except NameError:
        analysis.set_dbstatus('PyMongo Status: Disconnected')
        df_lib = pd.read_csv('database/database_eisdata/eisdata.csv', delimiter='\t')
        measurement_name = df_lib['sample'].unique()
        eis_files = [x for x in os.listdir('database/database_eisdata/') if x.endswith(".csv")]

    var = tk.StringVar(analysis.sub_top)
    var.set(eis_files[0])
    option = tk.OptionMenu(analysis.sub_top, var, *eis_files, command=lambda _: plotter_eis(var.get(), plotter_canvas,
                                                                                        data_table))

    option.grid(row=0, column=2, columnspan=6, sticky='ew', padx=10, pady=10)

    #plotter
    plotter_fig = Figure()
    plotter_fig.set_facecolor('lightgrey')
    plotter_fig.set_edgecolor('black')
    grid = plotter_fig.add_gridspec(10, 10)

    plotter_canvas = FigureCanvasTkAgg(plotter_fig, master=analysis.sub_canvas)
    plotter_canvas.get_tk_widget().configure(bg='red')
    plotter_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def plotter_eis(dropdown_var, canvas, data_table):

        plotter_fig.clear()

        grid = plotter_fig.add_gridspec(10, 10)

        fig_ax1 = plotter_fig.add_subplot(grid[:10, :10])

        fig_ax1.set_title('Nyquist-Plot', pad=10, fontdict=dict(fontsize=18, weight='bold'))
        fig_ax1.set_xlabel('Z (Re) [Ohm]')
        fig_ax1.set_ylabel('Z (Im) [Ohm]')
        fig_ax1.grid(b=True, which='both')

        data_table.delete(*data_table.get_children())

        if dropdown_var in plot_list:
            plot_list.remove(dropdown_var)
            del plot_dict[dropdown_var]
        else:
            plot_list.append(dropdown_var)

        for i in plot_list:
            try:
                #TODO: structure / reading of eis-data
                entry = current_collection.find_one({'measurement': 'EIS', 'name': i[10:-2]}, {'_id': 0})
                eis_data = pd.DataFrame.from_dict(entry.get('eis_data'))
                table_data = [entry.get('name'), entry.get('date'), entry.get('area [cm^2]'), \
                              entry.get('flow_rate_cathode [ml/min]'), entry.get('flow_rate_anode [ml/min]'), \
                              entry.get('temperature [°C]'), entry.get('add_info'), entry.get('signal amp.'),
                              entry.get('voltage'), entry.get('mode')]

            except:
                eis_data = pd.read_csv('database/database_eisdata/' + i, delimiter='\t')
                table_data = [eis_data.iloc[1]['sample'], eis_data.iloc[1]['date'], eis_data.iloc[1]['area [cm^2]'],
                              eis_data.iloc[1]['flow_rate_C [l/min]'], eis_data.iloc[1]['flow_rate_A [l/min]'],
                              eis_data.iloc[1]['Temperature [Cel.]']]

            x_values = np.asarray(eis_data['Re [Ohm*cm^2]'])
            y_values = np.asarray(eis_data['-Im [Ohm*cm^2]'])

            plt1 = fig_ax1.plot(x_values, y_values, 's-', label=str(i[:-4]))
            fig_ax1.legend(loc='best')


            plot_dict[i] = table_data

        #samples, dates, areas, flow_c, flow_a, temp = ['sample'], ['date'], ['area'], ['flow_c'], ['flow_a'], ['temp']

        i = 1

        for key, value in plot_dict.items():
            i += 1

            sampledata = [value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[8], value[7],
                          value[9]]

            if i % 2 == 0:
                data_table.insert('', 'end', values=sampledata, tag=('even',))
            else:
                data_table.insert('', 'end', values=sampledata, tag=('odd',))

        canvas.draw()

def get_eis_file(frame):
    filename = \
        tk.filedialog.askopenfilename(parent=frame, initialdir="exp_data/", title="Select file",
                                      filetypes=(("all files", "*.*"), ("Text files", "*.txt")))
    import_eisdata(filename)

def import_eisdata(file):
    df_specs_eis = pd.read_csv(file, decimal=',', encoding='cp1252', error_bad_lines=False, delim_whitespace=True,
                               index_col=False,
                               header=None, nrows=7, keep_default_na=False)

    eis_specs_date = df_specs_eis[3].values[0]
    eis_specs_time = df_specs_eis[1].values[5]
    eis_specs_datetime = datetime.strptime(eis_specs_date + ' ' + eis_specs_time, '%b,%d.%Y %H:%M:%S')
    eis_specs_voltage = df_specs_eis[1].values[2][0:-1]

    eis_import = ZBTtoplevel('Import EIS-Data', rows=14, columns=3, x_dim=500, y_dim=400)

    eis_import.set_file(file)

    l_head = ZBTlabel(master=eis_import.sub_top, font_spec='header', font_size=16, text='EIS Data-Import')
    l_head.grid(row=0, column=0, columnspan=3, sticky='news')

    l1_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='Sample:')
    l1_eis_imp.grid(row=3, column=0, sticky='nws')

    l2_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='Date:')
    l2_eis_imp.grid(row=4, column=0, sticky='nws')

    l9_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='Voltage:')
    l9_eis_imp.grid(row=5, column=0, sticky='nws')

    l3_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='Area:')
    l3_eis_imp.grid(row=6, column=0, sticky='nws')

    l4_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='FlowRate (C):')
    l4_eis_imp.grid(row=7, column=0, sticky='nws')  #

    l5_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='FlowRate (A):')
    l5_eis_imp.grid(row=8, column=0, sticky='nws')

    l6_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='Temperature:')
    l6_eis_imp.grid(row=9, column=0, sticky='nws')

    l8_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='Amp. Signal:')
    l8_eis_imp.grid(row=10, column=0, sticky='nws')

    l10_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='Mode:')
    l10_eis_imp.grid(row=11, column=0, sticky='nws')

    l7_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=12, text='Opt. Info:')
    l7_eis_imp.grid(row=12, column=0, sticky='nws')

    var = tk.StringVar()

    rb1_eis_imp = tk.Radiobutton(master=eis_import.sub_top, text="GEIS", variable=var, value='peis', bg='lightgrey')
    rb2_eis_imp = tk.Radiobutton(master=eis_import.sub_top, text="PEIS", variable=var, value='geis', bg='lightgrey')

    rb1_eis_imp.grid(row=11, padx=20, column=1, sticky='w')
    rb2_eis_imp.grid(row=11, padx=20, column=1, sticky='e')

    rb1_eis_imp.select()
    rb2_eis_imp.select()

    l02_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=10, text='[dd.mm.yyyy]')
    l02_eis_imp.grid(row=4, column=2, sticky='nws')

    l09_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=10, text='[V]')
    l09_eis_imp.grid(row=5, column=2, sticky='nws')

    l03_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=10, text='[cm²]')
    l03_eis_imp.grid(row=6, column=2, sticky='nws')

    l04_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=10, text='[ml/min]')
    l04_eis_imp.grid(row=7, column=2, sticky='nws')

    l05_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=10, text='[ml/min]')
    l05_eis_imp.grid(row=8, column=2, sticky='nws')

    l06_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=10, text='[°C]')
    l06_eis_imp.grid(row=9, column=2, sticky='nws')

    l08_eis_imp = ZBTlabel(master=eis_import.sub_top, font_size=10, text='[mA/mV]')
    l08_eis_imp.grid(row=10, column=2, sticky='nws')

    e1_eis_imp = ZBTentry(master=eis_import.sub_top)
    e1_eis_imp.grid(row=3, column=1, sticky='news')

    e2_eis_imp = ZBTentry(master=eis_import.sub_top)
    e2_eis_imp.grid(row=4, column=1, sticky='news')
    e2_eis_imp.insert(0, eis_specs_datetime)

    e9_eis_imp = ZBTentry(master=eis_import.sub_top)
    e9_eis_imp.grid(row=5, column=1, sticky='news')
    e9_eis_imp.insert(0, eis_specs_voltage)

    e3_eis_imp = ZBTentry(master=eis_import.sub_top)
    e3_eis_imp.grid(row=6, column=1, sticky='news')

    e4_eis_imp = ZBTentry(master=eis_import.sub_top)
    e4_eis_imp.grid(row=7, column=1, sticky='news')

    e5_eis_imp = ZBTentry(master=eis_import.sub_top)
    e5_eis_imp.grid(row=8, column=1, sticky='news')

    e6_eis_imp = ZBTentry(master=eis_import.sub_top)
    e6_eis_imp.grid(row=9, column=1, sticky='news')

    e7_eis_imp = ZBTentry(master=eis_import.sub_top)
    e7_eis_imp.grid(row=10, column=1, sticky='news')

    e10_eis_imp = ZBTentry(master=eis_import.sub_top)
    e10_eis_imp.grid(row=12, column=1, sticky='news')

    b1_eis_imp = ZBTbutton(master=eis_import.sub_top, text='OK', command=lambda: data_check_eis(eis_import, file,
                                                                                                e1_eis_imp.get(),
                                                                                                e2_eis_imp.get(),
                                                                                                e3_eis_imp.get(),
                                                                                                e4_eis_imp.get(),
                                                                                                e5_eis_imp.get(),
                                                                                                e6_eis_imp.get(),
                                                                                                e7_eis_imp.get(),
                                                                                                e9_eis_imp.get(),
                                                                                                e10_eis_imp.get(),
                                                                                                var.get()
                                                                                                ))

    b1_eis_imp.grid(row=14, column=1, sticky='news')

    eis_import.mainloop()

def data_check_eis(frame, file, e1, e2, e3, e4, e5, e6, e7, e9, e10, var):

    entries = [e1, e2, e3, e4, e5, e6, e7, e9, e10, var]

    if '' in entries:
        messagebox.showinfo(parent=frame, title="Data Error", message="Incomplete Data!!!")
    else:
        save_eisdata(file, frame, entries)

def save_eisdata(file, frame, entries):

    df_specs_eis = pd.read_csv(file, decimal=',', encoding='cp1252', error_bad_lines=False, delim_whitespace=True,
                               index_col=False,
                               header=None, nrows=7, keep_default_na=False)

    df_input = pd.read_csv(file, sep='\t', decimal='.', encoding='cp1252', error_bad_lines=False, skiprows=19,
                              index_col=False)

    # .txt data hast to be transfered into csv
    df_input.to_csv('temp_eis_data.txt', mode='w', header=True, index=False)

    df_input = pd.read_csv('temp_eis_data.txt', decimal='.', encoding='cp1252', error_bad_lines=False,
                                       delim_whitespace=True)

    df_input.columns = ['number', 'frequency [Hz]', 'impedance Re [Ohm]', 'impedance Im [Ohm]',
                                    'significance', 'time [s]']



    eis_data = {'sample': entries[0], 'date': entries[1], 'info': entries[6],
                'frequency [Hz]': df_input['frequency [Hz]'],
                'impedance Re [Ohm]': df_input['impedance Re [Ohm]'],
                'impedance Im [Ohm]': df_input['impedance Im [Ohm]'], 'amplitude sign.': entries[7],
                'area [cm^2]': int(entries[2]), 'flow_rate_C [l/min]': entries[3],
                'flow_rate_A [l/min]': entries[4], 'Temperature [Cel.]': entries[5]}



    df_eis_data = pd.DataFrame(eis_data)


    df_eis_data['Re [Ohm*cm^2]'] = df_input['impedance Re [Ohm]'] * int(entries[2])
    df_eis_data['-Im [Ohm*cm^2]'] = df_input['impedance Im [Ohm]'] * int(entries[2]) * -1

    pd.set_option('display.max_columns', None)
    df_eis_data_dict = df_eis_data[['frequency [Hz]', 'impedance Re [Ohm]', 'impedance Im [Ohm]', 'amplitude sign.',
                                    'Re [Ohm*cm^2]', '-Im [Ohm*cm^2]']]

    eis_data_dict = df_eis_data_dict.to_dict('records')
    db_data_dict = {'measurement': 'EIS', 'mode': entries[-1], "name": entries[0], 'date': entries[1],
                    'add_info': entries[8], 'area [cm^2]': entries[2],
                    'flow_rate_cathode [ml/min]': entries[3], 'flow_rate_anode [ml/min]': entries[4],
                    'temperature [°C]': entries[5], 'eis_data': eis_data_dict, 'voltage': entries[7],
                    'signal amp.': entries[6]}

    try:
        current_collection.insert_one(db_data_dict)
    except NameError:
        pass

    filename = str(entries[0]) + '.csv'
    df_eis_data.to_csv('database/database_eisdata/' + filename, mode='w', header=True, index=False, sep='\t')
    df_eis_data.to_csv('database/database_eisdata/eisdata.csv', mode='a', header=False, index=False, sep='\t')

    verify_eis_import(df_eis_data, entries)

    frame.destroy()

def verify_eis_import(df, entries):

    x_values = np.asarray(df['Re [Ohm*cm^2]'])
    y_values = np.asarray(df['-Im [Ohm*cm^2]'])

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, 'rs--')

    title = 'Nyquist Plot - ' + str(entries[0]) + ' (C: ' + str(entries[3]) +  ' / A: ' + \
            str(entries[4]) + '/ T: ' + str(entries[5]) + ')'
    ax.set_title(title)
    ax.set_xlabel('Re Z [Ohm*cm²]')
    ax.set_ylabel('Im Z [Ohm*cm²]')

    plt.show()

def delete_eis_file(frame, dropdown_var):
    result = messagebox.askyesno(parent=frame, title="Data Warning", message="Delete " + str(dropdown_var) + '?')
    if result == True:
        current_collection.delete_one({'name': dropdown_var[10:-2], 'measurement': 'EIS'})
        print('deleted ' + str(dropdown_var) + 'from database!')

def edit_eis_file(frame, dropdown_var):
    data = current_collection.find_one({'name': dropdown_var[10:-2], 'measurement': 'EIS'}, {'_id': 0})

    editor = ZBTtoplevel(master=frame, name='Edit File', rows=10, columns=3, x_dim=500, y_dim=400)

    l1_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Sample:')
    l1_eis_imp.grid(row=3, column=0, sticky='nws')

    l2_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Date:')
    l2_eis_imp.grid(row=4, column=0, sticky='nws')

    l9_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Voltage:')
    l9_eis_imp.grid(row=5, column=0, sticky='nws')

    l3_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Area')
    l3_eis_imp.grid(row=6, column=0, sticky='nws')

    l4_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='FlowRate (C)')
    l4_eis_imp.grid(row=7, column=0, sticky='nws')  #

    l5_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='FlowRate (A)')
    l5_eis_imp.grid(row=8, column=0, sticky='nws')

    l6_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Temperature')
    l6_eis_imp.grid(row=9, column=0, sticky='nws')

    l8_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Amp. Signal')
    l8_eis_imp.grid(row=10, column=0, sticky='nws')

    l7_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Opt. Info:')
    l7_eis_imp.grid(row=12, column=0, sticky='nws')

    var = tk.StringVar()

    rb1_eis_imp = tk.Radiobutton(master=editor, text="GEIS", variable=var, value='peis', bg='lightgrey')
    rb2_eis_imp = tk.Radiobutton(master=editor, text="PEIS", variable=var, value='geis', bg='lightgrey')

    rb1_eis_imp.grid(row=11, padx=20, column=1, sticky='w')
    rb2_eis_imp.grid(row=11, padx=20, column=1, sticky='e')

    rb1_eis_imp.select()
    rb2_eis_imp.select()

    l02_eis_imp = ZBTlabel(master=editor, font_size=16, text='dd.mm.yyyy')
    l02_eis_imp.grid(row=4, column=2, sticky='nes')

    l09_eis_imp = ZBTlabel(master=editor, font_size=16, text='V')
    l09_eis_imp.grid(row=5, column=2, sticky='nes')

    l03_eis_imp = ZBTlabel(master=editor, font_size=16, text='cm²')
    l03_eis_imp.grid(row=6, column=2, sticky='nes')

    l04_eis_imp = ZBTlabel(master=editor, font_size=16, text='l/min')
    l04_eis_imp.grid(row=7, column=2, sticky='nes')

    l05_eis_imp = ZBTlabel(master=editor, font_size=16, text='l/min')
    l05_eis_imp.grid(row=8, column=2, sticky='nes')

    l06_eis_imp = ZBTlabel(master=editor, font_size=16, text='°C')
    l06_eis_imp.grid(row=9, column=2, sticky='nes')

    l08_eis_imp = ZBTlabel(master=editor, font_size=16, text='mA/mV')
    l08_eis_imp.grid(row=10, column=2, sticky='nes')

    e1_eis_imp = ZBTentry(master=editor)
    e1_eis_imp.grid(row=3, column=1, sticky='news')
    e1_eis_imp.insert(0, data.get('name'))

    e2_eis_imp = ZBTentry(master=editor)
    e2_eis_imp.grid(row=4, column=1, sticky='news')
    e2_eis_imp.insert(0, data.get('date'))

    e9_eis_imp = ZBTentry(master=editor)
    e9_eis_imp.grid(row=5, column=1, sticky='news')
    e9_eis_imp.insert(0, data.get('voltage'))

    e3_eis_imp = ZBTentry(master=editor)
    e3_eis_imp.grid(row=6, column=1, sticky='news')
    e3_eis_imp.insert(0, data.get('area [cm^2]'))

    e4_eis_imp = ZBTentry(master=editor)
    e4_eis_imp.grid(row=7, column=1, sticky='news')
    e4_eis_imp.insert(0, data.get('flow_rate_cathode [ml/min]'))

    e5_eis_imp = ZBTentry(master=editor)
    e5_eis_imp.grid(row=8, column=1, sticky='news')
    e5_eis_imp.insert(0, data.get('flow_rate_anode [ml/min]'))

    e6_eis_imp = ZBTentry(master=editor)
    e6_eis_imp.grid(row=9, column=1, sticky='news')
    e6_eis_imp.insert(0, data.get('temperature [°C]'))

    e7_eis_imp = ZBTentry(master=editor)
    e7_eis_imp.grid(row=10, column=1, sticky='news')
    e7_eis_imp.insert(0, data.get('signal amp.'))

    e10_eis_imp = ZBTentry(master=editor)
    e10_eis_imp.grid(row=12, column=1, sticky='news')
    e10_eis_imp.insert(0, data.get('add_info'))

    b1_eis_imp = ZBTbutton(master=editor, text='OK', command=lambda: data_edit_eis(editor, dropdown_var,
                                                                               e1_eis_imp.get(),
                                                                               e2_eis_imp.get(),
                                                                               e3_eis_imp.get(),
                                                                               e4_eis_imp.get(),
                                                                               e5_eis_imp.get(),
                                                                               e6_eis_imp.get(),
                                                                               e7_eis_imp.get(),
                                                                               e9_eis_imp.get(),
                                                                               e10_eis_imp.get(),
                                                                               var.get()))

    b1_eis_imp.grid(row=14, column=1, sticky='news')

    editor.mainloop()

def data_edit_eis(frame, dropdown_var, e1, e2, e3, e4, e5, e6, e7, e9, e10, var):

    entries = [e1, e2, e3, e4, e5, e6, e7, e9, e10, var]

    current_collection.update_one({'name': dropdown_var[10:-2], 'measurement': 'EIS'}, {'$set': {"name": entries[0],
                                                                                                 'date': entries[1],
                                                                           'add_info': entries[8],
                                                                           'area [cm^2]': entries[2],
                                                                           'flow_rate_cathode [ml/min]': entries[3],
                                                                           'flow_rate_anode [ml/min]': entries[4],
                                                                           'temperature [°C]': entries[5],
                                                                           'voltage': entries[7],
                                                                           'mode': var}})

    frame.destroy()

def export_eis_graph(plot_list):
    fig, ax = plt.subplots()

    title = 'Nyquist-Plot'
    ax.set_title(title)
    ax.set_xlabel('Z (Re) [Ohm*cm^2]')
    ax.set_ylabel('Z (Im) [Ohm*cm^2]')
    ax.grid(b=True, which='both')

    for i in plot_list:
        try:
            # TODO: structure / reading of eis-data
            entry = current_collection.find_one({'measurement': 'EIS', 'name': i[10:-2]}, {'_id': 0})
            eis_data = pd.DataFrame.from_dict(entry.get('eis_data'))
            table_data = [entry.get('name'), entry.get('date'), entry.get('area [cm^2]'), \
                          entry.get('flowrate_cathode [ml/min]'), entry.get('flowrate_anode [ml/min]'), \
                          entry.get('temperature [°C]'), entry.get('current'), entry.get('signal ampl.'),
                          entry.get('voltage'), entry.get('mode')]

        except:
            eis_data = pd.read_csv('database/database_eisdata/' + i, delimiter='\t')
            table_data = [eis_data.iloc[1]['sample'], eis_data.iloc[1]['date'], eis_data.iloc[1]['area [cm^2]'],
                          eis_data.iloc[1]['flow_rate_C [l/min]'], eis_data.iloc[1]['flow_rate_A [l/min]'],
                          eis_data.iloc[1]['Temperature [Cel.]']]

        x_values = np.asarray(eis_data['Re [Ohm*cm^2]'])
        y_values = np.asarray(eis_data['-Im [Ohm*cm^2]'])

        ax.plot(x_values, y_values, 's-', label=str(i[:-4]))

    ax.legend(loc='best')
    plt.show()

    ax.legend(loc='best')


#ECR
def buttonevent_ecr(subwindow):
    analysis = ZBTtoplevel(master=main, canvas=True, x_dim=1500, name=subwindow, rows=10, columns=10)

    sub_b1 = ZBTbutton(master=analysis.sub_top, text='Import', command=lambda: get_ecr_file(analysis))
    sub_b1.grid(row=0, column=0, sticky='news', padx=10, pady=10)

    sub_b2 = ZBTbutton(master=analysis.sub_top, text='Delete', command=lambda: delete_ecr_file(analysis, var.get()))
    sub_b2.grid(row=1, column=0, sticky='news', padx=10, pady=10)

    sub_b3 = ZBTbutton(master=analysis.sub_top, text='Edit', command=lambda: edit_ecr_file(analysis, var.get()))
    sub_b3.grid(row=2, column=0, sticky='news', padx=10, pady=10)

    sub_b4 = ZBTbutton(master=analysis.sub_top, text='Export', command=lambda: export_ecr_graph(plot_list))
    sub_b4.grid(row=3, column=0, sticky='news', padx=10, pady=10)

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
        data_table.column(i, width=100, anchor='e')

    data_table.column(6, width=300, anchor='e')

    data_table.heading(column=0, text='Sample')
    data_table.heading(column=1, text='Date')
    data_table.heading(column=2, text='Mode')
    data_table.heading(column=3, text='GDL')
    data_table.heading(column=4, text='Area [cm²]')
    data_table.heading(column=5, text='cycles [#]')
    data_table.heading(column=6, text='Add. Info')

    data_table.grid(row=1, column=2, rowspan=3, sticky='news', padx=10, pady=10)

    try:
        analysis.set_dbstatus('PyMongo Status: Connected')
        ecr_files = current_collection.find({'measurement': 'ECR'}, {'_id': 0, 'name': 1})
    except NameError:
        analysis.set_dbstatus('PyMongo Status: Disconnected')
        df_lib = pd.read_csv('database/database_ecrdata/ecrdata.csv', delimiter='\t')
        measurement_name = df_lib['sample'].unique()
        ecr_files = [x for x in os.listdir('database/database_ecrdata/') if x.endswith(".csv")]

    var = tk.StringVar(analysis.sub_top)
    var.set(ecr_files[0])
    option = tk.OptionMenu(analysis.sub_top, var, *ecr_files, command=lambda _: plotter_ecr(var.get(), plotter_canvas,
                                                                                            data_table))

    option.grid(row=0, column=2, columnspan=6, sticky='ew', padx=10, pady=10)

    #plotter
    plotter_fig = Figure()
    plotter_fig.set_facecolor('lightgrey')
    plotter_fig.set_edgecolor('black')
    grid = plotter_fig.add_gridspec(10, 10)

    plotter_canvas = FigureCanvasTkAgg(plotter_fig, master=analysis.sub_canvas)
    plotter_canvas.get_tk_widget().configure(bg='red')
    plotter_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def plotter_ecr(dropdown_var, canvas, data_table):

        plotter_fig.clear()

        grid = plotter_fig.add_gridspec(10, 10)

        fig_ax1 = plotter_fig.add_subplot(grid[:10, :10])

        fig_ax1.set_title('Contact-Resistance', pad=10, fontdict=dict(fontsize=18, weight='bold'))
        fig_ax1.set_xlabel('resistance [mOhm*cm²]')
        fig_ax1.set_ylabel('pressure [bar]')
        fig_ax1.grid(b=True, which='both')

        data_table.delete(*data_table.get_children())

        if dropdown_var in plot_list:
            plot_list.remove(dropdown_var)
            del plot_dict[dropdown_var]
        else:
            plot_list.append(dropdown_var)

        for i in plot_list:
            try:
                entry = current_collection.find_one({'measurement': 'ECR', 'name': i[10:-2]}, {'_id': 0})
                ecr_data = pd.DataFrame.from_dict(entry.get('ecr_data'))
                table_data = [entry.get('name'), entry.get('date'), entry.get('area [cm^2]'), \
                              entry.get('flowrate_cathode [ml/min]'), entry.get('flowrate_anode [ml/min]'), \
                              entry.get('temperature [°C]'), entry.get('current'), entry.get('signal ampl.'),
                              entry.get('voltage'), entry.get('mode')]

            except:
                ecr_data = pd.read_csv('database/database_eisdata/' + i, delimiter='\t')
                table_data = [ecr_data.iloc[1]['sample'], ecr_data.iloc[1]['date'], ecr_data.iloc[1]['area [cm^2]'],
                              ecr_data.iloc[1]['flow_rate_C [l/min]'], ecr_data.iloc[1]['flow_rate_A [l/min]'],
                              ecr_data.iloc[1]['Temperature [Cel.]']]

            measurements = np.unique(ecr_data['measurement'].to_numpy())
            pressures = np.unique(ecr_data['pressure_rounded[bar]'].to_numpy(dtype=int))
            cycles = np.unique(ecr_data['cycle'].to_numpy(dtype=int))

            data_boxplot = []
            y_values = []
            for p in pressures:
                data_pressure = ecr_data['pressure_rounded[bar]'] == p
                data_boxplot.append(ecr_data[data_pressure]['as_contact_resistance[mOhm*cm2]'])
                y_values.append(ecr_data[data_pressure]['as_contact_resistance[mOhm*cm2]'].mean())

            fig_ax1.plot(pressures, y_values)
            fig_ax1.boxplot(data_boxplot, positions=pressures)
            fig_ax1.set_title('Contact-Resistance')
            fig_ax1.set_xlabel('pressure [bar]')
            fig_ax1.set_ylabel('resistance [mOhm*cm^2]')
            # a[1][2].set_xticks(range(0, max(x_values), 5))
            # a[1][2].set_yticks(range(0, int(max(data_boxplot[0])) + 5, 5))
            fig_ax1.grid()

            # fig_ax1.plot(x_values, y_values, 's-', label=str(i[:-4]))
            # fig_ax1.legend(loc='best')

            plot_dict[i] = table_data

        i = 1

        for key, value in plot_dict.items():
            data_table.heading(column=i, text=value[0])
            i += 1

            sampledata = [value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[8], value[7],
                          value[9]]

            if i % 2 == 0:
                data_table.insert('', 'end', values=sampledata, tag=('even',))
            else:
                data_table.insert('', 'end', values=sampledata, tag=('odd',))

        canvas.draw()

def get_ecr_file(frame):
    filename = \
        tk.filedialog.askopenfilename(parent=frame, initialdir="exp_data/", title="Select file",
                                      filetypes=(("all files", "*.*"), ("Text files", "*.txt")))
    import_ecrdata(filename)

def import_ecrdata(file):
    #get entrydata from file

    df_ecr = pd.read_csv(file, sep='\t', decimal=',', encoding='cp1252', error_bad_lines=False)

    pd.set_option('display.max_columns', None)
    print(df_ecr)

    ecr_specs_date = df_ecr.iloc[1]['Datum']
    ecr_specs_time = df_ecr.iloc[1]['Uhrzeit']
    ecr_specs_datetime = datetime.strptime(ecr_specs_date + ' ' + ecr_specs_time, '%d.%m.%Y %H:%M:%S')

    ecr_specs_area = df_ecr.iloc[1]['Anpressfläche / cm²']

    ecr_import = ZBTtoplevel('Import ECR-Data', rows=14, columns=3, x_dim=500, y_dim=400)

    ecr_import.set_file(file)

    # TODO:date? , thickness?, area?
    # header
    l_head = ZBTlabel(master=ecr_import.sub_top, font_spec='header', font_size=16, text='ECR Data-Import')
    l_head.grid(row=0, column=0, columnspan=3, sticky='news')

    #labels
    l1_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=12, text='Sample:')
    l1_ecr_imp.grid(row=3, column=0, sticky='nws')

    l2_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=12, text='Date:')
    l2_ecr_imp.grid(row=4, column=0, sticky='nws')

    l3_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=12, text='GDL:')
    l3_ecr_imp.grid(row=5, column=0, sticky='nws')

    l4_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=12, text='Meas. Pin:')
    l4_ecr_imp.grid(row=6, column=0, sticky='nws')  #

    l6_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=12, text='Thickness:')
    l6_ecr_imp.grid(row=8, column=0, sticky='nws')

    l7_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=12, text='Area:')
    l7_ecr_imp.grid(row=9, column=0, sticky='nws')

    l8_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=12, text='GDL Cycles BM.:')
    l8_ecr_imp.grid(row=10, column=0, sticky='nws')

    l9_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=12, text='Opt. Info:')
    l9_ecr_imp.grid(row=11, column=0, sticky='nws')

    # radiobuttons

    var_2 = tk.StringVar()

    rb3_ecr_imp = tk.Radiobutton(master=ecr_import.sub_top, text="F-H23", variable=var_2, value='f_h23', bg='lightgrey')
    rb4_ecr_imp = tk.Radiobutton(master=ecr_import.sub_top, text="SGL-29BC", variable=var_2, value='sgl_29bc', bg='lightgrey')

    rb3_ecr_imp.grid(row=5, padx=20, column=1, sticky='w')
    rb4_ecr_imp.grid(row=5, padx=20, column=1, sticky='e')

    rb3_ecr_imp.select()

    var = tk.StringVar()

    rb1_ecr_imp = tk.Radiobutton(master=ecr_import.sub_top, text="Yes", variable=var, value='yes', bg='lightgrey')
    rb2_ecr_imp = tk.Radiobutton(master=ecr_import.sub_top, text="No", variable=var, value='no', bg='lightgrey')

    rb1_ecr_imp.grid(row=6, padx=20, column=1, sticky='w')
    rb2_ecr_imp.grid(row=6, padx=20, column=1, sticky='e')

    rb1_ecr_imp.select()


    # units-labels
    l02_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=10, text='[dd.mm.yyyy]')
    l02_ecr_imp.grid(row=4, column=2, sticky='nws')

    l06_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=10, text='[cm]')
    l06_ecr_imp.grid(row=8, column=2, sticky='nws')

    l07_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=10, text='[cm^2]')
    l07_ecr_imp.grid(row=9, column=2, sticky='nws')

    l08_ecr_imp = ZBTlabel(master=ecr_import.sub_top, font_size=10, text='[#]')
    l08_ecr_imp.grid(row=10, column=2, sticky='nws')

    # TODO: auswahl Drücke und Mesströme in Datei

    # entries
    e1_ecr_imp = ZBTentry(master=ecr_import.sub_top)
    e1_ecr_imp.grid(row=3, column=1, sticky='news')

    e2_ecr_imp = ZBTentry(master=ecr_import.sub_top)
    e2_ecr_imp.grid(row=4, column=1, sticky='news')
    e2_ecr_imp.insert(0, ecr_specs_datetime)

    e5_ecr_imp = ZBTentry(master=ecr_import.sub_top)
    e5_ecr_imp.grid(row=8, column=1, sticky='news')

    e6_ecr_imp = ZBTentry(master=ecr_import.sub_top)
    e6_ecr_imp.grid(row=9, column=1, sticky='news')
    e6_ecr_imp.insert(0, ecr_specs_area)

    e7_ecr_imp = ZBTentry(master=ecr_import.sub_top)
    e7_ecr_imp.grid(row=10, column=1, sticky='news')

    e10_ecr_imp = ZBTentry(master=ecr_import.sub_top)
    e10_ecr_imp.grid(row=11, column=1, sticky='news')

    b1_ecr_imp = ZBTbutton(master=ecr_import.sub_top, text='OK', command=lambda: data_check_ecr(ecr_import, file,
                                                                                                 e1_ecr_imp.get(),
                                                                                                 e2_ecr_imp.get(),
                                                                                                 e5_ecr_imp.get(),
                                                                                                 e6_ecr_imp.get(),
                                                                                                 e7_ecr_imp.get(),
                                                                                                 e10_ecr_imp.get(),
                                                                                                 var.get(),
                                                                                                 var_2.get()
                                                                                                 ))

    b1_ecr_imp.grid(row=13, column=1, sticky='news')

    ecr_import.mainloop()

def data_check_ecr(frame, file, e1, e2, e5, e6, e7, e10, var, var_2):

    entries = {'sample': e1,'date': e2,'thickness': e5,'area': e6, 'gdl_age': e7, 'opt_info': e10,'mode': var,
               'gdl': var_2}

    if '' in entries.values():
        messagebox.showinfo(parent=frame, title="Data Error", message="Incomplete Data!!!")
    else:
        save_ecrdata(file, frame, entries)

def save_ecrdata(file, frame, entries):
    print(entries)
    df_ecr = pd.read_csv(file, sep='\t', decimal=',', encoding='cp1252', error_bad_lines=False)

    df_ecr = pd.read_csv(file, sep='\t', decimal=',', encoding='cp1252')

    df_ecr.round(6)

    df_ecr.rename(columns={df_ecr.iloc[0, 0]: 'date', 'Uhrzeit': 'time',
                           'Kommentar': 'measurement',
                           'p_Probe_Ist / bar': 'pressure_sample[bar]',
                           'I_Ist / mA': 'current[mA]',
                           'U_ges / mV': 'voltage[mV]',
                           'U_Nadel / mV': 'voltage_needle[mV]',
                           'U_ges-Th_U': 'voltage_th[mV]',
                           'U_Nadel-Th_U': 'voltage_needle_th[mV]',
                           'Anpressfläche / cm²': 'contact_area[cm2]',
                           'p_Ist / bar': 'pressure[bar]',
                           'p_Kraftsensor / ?': 'pressure_sensor'},
                  inplace=True)

    df_ecr = df_ecr[df_ecr['current[mA]'] != 0]

    df_ecr.fillna(0, inplace=True)

    df_ecr = df_ecr.iloc[:, :-1]

    sample_thickness = 'sample_thickness[cm]'
    df_ecr.insert(len(df_ecr.columns), sample_thickness, int(entries['thickness']))

    # Messzyklus
    cycle = 'cycle'
    df_ecr.insert(len(df_ecr.columns), cycle, 0.0)

    pressure_rounded = df_ecr['pressure_sample[bar]'].round(decimals=0)
    df_ecr.insert(4, column='pressure_rounded[bar]', value=pressure_rounded)

    current_rounded = df_ecr['current[mA]'].round(decimals=-2)
    df_ecr.insert(6, column='current_rounded[mA]', value=current_rounded)

    # spez. GDL-Korrektur
    corr = 'degradation_corr[mOhm]'
    df_ecr.insert(len(df_ecr.columns), corr, 0.0)

    as_corr = 'as_degradation_corr[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), as_corr, 0.0)

    # Gesamtwiderstand
    res_main_col = 'main_resistance[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_main_col, 0.0)

    res_main_mean_col = 'main_resistance_mean[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_main_mean_col, 0.0)

    res_main_error_col = 'main_resistance_error[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_main_error_col, 0.0)

    # as-Gesamtwiderstand
    res_main_as_col = 'as_main_resistance[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_main_as_col, 0.0)

    res_main_as_mean_col = 'as_main_resistance_mean[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_main_as_mean_col, 0.0)

    res_main_as_error_col = 'as_main_resistance_error[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_main_as_error_col, 0.0)

    # as-Durchgangswiderstand
    res_through_as_col = 'as_flow_resistance[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_through_as_col, 0.0)

    res_through_as_mean_col = 'as_flow_resistance_mean[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_through_as_mean_col, 0.0)

    res_through_as_error_col = 'as_flow_resistance_error[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_through_as_error_col, 0.0)

    # vs-Gesamtwiderstand
    res_main_vs_col = 'vs_main_resistance[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_main_vs_col, 0.0)

    res_main_vs_mean_col = 'vs_main_resistance_mean[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_main_vs_mean_col, 0.0)

    res_main_vs_error_col = 'vs_main_resistance_error[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_main_vs_error_col, 0.0)

    # Durchgangswiderstand
    res_through_col = 'flow_resistance[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_through_col, 0.0)

    res_through_mean_col = 'flow_resistance_mean[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_through_mean_col, 0.0)

    res_through_error_col = 'flow_resistance_error[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_through_error_col, 0.0)

    # vs-Durchgangswiderstand
    res_through_vs_col = 'vs_flow_resistance[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_through_vs_col, 0.0)

    res_through_vs_mean_col = 'vs_flow_resistance_mean[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_through_vs_mean_col, 0.0)

    res_through_vs_error_col = 'vs_flow_resistance_error[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_through_vs_error_col, 0.0)

    # Bulkwiderstand
    res_bulk_col = 'bulk_resistance[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_col, 0.0)

    res_bulk_mean_col = 'bulk_resistance_mean[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_mean_col, 0.0)

    res_bulk_error_col = 'bulk_resistance_error[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_error_col, 0.0)

    res_bulk_sub_col = 'bulk_resistance_sub[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_sub_col, 0.0)

    # as-Bulkwiderstand
    res_bulk_as_col = 'as_bulk_resistance[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_as_col, 0.0)

    res_bulk_as_mean_col = 'as_bulk_resistance_mean[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_as_mean_col, 0.0)

    res_bulk_as_error_col = 'as_bulk_resistance_error[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_as_error_col, 0.0)

    # vs-Bulkwiderstand
    res_bulk_vs_col = 'vs_bulk_resistance[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_vs_col, 0.0)

    res_bulk_vs_mean_col = 'vs_bulk_resistance_mean[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_vs_mean_col, 0.0)

    res_bulk_vs_error_col = 'vs_bulk_resistance_error[mOhm*cm]'
    df_ecr.insert(len(df_ecr.columns), res_bulk_vs_error_col, 0.0)

    # Kontaktwiderstand
    res_contact_col = 'contact_resistance[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_contact_col, 0.0)

    res_contact_mean_col = 'contact_resistance_mean[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_contact_mean_col, 0.0)

    res_contact_error_col = 'contact_resistance_error[mOhm]'
    df_ecr.insert(len(df_ecr.columns), res_contact_error_col, 0.0)

    # as-Kontaktwiderstand
    res_contact_as_col = 'as_contact_resistance[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_contact_as_col, 0.0)

    res_contact_as_mean_col = 'as_contact_resistance_mean[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_contact_as_mean_col, 0.0)

    res_contact_as_error_col = 'as_contact_resistance_error[mOhm*cm2]'
    df_ecr.insert(len(df_ecr.columns), res_contact_as_error_col, 0.0)

    # Gesamtleitwert
    con_main_vs_col = 'vs_main_conductance[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_main_vs_col, 0.0)

    con_main_vs_mean_col = 'vs_main_conductance_mean[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_main_vs_mean_col, 0.0)

    con_main_vs_error_col = 'vs_main_conductance_error[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_main_vs_error_col, 0.0)

    # Durchgangsleitwert
    con_through_vs_col = 'vs_flow_conductance[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_through_vs_col, 0.0)

    con_through_vs_mean_col = 'vs_flow_conductance_mean[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_through_vs_mean_col, 0.0)

    con_through_vs_error_col = 'vs_flow_conductance_error[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_through_vs_error_col, 0.0)

    # Bulkleitwert
    con_bulk_vs_col = 'vs_bulk_conductance[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_bulk_vs_col, 0.0)

    con_bulk_vs_mean_col = 'vs_bulk_conductance_mean[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_bulk_vs_mean_col, 0.0)

    con_bulk_vs_error_col = 'vs_bulk_conductance_error[S/cm]'
    df_ecr.insert(len(df_ecr.columns), con_bulk_vs_error_col, 0.0)

    no_cyc = int(entries['gdl_age'])

    for index, row in df_ecr.iterrows():

        current = row['current_rounded[mA]']
        pressure = row['pressure_rounded[bar]']

        if current < 600 and pressure < 3:
            no_cyc += 1

        df_ecr.loc[index, 'cycle'] = no_cyc

    measurements = np.unique(df_ecr['measurement'].to_numpy())
    pressures = np.unique(pressure_rounded.to_numpy(dtype=int))
    cycles = np.unique(df_ecr['cycle'].to_numpy(dtype=int))

    print(measurements)
    print(pressures)
    print(cycles)

    df_h23 = pd.read_csv('h23_reference.csv', sep='\t')

    pressure_ref = [1, 2, 3, 5, 6, 9, 10, 12, 15, 18, 20, 21, 24, 27, 30]

    for c in cycles:
        gdl_cycle = df_h23['cycle'] == c
        data_cycle = df_ecr['cycle'] == c

        for p in pressures:

            if p in pressure_ref:
                p_lookup = p
            else:
                p_lookup = min(pressure_ref, key=lambda x: abs(x - p))

            gdl_pressure = df_h23['pressure_rounded[bar]'] == p_lookup
            data_pressure = df_ecr['pressure_rounded[bar]'] == p_lookup

            gdl_corr = df_h23[gdl_cycle & gdl_pressure]['as_main_resistance[mOhm*cm2]'].mean() / \
                       df_h23[gdl_cycle & gdl_pressure]['contact_area[cm2]'].mean()
            gdl_as_corr = df_h23[gdl_cycle & gdl_pressure]['as_main_resistance[mOhm*cm2]'].mean()
            df_ecr.loc[data_cycle & data_pressure, corr] = gdl_corr
            df_ecr.loc[data_cycle & data_pressure, as_corr] = gdl_as_corr
    # seperate datafile into different measurements
    for m in measurements:

        data_measurement = df_ecr['measurement'] == m

        #     id = ref + ' ' + sample + ' ' + comment

        #     df_ecr.insert(2, 'measurement', id, True)

        for c in cycles:

            data_cycle = df_ecr['cycle'] == c

            for p in pressures:

                data_pressure = df_ecr['pressure_rounded[bar]'] == p

                df = df_ecr[data_cycle & data_pressure]

                res_main = df['voltage_th[mV]'] / df['current[mA]'] * 1000
                res_main_mean = res_main.mean()
                res_main_error = res_main.sem()
                res_main_as = res_main * df['contact_area[cm2]']
                res_main_as_mean = res_main_as.mean()
                res_main_as_error = res_main_as.sem()
                res_main_vs = res_main_as / df['sample_thickness[cm]']
                res_main_vs_mean = res_main_vs.mean()
                res_main_vs_error = res_main_vs.sem()
                con_main_vs = 1 / res_main_vs
                con_main_vs_mean = con_main_vs.mean()
                con_main_vs_error = con_main_vs.sem()
                df_ecr.loc[data_cycle & data_pressure, res_main_col] = res_main
                df_ecr.loc[data_cycle & data_pressure, res_main_mean_col] = res_main_mean
                df_ecr.loc[data_cycle & data_pressure, res_main_error_col] = res_main_error
                df_ecr.loc[data_cycle & data_pressure, res_main_as_col] = res_main_as
                df_ecr.loc[data_cycle & data_pressure, res_main_as_mean_col] = res_main_as_mean
                df_ecr.loc[data_cycle & data_pressure, res_main_as_error_col] = res_main_as_error
                df_ecr.loc[data_cycle & data_pressure, res_main_vs_col] = res_main_vs
                df_ecr.loc[data_cycle & data_pressure, res_main_vs_mean_col] = res_main_vs_mean
                df_ecr.loc[data_cycle & data_pressure, res_main_vs_error_col] = res_main_vs_error
                df_ecr.loc[data_cycle & data_pressure, con_main_vs_col] = con_main_vs
                df_ecr.loc[data_cycle & data_pressure, con_main_vs_mean_col] = con_main_vs_mean
                df_ecr.loc[data_cycle & data_pressure, con_main_vs_error_col] = con_main_vs_error

                res_through = res_main - df_ecr[corr]
                res_through_mean = res_through.mean()
                res_through_error = res_through.sem()
                res_through_as = res_through * df['contact_area[cm2]']
                res_through_as_mean = res_through_as.mean()
                res_through_as_error = res_through_as.sem()
                res_through_vs = res_through_as / df['sample_thickness[cm]']
                res_through_vs_mean = res_through_vs.mean()
                res_through_vs_error = res_through_vs.sem()
                con_through_vs = 1 / res_through_vs
                con_through_vs_mean = res_through_vs.mean()
                con_through_vs_error = res_through_vs.sem()
                df_ecr.loc[data_cycle & data_pressure, res_through_col] = res_through
                df_ecr.loc[data_cycle & data_pressure, res_through_mean_col] = res_through_mean
                df_ecr.loc[data_cycle & data_pressure, res_through_error_col] = res_through_error
                df_ecr.loc[data_cycle & data_pressure, res_through_as_col] = res_through_as
                df_ecr.loc[data_cycle & data_pressure, res_through_as_mean_col] = res_through_as_mean
                df_ecr.loc[data_cycle & data_pressure, res_through_as_error_col] = res_through_as_error
                df_ecr.loc[data_cycle & data_pressure, res_through_vs_col] = res_through_vs
                df_ecr.loc[data_cycle & data_pressure, res_through_vs_mean_col] = res_through_vs_mean
                df_ecr.loc[data_cycle & data_pressure, res_through_vs_error_col] = res_through_vs_error
                df_ecr.loc[data_cycle & data_pressure, con_through_vs_col] = con_through_vs
                df_ecr.loc[data_cycle & data_pressure, con_through_vs_mean_col] = res_through_vs_mean
                df_ecr.loc[data_cycle & data_pressure, con_through_vs_error_col] = res_through_vs_error

                if entries['mode'] == 'yes':
                    res_bulk = df['voltage_needle_th[mV]'] / df['current[mA]'] * 1000
                else:
                    res_bulk = 0

                print(entries['mode'])
                print(res_bulk)
                res_bulk_mean = res_bulk.mean()
                res_bulk_error = res_bulk.sem()
                res_bulk_as = res_bulk * df['contact_area[cm2]']
                res_bulk_as_mean = res_bulk_as.mean()
                res_bulk_as_error = res_bulk_as.sem()
                res_bulk_vs = res_bulk_as / df['sample_thickness[cm]']
                res_bulk_vs_mean = res_bulk_vs.mean()
                res_bulk_vs_error = res_bulk_vs.sem()
                con_bulk_vs = 1 / res_bulk_vs
                con_bulk_vs_mean = con_bulk_vs.mean()
                con_bulk_vs_error = con_bulk_vs.sem()
                df_ecr.loc[data_cycle & data_pressure, res_bulk_col] = res_bulk
                df_ecr.loc[data_cycle & data_pressure, res_bulk_mean_col] = res_bulk_mean
                df_ecr.loc[data_cycle & data_pressure, res_bulk_error_col] = res_bulk_error
                df_ecr.loc[data_cycle & data_pressure, res_bulk_as_col] = res_bulk_as
                df_ecr.loc[data_cycle & data_pressure, res_bulk_as_mean_col] = res_bulk_as_mean
                df_ecr.loc[data_cycle & data_pressure, res_bulk_as_error_col] = res_bulk_as_error
                df_ecr.loc[data_cycle & data_pressure, res_bulk_vs_col] = res_bulk_vs
                df_ecr.loc[data_cycle & data_pressure, res_bulk_vs_mean_col] = res_bulk_vs_mean
                df_ecr.loc[data_cycle & data_pressure, res_bulk_vs_error_col] = res_bulk_vs_error
                df_ecr.loc[data_cycle & data_pressure, con_bulk_vs_col] = con_bulk_vs
                df_ecr.loc[data_cycle & data_pressure, con_bulk_vs_mean_col] = con_bulk_vs_mean
                df_ecr.loc[data_cycle & data_pressure, con_bulk_vs_error_col] = con_bulk_vs_error

                res_contact = (res_through - res_bulk) / 2
                res_contact_mean = res_contact.mean()
                res_contact_error = res_contact.sem()
                res_contact_as = res_contact * df['contact_area[cm2]']
                res_contact_as_mean = res_contact.mean()
                res_contact_as_error = res_contact.sem()
                df_ecr.loc[data_cycle & data_pressure, res_contact_col] = res_contact
                df_ecr.loc[data_cycle & data_pressure, res_contact_mean_col] = res_contact_mean
                df_ecr.loc[data_cycle & data_pressure, res_contact_error_col] = res_contact_error
                df_ecr.loc[data_cycle & data_pressure, res_contact_as_col] = res_contact_as
                df_ecr.loc[data_cycle & data_pressure, res_contact_as_mean_col] = res_contact_as_mean
                df_ecr.loc[data_cycle & data_pressure, res_contact_as_error_col] = res_contact_as_error

    print(df_ecr[(df_ecr['cycle'] == 20) & (df_ecr['pressure_rounded[bar]'] == 20)])

    ecr_data_dict = df_ecr.to_dict('records')
    db_data_dict = {'measurement': 'ECR', "name": entries['sample'], 'mode': entries['mode'], 'gdl': entries['gdl'],
                    'date': entries['date'], 'add_info': entries['opt_info'], 'area [cm^2]': entries['area'],
                    'thickness': entries['thickness'], 'ecr_data': ecr_data_dict}

    try:
        current_collection.insert_one(db_data_dict)
    except NameError:
        pass

    filename = str(entries['sample']) + '.csv'
    df_ecr.to_csv('database/database_ecrdata/' + filename, mode='w', header=True, index=False, sep='\t')
    df_ecr.to_csv('database/database_ecrdata/ecrdata.csv', mode='a', header=False, index=False, sep='\t')

    verify_ecr_import(df_ecr, entries)

    frame.destroy()

def verify_ecr_import(df_ecr, entries):
    measurements = np.unique(df_ecr['measurement'].to_numpy())
    pressures = np.unique(df_ecr['pressure_rounded[bar]'].to_numpy(dtype=int))
    cycles = np.unique(df_ecr['cycle'].to_numpy(dtype=int))

    fig, a = plt.subplots(2, 3, figsize=(10, 10))

    # plot 1
    for c in cycles:
        data_cycle = df_ecr['cycle'] == c

        x_values = df_ecr[data_cycle]['pressure_rounded[bar]'].squeeze()
        y_values = df_ecr[data_cycle]['as_main_resistance_mean[mOhm*cm2]'].squeeze()
        error_values = df_ecr[data_cycle]['as_main_resistance_error[mOhm*cm2]'].squeeze()

        a[0][0].errorbar(x_values, y_values, yerr=error_values, elinewidth=None, capsize=2, label=str(c))

    a[0][0].set_title('Main-Resistance')
    a[0][0].set_xlabel('pressure [bar]')
    a[0][0].set_ylabel('resistance [mOhm*cm^2]')
    a[0][0].set_xticks(range(0, 31, 5))
    a[0][0].xaxis.set_minor_locator(AutoMinorLocator())
    a[0][0].set_yticks(ticks=range(0, int(y_values.max()) + 5, 10))
    a[0][0].yaxis.set_minor_locator(AutoMinorLocator())
    a[0][0].grid()
    a[0][0].legend(loc='best')

    # plot 2
    data_boxplot = []
    x_values = pressures
    y_values = []
    for p in pressures:
        data_pressure = df_ecr['pressure_rounded[bar]'] == p

        # data: mainresistance
        data_boxplot.append(df_ecr[data_pressure]['as_main_resistance[mOhm*cm2]'])
        y_values.append(df_ecr[data_pressure]['as_main_resistance_mean[mOhm*cm2]'].mean())

    a[0][1].boxplot(data_boxplot, positions=x_values)
    a[0][1].plot(x_values, y_values)

    a[0][1].set_title('Main-Resistance')
    a[0][1].set_xlabel('pressure [bar]')
    a[0][1].set_ylabel('resistance [mOhm*cm^2]')
    # a[0][1].xaxis.set_minor_locator(AutoMinorLocator())
    # ymax = int(max(y_values)) + 5
    # a[0][1].set_yticks(ticks=range(0, ymax, 10))
    # a[0][1].yaxis.set_minor_locator(AutoMinorLocator())
    a[0][1].grid()

    # plot 3
    data_boxplot = []
    x_values = pressures
    y_values = []
    for p in pressures:
        data_pressure = df_ecr['pressure_rounded[bar]'] == p

        data_boxplot.append(df_ecr[data_pressure]['as_bulk_resistance[mOhm*cm2]'])
        y_values.append(df_ecr[data_pressure]['as_bulk_resistance[mOhm*cm2]'].mean())

    a[1][0].plot(x_values, y_values)
    a[1][0].boxplot(data_boxplot, positions=x_values)
    a[1][0].set_title('Bulk-Resistance')
    a[1][0].set_xlabel('pressure [bar]')
    a[1][0].set_ylabel('resistance [mOhm*cm^2]')
    # a[1][1].set_xticks(range(0, max(x_values), 5))
    # a[1][0].set_yticks(range(0, max(y_values)*1.2))
    a[1][0].grid()

    # plot 4
    data_boxplot = []
    x_values = pressures
    y_values = []
    for p in pressures:
        data_pressure = df_ecr['pressure_rounded[bar]'] == p

        data_boxplot.append(df_ecr[data_pressure]['as_degradation_corr[mOhm*cm2]'])
        y_values.append(df_ecr[data_pressure]['as_degradation_corr[mOhm*cm2]'].mean())

    a[1][1].plot(x_values, y_values)
    a[1][1].boxplot(data_boxplot, positions=x_values)

    a[1][1].set_title('GDL-Correction')
    a[1][1].set_xlabel('pressure [bar]')
    a[1][1].set_ylabel('resistance [mOhm*cm^2]')

    #a[1][1].set_xticks(range(0, max(x_values), 5))
    #a[1][1].set_yticks(range(0, int(max(data_boxplot[0])) + 5))
    a[1][1].grid()

    # plot 5
    data_boxplot = []
    x_values = pressures
    y_values_main = []
    y_values_through = []
    y_values_bulk = []
    y_values_contact = []

    for p in pressures:
        data_pressure = df_ecr['pressure_rounded[bar]'] == p

        y_values_main.append(df_ecr[data_pressure]['as_main_resistance[mOhm*cm2]'].mean())
        y_values_through.append(df_ecr[data_pressure]['as_flow_resistance[mOhm*cm2]'].mean())
        y_values_bulk.append(df_ecr[data_pressure]['as_bulk_resistance[mOhm*cm2]'].mean())
        y_values_contact.append(df_ecr[data_pressure]['as_contact_resistance[mOhm*cm2]'].mean())

    a[0][2].plot(x_values, y_values_main, label='main_res')
    a[0][2].plot(x_values, y_values_through, label='through_res')
    a[0][2].plot(x_values, y_values_bulk, label='bulk_res')
    a[0][2].plot(x_values, y_values_contact, label='contact_res')

    a[0][2].set_title('Resistances')
    a[0][2].set_xlabel('pressure [bar]')
    a[0][2].set_ylabel('resistance [mOhm*cm^2]')
    a[0][2].set_xticks(range(0, max(x_values), 5))
    a[0][2].set_yticks(range(0, int(max(y_values_main)) + 5, 5))
    a[0][2].grid()
    a[0][2].legend(loc='best')

    # plot 6
    data_boxplot = []
    x_values = pressures
    y_values = []
    for p in pressures:
        data_pressure = df_ecr['pressure_rounded[bar]'] == p
        data_boxplot.append(df_ecr[data_pressure]['as_contact_resistance[mOhm*cm2]'])
        y_values.append(df_ecr[data_pressure]['as_contact_resistance[mOhm*cm2]'].mean())

    a[1][2].plot(x_values, y_values)
    a[1][2].boxplot(data_boxplot, positions=x_values)
    a[1][2].set_title('Contact-Resistance')
    a[1][2].set_xlabel('pressure [bar]')
    a[1][2].set_ylabel('resistance [mOhm*cm^2]')
    # a[1][2].set_xticks(range(0, max(x_values), 5))
    # a[1][2].set_yticks(range(0, int(max(data_boxplot[0])) + 5, 5))
    a[1][2].grid()

    plt.show()

def delete_ecr_file(frame, dropdown_var):
    result = messagebox.askyesno(parent=frame, title="Data Warning", message="Delete " + str(dropdown_var) + '?')
    if result == True:
        current_collection.delete_one({'name': dropdown_var[10:-2], 'measurement': 'ECR'})
        print('deleted ' + str(dropdown_var) + 'from database!')

def edit_ecr_file(frame, dropdown_var):
    data = current_collection.find_one({'name': dropdown_var[10:-2], 'measurement': 'EIS'}, {'_id': 0})

    editor = ZBTtoplevel(master=frame, name='Edit File', rows=10, columns=3, x_dim=500, y_dim=400)

    l1_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Sample:')
    l1_eis_imp.grid(row=3, column=0, sticky='nws')

    l2_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Date:')
    l2_eis_imp.grid(row=4, column=0, sticky='nws')

    l9_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Voltage:')
    l9_eis_imp.grid(row=5, column=0, sticky='nws')

    l3_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Area')
    l3_eis_imp.grid(row=6, column=0, sticky='nws')

    l4_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='FlowRate (C)')
    l4_eis_imp.grid(row=7, column=0, sticky='nws')  #

    l5_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='FlowRate (A)')
    l5_eis_imp.grid(row=8, column=0, sticky='nws')

    l6_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Temperature')
    l6_eis_imp.grid(row=9, column=0, sticky='nws')

    l8_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Amp. Signal')
    l8_eis_imp.grid(row=10, column=0, sticky='nws')

    l7_eis_imp = ZBTlabel(master=editor, font_spec='header', font_size=16, text='Opt. Info:')
    l7_eis_imp.grid(row=12, column=0, sticky='nws')

    var = tk.StringVar()

    rb1_eis_imp = tk.Radiobutton(master=editor, text="GEIS", variable=var, value='peis', bg='lightgrey')
    rb2_eis_imp = tk.Radiobutton(master=editor, text="PEIS", variable=var, value='geis', bg='lightgrey')

    rb1_eis_imp.grid(row=11, padx=20, column=1, sticky='w')
    rb2_eis_imp.grid(row=11, padx=20, column=1, sticky='e')

    rb1_eis_imp.select()
    rb2_eis_imp.select()

    l02_eis_imp = ZBTlabel(master=editor, font_size=16, text='dd.mm.yyyy')
    l02_eis_imp.grid(row=4, column=2, sticky='nes')

    l09_eis_imp = ZBTlabel(master=editor, font_size=16, text='V')
    l09_eis_imp.grid(row=5, column=2, sticky='nes')

    l03_eis_imp = ZBTlabel(master=editor, font_size=16, text='cm²')
    l03_eis_imp.grid(row=6, column=2, sticky='nes')

    l04_eis_imp = ZBTlabel(master=editor, font_size=16, text='l/min')
    l04_eis_imp.grid(row=7, column=2, sticky='nes')

    l05_eis_imp = ZBTlabel(master=editor, font_size=16, text='l/min')
    l05_eis_imp.grid(row=8, column=2, sticky='nes')

    l06_eis_imp = ZBTlabel(master=editor, font_size=16, text='°C')
    l06_eis_imp.grid(row=9, column=2, sticky='nes')

    l08_eis_imp = ZBTlabel(master=editor, font_size=16, text='mA/mV')
    l08_eis_imp.grid(row=10, column=2, sticky='nes')

    e1_eis_imp = ZBTentry(master=editor)
    e1_eis_imp.grid(row=3, column=1, sticky='news')
    e1_eis_imp.insert(0, data.get('name'))

    e2_eis_imp = ZBTentry(master=editor)
    e2_eis_imp.grid(row=4, column=1, sticky='news')
    e2_eis_imp.insert(0, data.get('date'))

    e9_eis_imp = ZBTentry(master=editor)
    e9_eis_imp.grid(row=5, column=1, sticky='news')
    e9_eis_imp.insert(0, data.get('voltage'))

    e3_eis_imp = ZBTentry(master=editor)
    e3_eis_imp.grid(row=6, column=1, sticky='news')
    e3_eis_imp.insert(0, data.get('area [cm^2]'))

    e4_eis_imp = ZBTentry(master=editor)
    e4_eis_imp.grid(row=7, column=1, sticky='news')
    e4_eis_imp.insert(0, data.get('flow_rate_cathode [ml/min]'))

    e5_eis_imp = ZBTentry(master=editor)
    e5_eis_imp.grid(row=8, column=1, sticky='news')
    e5_eis_imp.insert(0, data.get('flow_rate_anode [ml/min]'))

    e6_eis_imp = ZBTentry(master=editor)
    e6_eis_imp.grid(row=9, column=1, sticky='news')
    e6_eis_imp.insert(0, data.get('temperature [°C]'))

    e7_eis_imp = ZBTentry(master=editor)
    e7_eis_imp.grid(row=10, column=1, sticky='news')
    e7_eis_imp.insert(0, data.get('signal amp.'))

    e10_eis_imp = ZBTentry(master=editor)
    e10_eis_imp.grid(row=12, column=1, sticky='news')
    e10_eis_imp.insert(0, data.get('add_info'))

    b1_eis_imp = ZBTbutton(master=editor, text='OK', command=lambda: data_edit_eis(editor, dropdown_var,
                                                                               e1_eis_imp.get(),
                                                                               e2_eis_imp.get(),
                                                                               e3_eis_imp.get(),
                                                                               e4_eis_imp.get(),
                                                                               e5_eis_imp.get(),
                                                                               e6_eis_imp.get(),
                                                                               e7_eis_imp.get(),
                                                                               e9_eis_imp.get(),
                                                                               e10_eis_imp.get(),
                                                                               var.get()))

    b1_eis_imp.grid(row=14, column=1, sticky='news')

    editor.mainloop()

def data_edit_ecr(frame, dropdown_var, e1, e2, e3, e4, e5, e6, e7, e9, e10, var):

    entries = [e1, e2, e3, e4, e5, e6, e7, e9, e10, var]

    current_collection.update_one({'name': dropdown_var[10:-2], 'measurement': 'EIS'}, {'$set': {"name": entries[0],
                                                                                                 'date': entries[1],
                                                                           'add_info': entries[8],
                                                                           'area [cm^2]': entries[2],
                                                                           'flow_rate_cathode [ml/min]': entries[3],
                                                                           'flow_rate_anode [ml/min]': entries[4],
                                                                           'temperature [°C]': entries[5],
                                                                           'voltage': entries[7],
                                                                           'mode': var}})

    frame.destroy()

def export_ecr_graph(plot_list):
    fig, ax = plt.subplots()

    title = 'Nyquist-Plot'
    ax.set_title(title)
    ax.set_xlabel('Z (Re) [Ohm*cm^2]')
    ax.set_ylabel('Z (Im) [Ohm*cm^2]')
    ax.grid(b=True, which='both')

    for i in plot_list:
        try:
            # TODO: structure / reading of eis-data
            entry = current_collection.find_one({'measurement': 'EIS', 'name': i[10:-2]}, {'_id': 0})
            eis_data = pd.DataFrame.from_dict(entry.get('eis_data'))
            table_data = [entry.get('name'), entry.get('date'), entry.get('area [cm^2]'), \
                          entry.get('flowrate_cathode [ml/min]'), entry.get('flowrate_anode [ml/min]'), \
                          entry.get('temperature [°C]'), entry.get('current'), entry.get('signal ampl.'),
                          entry.get('voltage'), entry.get('mode')]

        except:
            eis_data = pd.read_csv('database/database_eisdata/' + i, delimiter='\t')
            table_data = [eis_data.iloc[1]['sample'], eis_data.iloc[1]['date'], eis_data.iloc[1]['area [cm^2]'],
                          eis_data.iloc[1]['flow_rate_C [l/min]'], eis_data.iloc[1]['flow_rate_A [l/min]'],
                          eis_data.iloc[1]['Temperature [Cel.]']]

        x_values = np.asarray(eis_data['Re [Ohm*cm^2]'])
        y_values = np.asarray(eis_data['-Im [Ohm*cm^2]'])

        ax.plot(x_values, y_values, 's-', label=str(i[:-4]))

    ax.legend(loc='best')
    plt.show()

    ax.legend(loc='best')


# GUI-Design mainwindow
b1 = ZBTbutton(master=main.top, text='POL', command=lambda: buttonevent_pol('POL-Analysis', plotter='pol'))
b2 = ZBTbutton(master=main.top, text='EIS', command=lambda: buttonevent_eis('EIS-Analysis'))
b3 = ZBTbutton(master=main.top, text='MS', command=lambda: buttonevent_ms('MS-Analysis'))
b4 = ZBTbutton(master=main.top, text='ECR', command=lambda: buttonevent_ecr('ECR-Analysis'))

b1.grid(row=1, column=1, sticky='news', padx=10, pady=10)
b2.grid(row=2, column=1, sticky='news', padx=10, pady=10)
b3.grid(row=3, column=1, sticky='news', padx=10, pady=10)
b4.grid(row=4, column=1, sticky='news', padx=10, pady=10)

l1 = ZBTlabel(master=main.top, font_spec='header', text='Data Analysis')
l1.grid(row=0, column=0, columnspan=3, sticky='news')

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

