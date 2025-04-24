# GUI 4 TrajecSiumu
from tkinter import*
from tkinter import filedialog
import tkinter.ttk as ttk
import numpy as np
from Scripts.interface import TrajecSimu_UI
import tkinter.messagebox as msg
from Scripts.errors import ParameterDefineError

'''
2022.10.27 Kimdongmin (Hyon)

エラーがあったら改善しますので教えてください ❕
[ kimdongmin2248@gmail.com ]
'''

# GUI ----------
gui = Tk()
gui.title('TrajecSimu')
gui.geometry('500x320+300+200')
gui.resizable(False,False)

parameter_frame = LabelFrame(gui,text='Parameter File (*.csv)')
parameter_frame.pack(fill='x',padx=10,ipady=5)

parameter_path = Entry(parameter_frame,width=70)
parameter_path.pack(pady=5)

find_btn = Button(parameter_frame,text='open',width=10,command=lambda:find_csv())
find_btn.pack()

# location
location_frame = LabelFrame(gui,text='Location')
location_frame.pack(fill='x',padx=10,pady=10)

loca_comb = ttk.Combobox(location_frame,values=['能代','伊豆大島'],state='readonly')
loca_comb.pack(padx=50)
loca_comb.current(0)

Land_or_Sea = ttk.Combobox(location_frame,values=['陸','海'],state='readonly')
Land_or_Sea.pack()
Land_or_Sea.current(0)

# run mode
runmode_frame = Frame(gui)
runmode_frame.pack(pady=5)

mode_var = IntVar()

single_radiobtn = Radiobutton(runmode_frame,text='single run',value=1,variable=mode_var)
single_radiobtn.pack(side='left',padx=50)

loop_radiobtn = Radiobutton(runmode_frame,text='Loop run',value=2,variable=mode_var)
loop_radiobtn.pack(side='right',padx=50)

# loop running format
format_frame = LabelFrame(gui,text='Format for loop run')
format_frame.pack(fill='x',padx=10)

n_winddirec_frame = Frame(format_frame)
n_winddirec_frame.pack(side='left',padx=10,pady=5)

n_winddirec_label = Label(n_winddirec_frame,text='number of wind directions')
n_winddirec_label.pack()

n_winddirec_comb_val = [1,2,4,8,16,36]
n_winddirec_comb = ttk.Combobox(n_winddirec_frame,values=n_winddirec_comb_val,state='readonly')
n_winddirec_comb.pack(pady=3)

max_windspeed_frame = Frame(format_frame)
max_windspeed_frame.pack(side='left',padx=10,pady=5)

max_windspeed_label = Label(max_windspeed_frame,text='max wind speed [m/s]')
max_windspeed_label.pack()

max_windspeed_entry = Entry(max_windspeed_frame)
max_windspeed_entry.pack(pady=3)

windspeed_step_frame = Frame(format_frame)
windspeed_step_frame.pack(side='left',padx='10',pady=5)

windspeed_step_label =Label(windspeed_step_frame,text='wind speed step [m/s]')
windspeed_step_label.pack()

windspeed_step_entry = Entry(windspeed_step_frame)
windspeed_step_entry.pack(pady=3)

# run button
run_btn = Button(gui,text='Run',width=10,fg='yellow',bg='red',command=lambda:running(parameter_path.get(),mode_var.get(),n_winddirec_comb.get(),max_windspeed_entry.get(),windspeed_step_entry.get(),loca_comb.get(),Land_or_Sea.get()))
run_btn.pack(pady=10)

# Functuin ----------
def find_csv():
    file_selected = filedialog.askopenfilename(filetypes=(("csvファイル","*.csv"),("すべて","*.*")))
    parameter_path.delete(0,END)
    parameter_path.insert(0,file_selected)

def running(path,mode_var,w_direc,max_w,w_step,loca1,loca2):
    try:
        if loca1 == '伊豆大島' and loca2 == '陸':
            loca = 'izu'
        elif loca1 == '伊豆大島' and loca2 == '海':
            loca = 'izu_sea'
        elif loca1 == '能代' and loca2 == '陸':
            loca = 'noshiro'
        elif loca1 == '能代' and loca2 == '海':
            loca = 'noshiro_sea'
        simu = gui_run(path,mode_var,w_direc,max_w,w_step,loca)
        simu.SorL()
    except FileNotFoundError:
        msg.showerror(title='File Not Found Error',message='ファイルが見つかりませんでした')
    except modeselecterror:
        msg.showerror(title='Mode Select Error',message='single runまたは loop runを選択してください')
    except formaterror:
        msg.showerror(title='Loop run Format Error',message='loop run formatを確かめてください')
    except ParameterDefineError:
        msg.showerror(title='Prameter Define Error',message='Parameter Fileを確かめてください')
    except AttributeError:
        msg.showerror(title='Attribute Error',message='Parameter Fileを確かめてください')

class gui_run:
    def __init__(self,path,mode_var,w_direc,max_w,w_step,loca):
        self.path = path
        self.mode_var = mode_var
        try:
            self.w_direc = int(w_direc)
        except:
            self.w_direc = -1
        try:
            self.max_w = float(max_w)
        except:
            self.max_w = -1
        try:
            self.w_step = float(w_step)
        except:
            self.w_step = -1
        self.loca = loca
    def SorL(self):
        if self.mode_var == 1:
            S = gui_run(self.path,self.mode_var,self.w_direc,self.max_w,self.w_step,self.loca)
            S.single_run()
        elif self.mode_var == 2:
            L = gui_run(self.path,self.mode_var,self.w_direc,self.max_w,self.w_step,self.loca)
            if self.w_direc == -1 or self.max_w == -1 or self.w_step == -1:
                raise formaterror
            else:
                L.loop_run()
        else:
            raise modeselecterror
    def single_run(self):
        simu = TrajecSimu_UI(self.path,self.loca)
        simu.run_single()
    def loop_run(self):
        simu = TrajecSimu_UI(self.path,self.loca)
        simu.run_loop(self.w_direc,self.max_w,self.w_step)

# exception ----------
class modeselecterror(Exception):
    pass
class formaterror(Exception):
    pass

# run GUI!
gui.mainloop()