from tkinter import *
import webbrowser
import tkinter.messagebox
from PIL import Image, ImageTk
from pathlib import Path
from os.path import join, realpath
from tkinter import filedialog as fd
import src.model.crawler as crawler
import src.util.constant as const
import src.util.util as util
from src.ui.charts import BarChart, PieChart
import sys


class TopFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, width=800, height=100, bg='white', border=0)
        self.parent=parent
        self.create_widgets()
        
    def create_widgets(self):
        app_label = Label(self, text = const.app_str,font=("Arial", 18), bg='white')
        limitation_show_label = Label(self, text = '[?]',font=("Arial", 10), bg='white', fg="blue", cursor="hand2")
        limitation_show_label.bind("<Button-1>", lambda e: self.parent.infoFrame.place(x=50, y=35, anchor=NW))
        scan_dir_btn = Button(self, text = const.scandir_str, font=("Arial", 9), bg='white', command=self.scan_dir)
        self.back_dir_link = Label(self, text = '[Back]',font=("Arial", 10), bg='white', fg="blue", cursor="hand2")
        self.back_dir_link.bind("<Button-1>", lambda e: self.display_parent_dir())

        self.curr_dir_label = Label(self, text = "",font=("Arial", 11), bg='white', fg="black")
        if hasattr(sys, '_MEIPASS'):
            asset_dir = Path(sys._MEIPASS) / "asset"
        else:
            asset_dir = Path(__file__).resolve().parent.parent / "asset"
        dir_img = Image.open(asset_dir / const.dir_image_name)  # Adjusted path for pyinstaller
        self.dir_img_photo = ImageTk.PhotoImage(dir_img.resize((20, 20)))
        dir_img_label = Label(self, image=self.dir_img_photo, bg='white', cursor="hand2")
        dir_img_label.bind("<Button-1>", lambda e: self.dir_info_clicked())

        app_label.place(relx=0.5, x=-100)
        limitation_show_label.place(relx=1, y=6, anchor='ne')
        scan_dir_btn.place(x=9, y=55)
        self.curr_dir_label.place(x=68, y=57)
        dir_img_label.place(relx=1, y=50, anchor='ne')


    def display_parent_dir(self):
        curr_dir_path=self.parent.state['curr_dir_path']
        if(curr_dir_path != self.parent.state['root_dir_path']):
            curr_dir_path=realpath(Path(curr_dir_path).parent)
            print(f"curr_dir_path:{curr_dir_path}, self.parent.state['curr_dir_path']:{self.parent.state['curr_dir_path']}")
            self.parent.draw_all(curr_dir_path)
        # After Drawing charts, check if curr_dir matches with root_dir
        if(curr_dir_path == self.parent.state['root_dir_path']):
            self.back_dir_link.place_forget()

    def dir_info_clicked(self):
        curr_dir_path=self.parent.state['curr_dir_path']
        print(f"curr_dir_path={curr_dir_path}")
        if(curr_dir_path!=''):
            tkinter.messagebox.showinfo("Directory full path", f"{curr_dir_path} \n[{self.parent.state['dirs_dict'][curr_dir_path].size} Byte]")

    def update_dir_size(self, curr_dir_detail):
        curr_dir_size = util.format_bytes(curr_dir_detail.size)
        print(f"Curr_dir_path:{self.parent.state['curr_dir_path']} curr_dir_size:{curr_dir_size}")
        self.curr_dir_label['text'] = util.format_obj_name(curr_dir_detail, True) + f' [{curr_dir_size}]' #updating current_dir label

    def scan_dir(self):
        dirName = fd.askdirectory(
            title='Open a Directory',
            initialdir='/')
        if(dirName != ""):
            curr_dir_str=realpath(Path(dirName))
            self.parent.state['root_dir_path']=curr_dir_str
            self.parent.state['dirs_dict'] = crawler.crawl_dir(curr_dir_str)
            
            self.parent.draw_all(curr_dir_str)


class InfoFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, width=700, height=100, bg='lightblue', border=0)
        self.create_widgets()
        
    def create_widgets(self):
        limitation_header_label = Label(self, text = "App limitations:",font=("Arial", 11), bg='lightblue')
        limitation_close_label = Label(self, text = "[Close]",font=("Arial", 9), bg='lightblue', fg="blue", cursor="hand2")
        limitation_close_label.bind("<Button-1>", lambda e: self.place_forget())
        limitation1_label = Label(self, text = const.limitation1_txt, font=("Arial", 10), bg='lightblue')
        limitation1_link = Label(self, text=const.limitation1_link_txt, font=('Helveticabold', 10), bg="lightblue", fg="blue", cursor="hand2")
        limitation1_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab(const.limitation_windows_doc_url))

        limitation2_label = Label(self, text = const.limitation2_txt, font=("Arial", 10), bg='lightblue')
        limitation3_label = Label(self, text = const.limitation3_txt, font=("Arial", 10), bg='lightblue')

        limitation_header_label.place(x=10, y=10)
        limitation_close_label.place(relx=1, y=8, anchor='ne')
        limitation1_label.place(x=10, y=32)
        limitation1_link.place(relx=0.7, y=32, anchor='ne')
        limitation2_label.place(x=10, y=52)
        limitation3_label.place(x=10, y=72)


class ChartFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='white', width=400, height=400, border=0)
        self.create_widgets()
        self.parent=parent
        
    def create_widgets(self):
        self.chartCanvas = Canvas(self, width=400, height=400, bg='white', highlightthickness=0)
        self.chartCanvas.pack(expand=1, side = RIGHT)
        self.barChart=BarChart(self)
        self.pieChart=PieChart(self)

    def draw_chart_dropdown(self, curr_dir_detail, chartPortions):
        chart_dropdown_opt = [const.barchart_str, const.piechart_str]
        chart_dropdown_val = StringVar(self.chartCanvas)
        chart_dropdown_val.set(self.parent.state['chart_selected']) #selected value in dropdown
        self.chart_dropdown = OptionMenu(self.chartCanvas, chart_dropdown_val, *chart_dropdown_opt, command = lambda selected_val=chart_dropdown_val.get(), curr_dir_obj=curr_dir_detail, data=chartPortions : self.dropdown_changed(selected_val, data))
        self.chart_dropdown.config(bg="white",border=2,relief="raised")
        self.chart_dropdown["menu"].config(bg="white")
        self.chart_dropdown.place(x=10, y=10)

    def dropdown_changed(self, dropdown_val, data):
        self.parent.state['chart_selected']=dropdown_val
        self.draw_chart(data)

    def draw_chart(self, data):
        self.parent.clear_canvas(self)

        curr_dir_detail = self.parent.state['dirs_dict'][self.parent.state['curr_dir_path']]
        if(curr_dir_detail.size==0): 
            return

        if(self.parent.state['chart_selected']==const.barchart_str):
            self.barChart.draw(data)
        elif(self.parent.state['chart_selected']==const.piechart_str):
            self.pieChart.draw(data)
        else:
            pass

    def pie_chart_clicked(self, event, obj):
        global is_chart_clicked
        is_chart_clicked = True
        if(obj and obj.is_dir):
            self.parent.draw_all(obj.full_path)
            self.parent.topFrame.back_dir_link.place(relx=0.63, y=78, anchor='ne')

        print(f"Clicked object. Co-ordinate: [{event.x}, {event.y}] , event.num: {event.num}, full_path:{obj.full_path}")


 
class ListingFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='white', width=400, height=400, border=0)
        self.create_widgets()
        self.parent=parent
        
    def create_widgets(self):
        self.listBoxCanvas = Canvas(self, bg="white", width=400, height=400, highlightthickness=0)
        self.listBoxCanvas.pack(side = LEFT, fill = BOTH , expand = 2, pady=5)

    def draw_listbox(self, chartViewDetailList, child_objects):
        yHeight = 0
        counter=0

        for obj in child_objects:
            # Creating new ListBoxes for the current Scan Dir result
            labelFrame = LabelFrame(self.listBoxCanvas, border=0)
            labelFrame.grid(column=0, row=0, padx=2, pady=2)
            label1 = Label(labelFrame,text=util.format_bytes(obj.size), font=("Courier", 9), compound=RIGHT, bg=const.default_chart_color, bd=0)
            label2 = Label(labelFrame,text=util.format_obj_name(obj), font=("Courier", 9), compound=RIGHT, bg="white")
            label3 = Label(labelFrame,text=const.dir_str, font=("Courier", 9), compound=RIGHT, bg="white")
            
            label1.grid(column=0, row=0, padx=2, pady=2)
            label2.grid(column=1, row=0, ipadx=1, ipady=1)
            if(obj.is_dir):
                label2.config(fg="blue", cursor="hand2")
                label2.bind("<Button-1>", lambda e,dir_full_path=obj.full_path: self.listBoxWindow_clicked(dir_full_path))
                label3.grid(column=2, row=0, ipadx=1, ipady=1)  # Display label 'Folder' only when obj is a directory
            if(counter < len(chartViewDetailList)):
                label1.config(bg=const.chart_colors[chartViewDetailList[counter].rank])
                counter+=1

            self.listBoxCanvas.create_window(0, yHeight, window=labelFrame, anchor=NW)
            yHeight += 22
        self.listBoxCanvas['scrollregion']=(0, 0, 0, yHeight)
        scrollbar = Scrollbar(self.listBoxCanvas, orient=VERTICAL, command=self.listBoxCanvas.yview)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor=NE)
        self.listBoxCanvas['yscrollcommand']=scrollbar.set

        self.listBoxCanvas.bind_all("<MouseWheel>", "break") # By default mousewheel scroll should be stopped

        if(yHeight > self.listBoxCanvas.winfo_height()):
            # If listBox actual height more than max allowed height mousewheel is allowed
            self.listBoxCanvas.bind_all("<MouseWheel>", self.mousewheel_moved)

        print(f"yHeight:{yHeight}, listBoxCanvas.winfo_height:{self.listBoxCanvas.winfo_height()}")

    def listBoxWindow_clicked(self, dir_full_path):
        self.parent.draw_all(dir_full_path)
        self.parent.topFrame.back_dir_link.place(relx=0.63, y=78, anchor='ne')

    def mousewheel_moved(self, event):
        self.listBoxCanvas.yview_scroll(int(-1*(event.delta/120)), "units")
