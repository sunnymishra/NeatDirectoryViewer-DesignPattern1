from tkinter import *
import webbrowser
import tkinter.messagebox
from PIL import Image, ImageTk
from pathlib import Path
from os.path import join, realpath
from tkinter import filedialog as fd
import math
import os
from os.path import join, getsize

# Directory Crawler code here:
class FSObjectDetail:
    def __init__(self, full_path: str, sub_files: list, sub_dirs: list, size: int, is_dir: bool) -> None:
        self.full_path = full_path
        self.sub_files = sub_files
        self.sub_dirs = sub_dirs
        self.size = size
        self.is_dir = is_dir

def crawl_dir(dir_path):
    dirs_dict = {}

    for current_dir_path, sub_dirs, sub_files in os.walk(dir_path,topdown = False):
        # Walk the directory tree from bottom to top fashion.
        if '$Recycle.Bin' in current_dir_path:
            # print(f"Ignoring current loop. root:{current_dir_path}")
            continue
        if '$Recycle.Bin' in sub_dirs: sub_dirs.remove('$Recycle.Bin')
        if 'Config.Msi' in sub_dirs: sub_dirs.remove('Config.Msi')
        
        files_size=0
        for sub_file_name in sub_files:
            # Loop through every file in this directory and sum their sizes
            try:
                sub_file_path = join(current_dir_path, sub_file_name)
                file_size=getsize(sub_file_path)
                files_size+=file_size
                dirs_dict[sub_file_path] = FSObjectDetail(sub_file_path, None, None, file_size, False)
                # print(f"sub_file_name:{sub_file_name}, sub_file_path:{sub_file_path}, file_size:{file_size}")
            except FileNotFoundError:
                # print(f"FileNotFoundError for Path: {join(current_dir_path,sub_file_name)}")
                pass
        
        subdir_size=0
        for sub_dir_name in sub_dirs:
            # Loop through every sub-directory in this Parent directory and sum their sizes
            try:
                directoryDetail = dirs_dict[join(current_dir_path,sub_dir_name)]
                dir_size=directoryDetail.size
                subdir_size+=dir_size
            except KeyError:
                # print(f"KeyError for Path: {join(current_dir_path,sub_dir_name)}")
                pass
        # store the size of this directory (plus subdirectories) in a dict so we can access it later
        curr_dir_size = files_size + subdir_size
        dirs_dict[current_dir_path] = FSObjectDetail(current_dir_path, sub_files, sub_dirs, curr_dir_size, True)
        
        # print(f"root:{current_dir_path}, curr_dir_name:{curr_dir_name}, files_size:{files_size}, curr_dir_size:{curr_dir_size}, dirs:{sub_dirs}, files:{sub_files}\n---------")
    
    return dirs_dict

# UI Canvas code here
class ChartViewDetail:
    def __init__(self, rank: int, directoryDetail: FSObjectDetail, obj_size_fraction:float):
        self.rank=rank
        self.directoryDetail=directoryDetail
        self.obj_size_fraction=obj_size_fraction

tk = Tk()
tk.geometry("800x500")
tk['bg'] = 'white'
dirs_dict={}
curr_dir_path = ""
root_dir_path = ""
global_state = {'chart_selected':'Bar Chart'}

topFrame = Frame(tk, width=800, height=100, bg='white', border=0)
topFrame.pack_propagate(0)
topFrame.pack(side='top', expand='True', padx=0, pady=0)

chartFrame = Frame(tk, bg='white', width=400, height=400, border=0)
chartFrame.pack_propagate(0)
chartFrame.pack(fill='x', side='left', expand='True', anchor='s')

listBoxFrame = Frame(tk, bg='white', width=400, height=400, border=0)
listBoxFrame.pack_propagate(0)
listBoxFrame.pack(fill='x', side='right', expand='True', anchor='s')
##################################################
def scan():
    dirName = fd.askdirectory(
        title='Open a Directory',
        initialdir='/')
    if(dirName != ""):
        curr_dir_str=realpath(Path(dirName))
        global root_dir_path
        root_dir_path=curr_dir_str

        global dirs_dict
        dirs_dict = crawl_dir(curr_dir_str)
        
        canvas_data(dirs_dict, curr_dir_str)

