from tkinter import *
import webbrowser
import tkinter.messagebox
from PIL import Image, ImageTk
from pathlib import Path
from os.path import join, realpath
from tkinter import filedialog as fd
import DirectoryCrawler as crawler
from DirectoryCrawler import ObjectDetail
import math
import Constant as const
import Util as util


class ChartViewDetail:
    def __init__(self, rank: int, objectDetail: ObjectDetail, obj_size_fraction:float):
        self.rank=rank
        self.objectDetail=objectDetail
        self.obj_size_fraction=obj_size_fraction


def scan_dir():
    dirName = fd.askdirectory(
        title='Open a Directory',
        initialdir='/')
    if(dirName != ""):
        curr_dir_str=realpath(Path(dirName))
        global root_dir_path
        root_dir_path=curr_dir_str

        global dirs_dict
        dirs_dict = crawler.crawl_dir(curr_dir_str)
        
        draw_all(dirs_dict, curr_dir_str)


def draw_all(dirs_dict, curr_dir_str):
    
    canvas_clear(listBoxCanvas)
    canvas_clear(chartCanvas)

    global curr_dir_path
    curr_dir_path=curr_dir_str # Important step while walking up-down the tree

    curr_dir_detail = dirs_dict[curr_dir_path]

    update_dir_size(curr_dir_detail)

    if(curr_dir_detail.size==0): 
        return

    child_objects = get_child_obj(curr_dir_detail)
    chartPortions = get_chart_portions(curr_dir_detail, child_objects)

    draw_chart_dropdown(curr_dir_detail, chartPortions)
    draw_chart(chartPortions)
    draw_listbox(chartPortions, child_objects)


def update_dir_size(curr_dir_detail):
    curr_dir_size = util.format_bytes(curr_dir_detail.size)
    print(f"Curr_dir_path:{curr_dir_path} curr_dir_size:{curr_dir_size}")
    curr_dir_label['text'] = util.format_obj_name(curr_dir_detail, True) + f' [{curr_dir_size}]' #updating current_dir label

def get_child_obj(curr_dir_detail):
    child_object_names = curr_dir_detail.sub_files + curr_dir_detail.sub_dirs
    child_objects = []
    for obj_name in child_object_names:
        try:
            child_objects.append(dirs_dict[join(curr_dir_path,obj_name)])
        except KeyError:
            print(f"In get_dir_view_data: KeyError for Path: {join(curr_dir_path,child_object_names)}")
            pass
    # Sort child_objects in Descending order of size
    child_objects = sorted(child_objects, key=lambda obj: obj.size, reverse=True)
    return child_objects


def get_chart_portions(curr_dir_detail, child_objects):
    chartPortions=[]
    totalTopObjSize=0
    endIndex = len(child_objects)+1 if(len(child_objects)<6) else 6
    for i in range(1, endIndex):
        obj=child_objects[i-1]
        if(obj.size==0): break

        chartPortions.append(ChartViewDetail(i, obj, (obj.size/curr_dir_detail.size)))
        totalTopObjSize+=obj.size
    chartPortions.append(ChartViewDetail(6, ObjectDetail('OTHERS', None, None, None, None), ((curr_dir_detail.size - totalTopObjSize)/curr_dir_detail.size)))
    return chartPortions


def draw_chart_dropdown(curr_dir_detail, chartPortions):
    chart_dropdown_opt = [const.barchart, const.piechart]
    chart_dropdown_val = StringVar(chartCanvas)
    chart_dropdown_val.set(global_state['chart_selected']) #selected value in dropdown
    chart_dropdown = OptionMenu(chartCanvas, chart_dropdown_val, *chart_dropdown_opt, command = lambda selected_val=chart_dropdown_val.get(), curr_dir_obj=curr_dir_detail, data=chartPortions : dropdown_changed(selected_val, data))
    chart_dropdown.config(bg="white",border=2,relief="raised")
    chart_dropdown["menu"].config(bg="white")
    chart_dropdown.place(x=10, y=10)


