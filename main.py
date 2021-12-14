import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
from time import strftime
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
#from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.font as tkFont
import TKlighter
import sqlite3
import json
import pandas as pd
from ttkthemes import ThemedTk
import re
import os.path


#db_path="/home/joy/01myfolder/sqlite_DB/Master_DB.db"
#db_path="C:/Users/313156/python_proj/xml_parsing/xml.db"
db_path="./Sahayak.db"
if os.path.isfile(db_path):
    pass
else:
    with open(db_path, 'x') as f:
        pass

# creating tkinter window
root = ThemedTk(theme="adapta")
#root = Tk()
root.title('Sahayak')
# Set window size and transparency
#root.attributes('-alpha', 0.8)
root.geometry("1080x800")
fname=''
filepath=''
df=pd.DataFrame()
myFont = tkFont.Font(family="Arial",size=10)#"Times New Roman", size=12)

def refresh():
    for i in tree.get_children():
        tree.delete(i)
    tab=get_table_name()
    for i in enumerate(tab):
        tree.insert(parent='', index=i[0], iid=i[0],text='', values=(i[1]))
        col = get_col(i[1])
        for j in enumerate(col):
            tree.insert(parent=i[0], index=j[0], text='', values=(j[1]))


def get_table_name():
    con1 = sqlite3.connect(db_path)
    cur1 = con1.cursor()
    cur1.execute("""select name 
	 from sqlite_master
	 where type = 'table'""")
    rows = cur1.fetchall() 
    con1.close()
    return(rows)


def get_col(table_name):
    con1 = sqlite3.connect(db_path)
    cur1 = con1.cursor()
    cur1.execute("""select name 
        from pragma_table_info(('"""+table_name[0]+"""'))
        """)
    rows = cur1.fetchall() 
    con1.close()
    return(rows)


def xlfile2db():
    # get the file name and table name, 
    # connect to the DB and create the table, 
    # insert the date from the file to the created table
    global fname
    meta=''
    con1 = sqlite3.connect(db_path)
    cur1 = con1.cursor()

    # get the names of the sheets in the excel file loaded
    try:
        xl = pd.ExcelFile(fname)
        sn=xl.sheet_names
    except:
        sn =["default"]
    for i in sn:  #xl.sheet_names:
        table_name1 = simpledialog.askstring(title="Table Name",
                                  prompt="Enter table Name for : " +i)
        if table_name1 is not None:
            # get the data from the file into the pandas data frame
            try:
                data = pd.read_excel(
                    fname, 
                    sheet_name=i,
                    header=0)
            except:
                data = pd.read_csv(
                    fname, 
                    encoding='latin-1',
                    skip_blank_lines=True,
                    skipinitialspace=True,
                    header=0)


            #prepare the metadata for the table to be created from the header of the excel
            for c in data.columns:
                c=re.sub('[^a-zA-Z0-9 \n\." "]', '_', c)
                c=c.replace(' ','').rstrip("_")
                meta = meta + c+" varchar(255)"+ ', '
            meta_col = list(meta.split(", "))
            meta_col.pop()
            col2=[]
            for s in meta_col:
                col2.append(s.split(" ")[0])
            meta = '('+meta+')'
            meta=meta.replace(', )',')')
            try:
                cur1.execute("CREATE TABLE "+table_name1+meta)
                # insert the data into the created table
                data.columns = col2
                try:
                    data.to_sql(table_name1, con1, if_exists='append',index=False)
                except Exception as e:
                    messagebox.showinfo('error',e)
                messagebox.showinfo('File load','Table created')
            except Exception as e:
                messagebox.showinfo('Error',e)
            meta = ''

    refresh()
    con1.close()

def t_drop():
    curItem = tree.focus()
    sel=tree.item(curItem)
    if sel['values'] == '':
        pass
    else:
        con1 = sqlite3.connect(db_path)
        cur1 = con1.cursor()
        cur1.execute("drop table "+str(sel['values'][0]))
        con1.close()
        messagebox.showinfo('Confirmation',"Table drop Successfull")
        refresh()


def open_file():
    """Open a file for editing."""
    global filepath 
    filepath = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    queryframe.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        queryframe.insert(tk.END, text)
    root.title(f"Sahayak - {filepath}")