def canvas_data(dirs_dict, curr_dir_str):
    
    canvas_clear(listBoxCanvas)
    canvas_clear(chartCanvas)

    global curr_dir_path
    curr_dir_path=curr_dir_str # Important step while walking up-down the tree

    curr_dir_detail = dirs_dict[curr_dir_path]

    curr_dir_size = format_byte(curr_dir_detail.size)
    print(f"Curr_dir_path:{curr_dir_path} curr_dir_size:{curr_dir_size}")
    curr_dir_label['text'] = 'Current Dir: '+ format_str(curr_dir_detail, True) + f' [{curr_dir_size}]' #curr_dir_path

    if(curr_dir_detail.size==0): 
        return

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
    chartViewDetailList=[]
    totalTopObjSize=0
    endIndex = len(child_objects)+1 if(len(child_objects)<6) else 6
    for i in range(1, endIndex):
        obj=child_objects[i-1]
        if(obj.size==0): break

        chartViewDetailList.append(ChartViewDetail(i, obj, (obj.size/curr_dir_detail.size)))
        totalTopObjSize+=obj.size
    chartViewDetailList.append(ChartViewDetail(6, FSObjectDetail('OTHERS', None, None, None, None), ((curr_dir_detail.size - totalTopObjSize)/curr_dir_detail.size)))  # round(((curr_dir_detail.size - totalTopObjSize)/curr_dir_detail.size)*360, 3)

    chart_dropdown_opt = ['Bar Chart', 'Pie Chart']
    chart_dropdown_val = StringVar(chartCanvas)
    chart_dropdown_val.set(global_state['chart_selected']) #selected value in dropdown
    chart_dropdown = OptionMenu(chartCanvas, chart_dropdown_val, *chart_dropdown_opt, command = lambda      selected_val=chart_dropdown_val.get(), data=chartViewDetailList : dropdown(selected_val, curr_dir_detail.full_path))

    chart_dropdown.config(bg="white",border=2,relief="raised")
    chart_dropdown["menu"].config(bg="white")
    chart_dropdown.place(x=10, y=10)
    chart_colors={1:"#EA5D57", 2:"#FDC135", 3:"#4FB3E8", 4:"#99CF43", 5:"#08AEA1", 6:"#AAAAAA"}

    # Draw Bar Chart
    if(global_state['chart_selected']=='Bar Chart'):
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
            chartBar = chartCanvas.create_rectangle(bar_chart_x0, bar_chart_y0, bar_chart_x1, bar_chart_y1, fill=chart_colors[item.rank])  # Draw the bar
            chartCanvas.create_text(bar_chart_x0 + 2, bar_chart_y0, anchor=SW, text=f"{str(bar_chart_item_val)}%" ) # Put the y value above the bar
            chartCanvas.tag_bind(chartBar,"<Button-1>",lambda event,item=item : chart_pie_clicked(event, item.directoryDetail))

    # Draw Pie Chart
    elif(global_state['chart_selected']=='Pie Chart'):
        start_angle=0
        tot_angle=0
        for x,item in enumerate(chartViewDetailList):
            # Updating the Chart pies
            # print(f"ChartViewDetail: rank:{item.rank}, pie_angle_width:{item.pie_angle_width}, \
            #     DirectoryDetail: name:{None if(item.directoryDetail is None) else Path(item.directoryDetail.full_path).name}, \
            #     size:{None if(item.directoryDetail is None) else item.directoryDetail.size}, \
            #     is_dir:{None if(item.directoryDetail is None) else item.directoryDetail.is_dir}, \
            #     sub_files:{None if(item.directoryDetail is None) else item.directoryDetail.sub_files}, \
            #     sub_dirs:{None if(item.directoryDetail is None) else item.directoryDetail.sub_dirs}, ")
            # canvasItem = chartCanvas.find_withtag("pie"+str(item.rank))

            pie_angle_width=round((item.obj_size_fraction)*360, 3)
            tot_angle+=pie_angle_width  #tot_angle+=item.pie_angle_width

            print(f"BEFORE start_angle:{start_angle}, pie_angle_width:{pie_angle_width}")

            if(start_angle>=359):
                continue
            elif(start_angle+pie_angle_width>359):
                pie_angle_width-=start_angle+pie_angle_width-359

            print(f"AFTER start_angle:{start_angle}, pie_angle_width:{pie_angle_width}")

            chartPie = chartCanvas.create_arc((35,35,360,360), activedash=(50,10), fill=chart_colors[item.rank], outline="white", start=start_angle, extent=pie_angle_width, tag="pie"+str(item.rank))
            chartCanvas.tag_bind(chartPie,"<Button-1>",lambda event,item=item : chart_pie_clicked(event, item.directoryDetail))
            
            # Percentage of each Pie is Drawn as text outside each Pie.
            percentage=round((item.obj_size_fraction)*100, 2)
            if(percentage>0.00):
                txt = chartCanvas.create_text(1, 1, text=f'{percentage}%')
                chartCanvas.itemconfig(txt)
                _x = math.cos(math.radians(-(start_angle + pie_angle_width/2))) * 180 + 200
                _y = math.sin(math.radians(-(start_angle + pie_angle_width/2))) * 180 + 200
                chartCanvas.coords(txt, _x, _y)
                chartCanvas.lift(txt, chartPie) # superimpose txt on top of Pie

            start_angle+=pie_angle_width  # start_angle+=item.pie_angle_width
    else:
        pass
    
    # Draw List Boxes
    yHeight = 0
    counter=0

    for obj in child_objects:
        # Creating new ListBoxes for the current Scan Dir result
        labelFrame = LabelFrame(listBoxCanvas, border=0)
        labelFrame.grid(column=0, row=0, padx=2, pady=2)
        label1 = Label(labelFrame,text=format_byte(obj.size), font=("Courier", 9), compound=RIGHT, bg="#AAAAAA", bd=0)
        label2 = Label(labelFrame,text=format_str(obj), font=("Courier", 9), compound=RIGHT, bg="white")
        label3 = Label(labelFrame,text='[Folder]', font=("Courier", 9), compound=RIGHT, bg="white")
        
        label1.grid(column=0, row=0, padx=2, pady=2)
        label2.grid(column=1, row=0, ipadx=1, ipady=1)
        if(obj.is_dir):
            label2.config(fg="blue", cursor="hand2")
            label2.bind("<Button-1>", lambda e,dir_full_path=obj.full_path: listBoxWindow_clicked(dir_full_path))
            label3.grid(column=2, row=0, ipadx=1, ipady=1)  # Display label 'Folder' only when obj is a directory
        if(counter < len(chartViewDetailList)):
            label1.config(bg=chart_colors[chartViewDetailList[counter].rank])
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
        listBoxCanvas.bind_all("<MouseWheel>", scroll)

    print(f"yHeight:{yHeight}, listBoxCanvas.winfo_height:{listBoxCanvas.winfo_height()}")