def draw_listbox(chartViewDetailList, child_objects):
    yHeight = 0
    counter=0

    for obj in child_objects:
        # Creating new ListBoxes for the current Scan Dir result
        labelFrame = LabelFrame(listBoxCanvas, border=0)
        labelFrame.grid(column=0, row=0, padx=2, pady=2)
        label1 = Label(labelFrame,text=util.format_bytes(obj.size), font=("Courier", 9), compound=RIGHT, bg=const.default_chart_color, bd=0)
        label2 = Label(labelFrame,text=util.format_obj_name(obj), font=("Courier", 9), compound=RIGHT, bg="white")
        label3 = Label(labelFrame,text=const.dir_label, font=("Courier", 9), compound=RIGHT, bg="white")
        
        label1.grid(column=0, row=0, padx=2, pady=2)
        label2.grid(column=1, row=0, ipadx=1, ipady=1)
        if(obj.is_dir):
            label2.config(fg="blue", cursor="hand2")
            label2.bind("<Button-1>", lambda e,dir_full_path=obj.full_path: listBoxWindow_clicked(dir_full_path))
            label3.grid(column=2, row=0, ipadx=1, ipady=1)  # Display label 'Folder' only when obj is a directory
        if(counter < len(chartViewDetailList)):
            label1.config(bg=const.chart_colors[chartViewDetailList[counter].rank])
            counter+=1

        listBoxCanvas.create_window(0, yHeight, window=labelFrame, anchor=NW)
        yHeight += 22
    listBoxCanvas['scrollregion']=(0, 0, 0, yHeight)
    scrollbar = Scrollbar(listBoxCanvas, orient=VERTICAL, command=listBoxCanvas.yview)
    scrollbar.place(relx=1, rely=0, relheight=1, anchor=NE)
    listBoxCanvas['yscrollcommand']=scrollbar.set

    listBoxCanvas.bind_all("<MouseWheel>", "break") # By default mousewheel scroll should be stopped

    if(yHeight > listBoxCanvas.winfo_height()):
        # If listBox actual height more than max allowed height mousewheel is allowed
        listBoxCanvas.bind_all("<MouseWheel>", mousewheel_moved)

    print(f"yHeight:{yHeight}, listBoxCanvas.winfo_height:{listBoxCanvas.winfo_height()}")


def dropdown_changed(dropdown_val, data):
    global_state['chart_selected']=dropdown_val
    draw_chart(data)


def draw_chart(data):
    canvas_clear(chartCanvas)

    global curr_dir_path
    curr_dir_detail = dirs_dict[curr_dir_path]
    if(curr_dir_detail.size==0): 
        return

    if(global_state['chart_selected']==const.barchart):
        draw_barchart(data)
    elif(global_state['chart_selected']==const.piechart):
        draw_piechart(data)
    else:
        pass
    

def draw_barchart(chartViewDetailList):
    # The variables below size the bar chart
    bar_chart_width = 400  # Define it's width
    bar_chart_height = 400  # Define it's height
    y_stretch_bar_chart = 3  # The highest y = max_data_value * y_stretch
    x_gap_bar_chart = 50  # The gap between left canvas edge and y axis
    y_gap_bar_chart = 35  # The gap between lower canvas edge and x axis
    x_stretch_bar_chart = 20  # Stretch x wide enough to fit the variables
    x_width_bar_chart = 30  # The width of the x-axis

    for x,item in enumerate(chartViewDetailList):
        bar_chart_item_val=round((item.obj_size_fraction)*100, 2)
        if(bar_chart_item_val==0.0):
            continue
        bar_chart_x0 = x * x_stretch_bar_chart + x * x_width_bar_chart + x_gap_bar_chart  # Bottom left coordinate
        bar_chart_y0 = bar_chart_height - (bar_chart_item_val * y_stretch_bar_chart + y_gap_bar_chart)  # Top left coordinates
        bar_chart_x1 = x * x_stretch_bar_chart + x * x_width_bar_chart + x_width_bar_chart + x_gap_bar_chart  # Bottom right coordinates
        bar_chart_y1 = bar_chart_height - y_gap_bar_chart  # Top right coordinates
        chartBar = chartCanvas.create_rectangle(bar_chart_x0, bar_chart_y0, bar_chart_x1, bar_chart_y1, fill=const.chart_colors[item.rank])  # Draw the bar
        chartCanvas.create_text(bar_chart_x0 + 2, bar_chart_y0, anchor=SW, text=f"{str(bar_chart_item_val)}%" ) # Put the y value above the bar
        chartCanvas.tag_bind(chartBar,"<Button-1>",lambda event,item=item : chart_pie_clicked(event, item.objectDetail))