def save_as_file():
    """Save the current file as a new file."""
    global filepath 
    filepath = filedialog.asksaveasfilename(
        defaultextension="txt",
        filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx"), ("Excel2 Files", "*.xls"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = queryframe.get(1.0, tk.END)
        output_file.write(text)
    root.title(f"Sahayak - {filepath}")


def save_file():
    """Save the current file."""
    global filepath
    if not filepath:
        save_as_file()
    with open(filepath, "w") as output_file:
        text = queryframe.get(1.0, tk.END)
        output_file.write(text)
    root.title(f"Sahayak - {filepath}")

def new_file():
    """Save the current file as a new file."""
    global filepath
    if not filepath:
        queryframe.delete(1.0, tk.END)
    else:
        save_file()
        queryframe.delete(1.0, tk.END)
    filepath=''
    root.title("Sahayak")



def browseFiles():
    # select the file to load data to the table
    global fname
    fname = filedialog.askopenfilename(initialdir = "/",
										title = "Select a File",
										filetypes = (("csv files","*.csv*"),("Excel files","*.xlsx"),("Excel2 files","*.xls"), ("all files","*.*")))
    messagebox.showinfo('File selected',fname)
    if not fname:
        pass
    else:
        #table_name = simpledialog.askstring(title="Table Name", prompt="Enter table Name:")
        xlfile2db()

def export_df():
    global df
    filepath = filedialog.asksaveasfilename(
        defaultextension="txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    #df.to_excel(r'./Export.xlsx', sheet_name='df',index=False, header=True)
    if filepath != '':
        df.to_excel(filepath, sheet_name='df',index=False, header=True)


def get_ele(event=None):
    curItem = tree.focus()
    sel=tree.item(curItem)
    if sel is not None:
        queryframe.insert(INSERT, sel['values'])

def hl(event):
    TKlighter.custom_h(queryframe,'select', 'green')
    TKlighter.custom_h(queryframe,'ADD', 'green')
    TKlighter.custom_h(queryframe,'ADD CONSTRAINT', 'green')
    TKlighter.custom_h(queryframe,'ALTER', 'green')
    TKlighter.custom_h(queryframe,'ALTER COLUMN', 'green')
    TKlighter.custom_h(queryframe,'ALTER TABLE', 'green')
    TKlighter.custom_h(queryframe,'ALL', 'green')
    TKlighter.custom_h(queryframe,'AND', 'green')
    TKlighter.custom_h(queryframe,'ANY', 'green')
    TKlighter.custom_h(queryframe,'AS', 'green')
    TKlighter.custom_h(queryframe,'ASC', 'green')
    TKlighter.custom_h(queryframe,'BACKUP DATABASE', 'green')
    TKlighter.custom_h(queryframe,'BETWEEN', 'green')
    TKlighter.custom_h(queryframe,'CASE', 'green')
    TKlighter.custom_h(queryframe,'CHECK', 'green')
    TKlighter.custom_h(queryframe,'COLUMN', 'green')
    TKlighter.custom_h(queryframe,'CONSTRAINT', 'green')
    TKlighter.custom_h(queryframe,'CREATE', 'green')
    TKlighter.custom_h(queryframe,'CREATE DATABASE', 'green')
    TKlighter.custom_h(queryframe,'CREATE INDEX', 'green')
    TKlighter.custom_h(queryframe,'CREATE OR REPLACE VIEW', 'green')
    TKlighter.custom_h(queryframe,'CREATE TABLE', 'green')
    TKlighter.custom_h(queryframe,'CREATE PROCEDURE', 'green')
    TKlighter.custom_h(queryframe,'CREATE UNIQUE INDEX', 'green')
    TKlighter.custom_h(queryframe,'CREATE VIEW', 'green')
    TKlighter.custom_h(queryframe,'DATABASE', 'green')
    TKlighter.custom_h(queryframe,'DEFAULT', 'green')
    TKlighter.custom_h(queryframe,'DELETE', 'green')
    TKlighter.custom_h(queryframe,'DESC', 'green')
    TKlighter.custom_h(queryframe,'DISTINCT', 'green')
    TKlighter.custom_h(queryframe,'DROP', 'green')
    TKlighter.custom_h(queryframe,'DROP COLUMN', 'green')
    TKlighter.custom_h(queryframe,'DROP CONSTRAINT', 'green')
    TKlighter.custom_h(queryframe,'DROP DATABASE', 'green')
    TKlighter.custom_h(queryframe,'DROP DEFAULT', 'green')
    TKlighter.custom_h(queryframe,'DROP INDEX', 'green')
    TKlighter.custom_h(queryframe,'DROP TABLE', 'green')
    TKlighter.custom_h(queryframe,'DROP VIEW', 'green')
    TKlighter.custom_h(queryframe,'EXEC', 'green')
    TKlighter.custom_h(queryframe,'EXISTS', 'green')
    TKlighter.custom_h(queryframe,'FOREIGN KEY', 'green')
    TKlighter.custom_h(queryframe,'FROM', 'green')
    TKlighter.custom_h(queryframe,'FULL OUTER JOIN', 'green')
    TKlighter.custom_h(queryframe,'GROUP BY', 'green')
    TKlighter.custom_h(queryframe,'HAVING', 'green')
    TKlighter.custom_h(queryframe,'IN', 'green')
    TKlighter.custom_h(queryframe,'INDEX', 'green')
    TKlighter.custom_h(queryframe,'INNER JOIN', 'green')
    TKlighter.custom_h(queryframe,'INSERT INTO', 'green')
    TKlighter.custom_h(queryframe,'INSERT INTO SELECT', 'green')
    TKlighter.custom_h(queryframe,'IS NULL', 'green')
    TKlighter.custom_h(queryframe,'IS NOT NULL', 'green')
    TKlighter.custom_h(queryframe,'JOIN', 'green')
    TKlighter.custom_h(queryframe,'LEFT JOIN', 'green')
    TKlighter.custom_h(queryframe,'LIKE', 'green')
    TKlighter.custom_h(queryframe,'LIMIT', 'green')
    TKlighter.custom_h(queryframe,'NOT', 'green')
    TKlighter.custom_h(queryframe,'NOT NULL', 'green')
    TKlighter.custom_h(queryframe,'OR', 'green')
    TKlighter.custom_h(queryframe,'ORDER BY', 'green')
    TKlighter.custom_h(queryframe,'OUTER JOIN', 'green')
    TKlighter.custom_h(queryframe,'PRIMARY KEY', 'green')
    TKlighter.custom_h(queryframe,'PROCEDURE', 'green')
    TKlighter.custom_h(queryframe,'RIGHT JOIN', 'green')
    TKlighter.custom_h(queryframe,'ROWNUM', 'green')
    TKlighter.custom_h(queryframe,'SELECT', 'green')
    TKlighter.custom_h(queryframe,'SELECT DISTINCT', 'green')
    TKlighter.custom_h(queryframe,'SELECT INTO', 'green')
    TKlighter.custom_h(queryframe,'SELECT TOP', 'green')
    TKlighter.custom_h(queryframe,'SET', 'green')
    TKlighter.custom_h(queryframe,'TABLE', 'green')
    TKlighter.custom_h(queryframe,'TOP', 'green')
    TKlighter.custom_h(queryframe,'TRUNCATE TABLE', 'green')
    TKlighter.custom_h(queryframe,'UNION', 'green')
    TKlighter.custom_h(queryframe,'UNION ALL', 'green')
    TKlighter.custom_h(queryframe,'UNIQUE', 'green')
    TKlighter.custom_h(queryframe,'UPDATE', 'green')
    TKlighter.custom_h(queryframe,'VALUES', 'green')
    TKlighter.custom_h(queryframe,'VIEW', 'green')
    TKlighter.custom_h(queryframe,'WHERE', 'green')
    TKlighter.custom_h(queryframe,'add', 'green')
    TKlighter.custom_h(queryframe,'add constraint', 'green')
    TKlighter.custom_h(queryframe,'alter', 'green')
    TKlighter.custom_h(queryframe,'alter column', 'green')
    TKlighter.custom_h(queryframe,'alter table', 'green')
    TKlighter.custom_h(queryframe,'all', 'green')
    TKlighter.custom_h(queryframe,'and', 'green')
    TKlighter.custom_h(queryframe,'any', 'green')
    TKlighter.custom_h(queryframe,'as', 'green')
    TKlighter.custom_h(queryframe,'asc', 'green')
    TKlighter.custom_h(queryframe,'backup database', 'green')
    TKlighter.custom_h(queryframe,'between', 'green')
    TKlighter.custom_h(queryframe,'case', 'green')
    TKlighter.custom_h(queryframe,'check', 'green')
    TKlighter.custom_h(queryframe,'column', 'green')
    TKlighter.custom_h(queryframe,'constraint', 'green')
    TKlighter.custom_h(queryframe,'create', 'green')
    TKlighter.custom_h(queryframe,'create database', 'green')
    TKlighter.custom_h(queryframe,'create index', 'green')
    TKlighter.custom_h(queryframe,'create or replace view', 'green')
    TKlighter.custom_h(queryframe,'create table', 'green')
    TKlighter.custom_h(queryframe,'create procedure', 'green')
    TKlighter.custom_h(queryframe,'create unique index', 'green')
    TKlighter.custom_h(queryframe,'create view', 'green')
    TKlighter.custom_h(queryframe,'database', 'green')
    TKlighter.custom_h(queryframe,'default', 'green')
    TKlighter.custom_h(queryframe,'delete', 'green')
    TKlighter.custom_h(queryframe,'desc', 'green')
    TKlighter.custom_h(queryframe,'distinct', 'green')
    TKlighter.custom_h(queryframe,'drop', 'green')
    TKlighter.custom_h(queryframe,'drop column', 'green')
    TKlighter.custom_h(queryframe,'drop constraint', 'green')
    TKlighter.custom_h(queryframe,'drop database', 'green')
    TKlighter.custom_h(queryframe,'drop default', 'green')
    TKlighter.custom_h(queryframe,'drop index', 'green')
    TKlighter.custom_h(queryframe,'drop table', 'green')
    TKlighter.custom_h(queryframe,'drop view', 'green')
    TKlighter.custom_h(queryframe,'exec', 'green')
    TKlighter.custom_h(queryframe,'exists', 'green')
    TKlighter.custom_h(queryframe,'foreign key', 'green')
    TKlighter.custom_h(queryframe,'from', 'green')
    TKlighter.custom_h(queryframe,'full outer join', 'green')
    TKlighter.custom_h(queryframe,'group by', 'green')
    TKlighter.custom_h(queryframe,'having', 'green')
    TKlighter.custom_h(queryframe,'in', 'green')
    TKlighter.custom_h(queryframe,'index', 'green')
    TKlighter.custom_h(queryframe,'inner join', 'green')
    TKlighter.custom_h(queryframe,'insert into', 'green')
    TKlighter.custom_h(queryframe,'insert into select', 'green')
    TKlighter.custom_h(queryframe,'is null', 'green')
    TKlighter.custom_h(queryframe,'is not null', 'green')
    TKlighter.custom_h(queryframe,'join', 'green')
    TKlighter.custom_h(queryframe,'left join', 'green')
    TKlighter.custom_h(queryframe,'like', 'green')
    TKlighter.custom_h(queryframe,'limit', 'green')
    TKlighter.custom_h(queryframe,'not', 'green')
    TKlighter.custom_h(queryframe,'not null', 'green')
    TKlighter.custom_h(queryframe,'or', 'green')
    TKlighter.custom_h(queryframe,'order by', 'green')
    TKlighter.custom_h(queryframe,'outer join', 'green')
    TKlighter.custom_h(queryframe,'primary key', 'green')
    TKlighter.custom_h(queryframe,'procedure', 'green')
    TKlighter.custom_h(queryframe,'right join', 'green')
    TKlighter.custom_h(queryframe,'rownum', 'green')
    TKlighter.custom_h(queryframe,'select', 'green')
    TKlighter.custom_h(queryframe,'select distinct', 'green')
    TKlighter.custom_h(queryframe,'select into', 'green')
    TKlighter.custom_h(queryframe,'select top', 'green')
    TKlighter.custom_h(queryframe,'set', 'green')
    TKlighter.custom_h(queryframe,'table', 'green')
    TKlighter.custom_h(queryframe,'top', 'green')
    TKlighter.custom_h(queryframe,'truncate table', 'green')
    TKlighter.custom_h(queryframe,'union', 'green')
    TKlighter.custom_h(queryframe,'union all', 'green')
    TKlighter.custom_h(queryframe,'unique', 'green')
    TKlighter.custom_h(queryframe,'update', 'green')
    TKlighter.custom_h(queryframe,'values', 'green')
    TKlighter.custom_h(queryframe,'view', 'green')
    TKlighter.custom_h(queryframe,'where', 'green')



def runq(event=None):
    global df
    def on_dclick(event=None):
        curItem = tree2.focus()
        sel=tree2.item(curItem)
        d=list(zip(list(col), sel['values']))
        d=json.dumps(d)
        root.clipboard_clear()
        root.clipboard_append(d)
        messagebox.showinfo('test',d)
    try:
        exe_query = queryframe.selection_get()
    #except :
        #exe_query=''
        p=queryframe.index('sel.first')
        queryframe.mark_set("insert", p)  #queryframe.index(tk.INSERT))
        if event is None:
            pass
        else:
            queryframe.insert(p, exe_query)
        if exe_query.strip()=='':
            pass
        else:

            col=()
            con1 = sqlite3.connect(db_path)
            cur1 = con1.cursor()
            try:
                cur1.execute(exe_query)
                rows = cur1.fetchall()
                #df = pd. DataFrame(rows, columns = cur1.description)
                try:
                    for widgets in f3.winfo_children():
                        widgets.destroy()
                    for d in cur1.description:
                        col=(*col,d[0])
                    df = pd. DataFrame(rows, columns = col)
                    #col=("c1","c2","c3")
                    tree2 = ttk.Treeview(f3,  column=col, show='tree headings')
                    tree2.bind('<Double-1>', on_dclick)
                    tree2.column('#0', width=0, stretch=NO)
                    for i in enumerate(col):
                        tree2.column("#"+str(int(i[0])+1))
                        tree2.heading("#"+str(int(i[0])+1), text=i[1])
                    # add a scrollbar
                    scrollbar3 = ttk.Scrollbar(f3, orient=tk.VERTICAL, command=tree2.yview)
                    tree2.configure(yscroll=scrollbar3.set)
                    scrollbar3.pack(side=tk.RIGHT, fill=tk.Y)
                    scrollbar4 = ttk.Scrollbar(f3, orient=tk.HORIZONTAL, command=tree2.xview)
                    tree2.configure(xscroll=scrollbar4.set)
                    scrollbar4.pack(side=tk.BOTTOM, fill=tk.X)
                    #messagebox.showinfo('test',cur1.description[0][0])    
                    for row in rows:
                        #print(row) 
                        tree2.insert("", tk.END, values=row)        
                    con1.close()
                    tree2.pack(side=tk.LEFT,fill="both", expand=Y)
                except:
                    df=pd.DataFrame()
            except Exception as e:
                messagebox.showinfo('Error',e)
    except :
        exe_query=''

def lics():
    msg="""
MIT License

Copyright (c) [2021] [Joy Maitra]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
    """
    messagebox.showinfo('License',msg)

def help_key():
    msg="""
To execute the       : Select the query and press <ctl+enter>
query
Copy items from      : Select the item then right click on it.
Browser panel   
Copy a record from   : Double click on the record. 
the output panel
    """
    messagebox.showinfo('Help',msg)

def abt():
    msg= """
Version : 1.0.0.0
From : SparrowSolutions
Link : https://SparrowSolutions.github.io/Home/
    """
    messagebox.showinfo('About',msg)

# Creating Menubar
menubar = Menu(root)

# Adding File Menu and commands
file = Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='File', menu = file)
file.add_command(label ='Load File', command = browseFiles)
file.add_command(label ='Refresh', command = refresh)
file.add_command(label ='Drop table', command = t_drop)
file.add_separator()
file.add_command(label ='New File', command = new_file)
file.add_command(label ='Open', command = open_file)
file.add_command(label ='Save', command = save_file)
file.add_command(label ='Save As', command = save_as_file)
file.add_separator()
file.add_command(label ='Exit', command = root.destroy)

run = Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='Run', menu = run)
run.add_command(label ='Run query', command = runq)
run.add_command(label ='Export Output', command = export_df)

more = Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='More', menu = more)
more.add_command(label ='Help', command = help_key)
more.add_command(label ='License', command = lics)
more.add_command(label ='About', command = abt)

# creating the table browser
f=tk.Frame(root)
tree = ttk.Treeview(f,  column=("c1"), show='tree headings')
tree.column('#0', width=20, stretch=NO)
tree.column("#1")
tree.heading("#1", text="Tables")
tab=get_table_name()
for i in enumerate(tab):
    tree.insert(parent='', index=i[0], iid=i[0],text='', values=(i[1]))
    col = get_col(i[1])
    for j in enumerate(col):
        tree.insert(parent=i[0], index=j[0], text='', values=(j[1]))
# add a scrollbar
scrollbar = ttk.Scrollbar(f, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(side=tk.LEFT,fill=tk.Y)
tree.bind('<Button-3>',get_ele)

#create the query canvas
f2=tk.Frame(root, bg ="red")
queryframe=Text(f2,undo=True)
scrollbar1 = ttk.Scrollbar(f2, orient=tk.VERTICAL, command=queryframe.yview)
scrollbar2 = ttk.Scrollbar(f2, orient=tk.HORIZONTAL, command=queryframe.xview)
queryframe.configure(yscroll=scrollbar1.set)
queryframe.configure(xscroll=scrollbar2.set)
queryframe.configure(font=myFont)
queryframe.configure(selectbackground='#9494b8')
scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar2.pack(side=tk.BOTTOM, fill=tk.X)
queryframe.bind('<Control-Return>', runq)
queryframe.bind('<Key>',hl)

# create the query output canvas
f3=tk.Frame(root,width=20,height=50)
#tree2 = ttk.Treeview(f3,  column=col, show='tree headings')


# display items
root.config(menu = menubar)
f.pack(side=tk.LEFT, fill=tk.Y)
queryframe.pack(side=tk.LEFT, fill="both", expand=Y)
f2.pack(side=tk.TOP, fill=tk.X)

f3.pack(side=tk.TOP,fill=tk.BOTH, expand=Y)

mainloop()