def dropdown(dropdown_val, dir_full_path):
    global_state['chart_selected']=dropdown_val
    canvas_data(dirs_dict, dir_full_path)

def format_str(obj, is_top_display=False):
    max_name_len=35 if(obj.is_dir) else 35+len('[Folder]')+1
    if(is_top_display):
        max_name_len=75
    name=obj.full_path if is_top_display else Path(obj.full_path).name
    if(len(name)>max_name_len):
        charLenToStrip=len(name)-max_name_len+3  # Here 3 is for the 3 dots ... to be displayed in cropped final String.
        listbox_large_name_strip_start_idx=int(max_name_len/2)
        name = name[0: listbox_large_name_strip_start_idx:] + '...' + name[listbox_large_name_strip_start_idx + charLenToStrip::]
    return name

def format_byte(size):
    power = 2**10  # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    size=round(size,2)
    return f'{size:>6} {power_labels[n]}'

def listBoxWindow_clicked(dir_full_path):
    canvas_data(dirs_dict, dir_full_path)

def go_up():
    global dirs_dict
    global curr_dir_path
    global root_dir_path
    if(curr_dir_path != root_dir_path):
        curr_dir_path=realpath(Path(curr_dir_path).parent)
        canvas_data(dirs_dict, curr_dir_path)


app_label = Label(topFrame, text = "Neat Directory Viewer",font=("Arial", 18), bg='white')
scan_dir_btn = Button(topFrame, text = "Scan Dir",font=("Arial", 9), bg='white', command=scan)
back_dir_btn = Button(topFrame, text = "Back",font=("Arial", 9), bg='white', command=go_up)

curr_dir_label = Label(topFrame, text = f"Current Dir: ",font=("Arial", 11), bg='white', fg="black")
dir_img = Image.open(join(Path(__file__).resolve().parent, "file-open-icon.png"))
dir_img_photo = ImageTk.PhotoImage(dir_img.resize((20, 20)))
dir_img_label = Label(topFrame, image=dir_img_photo, bg='white', cursor="hand2")
dir_img_label.bind("<Button-1>", lambda e: dir_info())

policy1_label = Label(topFrame, text = "* App ignores directories whose Windows path is more than 260 letters, in accordance with Windows API",font=("Arial", 8), bg='white')
policy1_link = Label(topFrame, text='policy.',font=('Helveticabold', 8), bg="white", fg="blue", cursor="hand2")
policy1_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab('https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation'))

app_label.place(relx=0.5, x=-100)

scan_dir_btn.place(x=10, y=30)
back_dir_btn.place(x=72, y=30)
policy1_label.place(relx=0.9, x=-35, y=37, anchor='ne')
policy1_link.place(relx=0.9, y=37, anchor='ne')

curr_dir_label.place(x=40, y=65)
dir_img_label.place(relx=1, y=65, anchor='ne')

def dir_info():
    global curr_dir_path
    print(f"curr_dir_path={curr_dir_path}")
    if(curr_dir_path!=''):
        tkinter.messagebox.showinfo("Directory full path", f"{curr_dir_path} \n[{dirs_dict[curr_dir_path].size} Byte]")
##################################################
chartCanvas = Canvas(chartFrame, width=400, height=400, bg='white', highlightthickness=0)

is_chart_clicked = False

def canvas_clear(canvas):
    canvas.delete("all")

def chart_pie_clicked(event, obj):
    global is_chart_clicked
    is_chart_clicked = True
    if(obj and obj.is_dir):
        canvas_data(dirs_dict, obj.full_path)
    # item = chartCanvas.find_closest(event.x, event.y)
    print(f"Clicked object. Co-ordinate: [{event.x}, {event.y}] , event.num: {event.num}, full_path:{obj.full_path}")


chartCanvas.pack(expand=1, side = RIGHT)

############################################################
def scroll(event):
    listBoxCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

listBoxCanvas = Canvas(listBoxFrame, bg="white", width=400, height=400, highlightthickness=0)
listBoxCanvas.pack( side = LEFT, fill = BOTH , expand = 2, pady=5)


#######################################33

tk.mainloop()