def draw_piechart(chartViewDetailList):
    start_angle=0
    tot_angle=0
    for x,item in enumerate(chartViewDetailList):
        # print(f"ChartViewDetail: rank:{item.rank}, pie_angle_width:{item.pie_angle_width}, \
        #     ObjectDetail: name:{None if(item.objectDetail is None) else Path(item.objectDetail.full_path).name}, \
        #     size:{None if(item.objectDetail is None) else item.objectDetail.size}, \
        #     is_dir:{None if(item.objectDetail is None) else item.objectDetail.is_dir}, \
        #     sub_files:{None if(item.objectDetail is None) else item.objectDetail.sub_files}, \
        #     sub_dirs:{None if(item.objectDetail is None) else item.objectDetail.sub_dirs}, ")
        # canvasItem = chartCanvas.find_withtag("pie"+str(item.rank))

        pie_angle_width=round((item.obj_size_fraction)*360, 3)
        tot_angle+=pie_angle_width  #tot_angle+=item.pie_angle_width

        if(start_angle>=359):
            continue
        elif(start_angle+pie_angle_width>359):
            pie_angle_width-=start_angle+pie_angle_width-359

        # print(f"AFTER start_angle:{start_angle}, pie_angle_width:{pie_angle_width}")

        chartPie = chartCanvas.create_arc((35,35,360,360), activedash=(50,10), fill=const.chart_colors[item.rank], outline="white", start=start_angle, extent=pie_angle_width, tag="pie"+str(item.rank))
        chartCanvas.tag_bind(chartPie,"<Button-1>",lambda event,item=item : chart_pie_clicked(event, item.objectDetail))
        
        # Percentage of each Pie is Drawn as text outside each Pie.
        percentage=round((item.obj_size_fraction)*100, 2)
        if(percentage>0.00):
            txt = chartCanvas.create_text(1, 1, text=f'{percentage}%')
            chartCanvas.itemconfig(txt)
            _x = math.cos(math.radians(-(start_angle + pie_angle_width/2))) * 180 + 200
            _y = math.sin(math.radians(-(start_angle + pie_angle_width/2))) * 180 + 200
            chartCanvas.coords(txt, _x, _y)
            chartCanvas.lift(txt, chartPie) # superimpose txt on top of Pie

        start_angle+=pie_angle_width


def listBoxWindow_clicked(dir_full_path):
    draw_all(dirs_dict, dir_full_path)
    back_dir_label.place(relx=0.63, y=78, anchor='ne')


def display_parent_dir():
    global dirs_dict
    global curr_dir_path
    global root_dir_path
    if(curr_dir_path != root_dir_path):
        curr_dir_path=realpath(Path(curr_dir_path).parent)
        draw_all(dirs_dict, curr_dir_path)
    # After Drawing charts, check if curr_dir matches with root_dir
    if(curr_dir_path == root_dir_path):
        back_dir_label.place_forget()


def dir_info_clicked():
    global curr_dir_path
    print(f"curr_dir_path={curr_dir_path}")
    if(curr_dir_path!=''):
        tkinter.messagebox.showinfo("Directory full path", f"{curr_dir_path} \n[{dirs_dict[curr_dir_path].size} Byte]")


def canvas_clear(canvas):
    canvas.delete("all")


def chart_pie_clicked(event, obj):
    global is_chart_clicked
    is_chart_clicked = True
    if(obj and obj.is_dir):
        draw_all(dirs_dict, obj.full_path)
        back_dir_label.place(relx=0.63, y=78, anchor='ne')

    print(f"Clicked object. Co-ordinate: [{event.x}, {event.y}] , event.num: {event.num}, full_path:{obj.full_path}")
    

def mousewheel_moved(event):
    listBoxCanvas.yview_scroll(int(-1*(event.delta/120)), "units")



tk = Tk()
tk.geometry("800x500")
tk['bg'] = 'white'
dirs_dict={}
curr_dir_path = ""
root_dir_path = ""
global_state = {'chart_selected':const.barchart}

topFrame = Frame(tk, width=800, height=100, bg='white', border=0)
topFrame.pack_propagate(0)
topFrame.pack(side='top', expand='True', padx=0, pady=0)

chartFrame = Frame(tk, bg='white', width=400, height=400, border=0)
chartFrame.pack_propagate(0)
chartFrame.pack(fill='x', side='left', expand='True', anchor='s')

listBoxFrame = Frame(tk, bg='white', width=400, height=400, border=0)
listBoxFrame.pack_propagate(0)
listBoxFrame.pack(fill='x', side='right', expand='True', anchor='s')

app_label = Label(topFrame, text = const.app_label,font=("Arial", 18), bg='white')
limitation_show_label = Label(topFrame, text = '[?]',font=("Arial", 10), bg='white', fg="blue", cursor="hand2")
limitation_show_label.bind("<Button-1>", lambda e: limitationFrame.place(x=30, y=35, anchor=NW))
scan_dir_btn = Button(topFrame, text = "Scan Dir",font=("Arial", 9), bg='white', command=scan_dir)
back_dir_label = Label(topFrame, text = '[Back]',font=("Arial", 10), bg='white', fg="blue", cursor="hand2")
back_dir_label.bind("<Button-1>", lambda e: display_parent_dir())

curr_dir_label = Label(topFrame, text = "",font=("Arial", 11), bg='white', fg="black")
dir_img = Image.open(join(Path(__file__).resolve().parent, "file-open-icon.png"))
dir_img_photo = ImageTk.PhotoImage(dir_img.resize((20, 20)))
dir_img_label = Label(topFrame, image=dir_img_photo, bg='white', cursor="hand2")
dir_img_label.bind("<Button-1>", lambda e: dir_info_clicked())

app_label.place(relx=0.5, x=-100)
limitation_show_label.place(relx=1, y=6, anchor='ne')
scan_dir_btn.place(x=9, y=55)
curr_dir_label.place(x=68, y=57)
dir_img_label.place(relx=1, y=55, anchor='ne')
# back_dir_label.place(relx=0.63, y=78, anchor='ne')


limitationFrame = Frame(tk, width=700, height=125, bg='lightblue', border=0)
limitation_header_label = Label(limitationFrame, text = "App limitations:",font=("Arial", 11), bg='lightblue')
limitation_close_label = Label(limitationFrame, text = "[Close]",font=("Arial", 9), bg='lightblue', fg="blue", cursor="hand2")
limitation_close_label.bind("<Button-1>", lambda e: limitationFrame.place_forget())
limitation1_label = Label(limitationFrame, text = "- Directory with Path longer than  260 characters will be ignored by",font=("Arial", 10), bg='lightblue')
limitation1_link = Label(limitationFrame, text='Windows API.',font=('Helveticabold', 10), bg="lightblue", fg="blue", cursor="hand2")
limitation1_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab('https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation'))

limitation2_label = Label(limitationFrame, text = "- Large Directory scan takes time and UI freezes. Currently there is no 'Progress bar' or a 'Stop Scan' button feature.",font=("Arial", 10), bg='lightblue')
limitation3_label = Label(limitationFrame, text = "- Pie chart hides a pie with less than 1 degree width, due to limitation with Tkinter library",font=("Arial", 10), bg='lightblue')
limitation4_label = Label(limitationFrame, text = "- App is not responsive UI, i.e. screen elements don't adjust position if you resize Window.",font=("Arial", 10), bg='lightblue')

limitation_header_label.place(x=10, y=10)
limitation_close_label.place(relx=1, y=8, anchor='ne')
limitation1_label.place(x=10, y=32)
limitation1_link.place(relx=0.7, y=32, anchor='ne')
limitation2_label.place(x=10, y=52)
limitation3_label.place(x=10, y=72)
limitation4_label.place(x=10, y=92)


chartCanvas = Canvas(chartFrame, width=400, height=400, bg='white', highlightthickness=0)

is_chart_clicked = False

chartCanvas.pack(expand=1, side = RIGHT)

listBoxCanvas = Canvas(listBoxFrame, bg="white", width=400, height=400, highlightthickness=0)
listBoxCanvas.pack(side = LEFT, fill = BOTH , expand = 2, pady=5)




tk.mainloop()