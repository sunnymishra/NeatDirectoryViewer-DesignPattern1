from tkinter import *
import webbrowser
import tkinter.messagebox
from PIL import Image, ImageTk
from pathlib import Path
from os.path import join, realpath
from tkinter import filedialog as fd
import DirectoryCrawler as crawler
from DirectoryCrawler import FSObjectDetail as DirectoryDetail
import math
import Constants as const


class ChartViewDetail:
    def __init__(self, rank: int, directoryDetail: DirectoryDetail, obj_size_fraction:float):
        self.rank=rank
        self.directoryDetail=directoryDetail
        self.obj_size_fraction=obj_size_fraction

tk = Tk()
tk.geometry("800x500")
tk['bg'] = 'white'
dirs_dict={}
curr_dir_path = ""
root_dir_path = ""
global_state = {'graph_selected':const.barchart}

topFrame = Frame(tk, width=800, height=100, bg='white', border=0)
topFrame.pack_propagate(0)
topFrame.pack(side='top', expand='True', padx=0, pady=0)

graphFrame = Frame(tk, bg='white', width=400, height=400, border=0)
graphFrame.pack_propagate(0)
graphFrame.pack(fill='x', side='left', expand='True', anchor='s')

listBoxFrame = Frame(tk, bg='white', width=400, height=400, border=0)
listBoxFrame.pack_propagate(0)
listBoxFrame.pack(fill='x', side='right', expand='True', anchor='s')
##################################################
def scan_dir():
    filetypes = (
        ('Text files', '*.txt'),
        ('All files', '*.*')
    )
    dirName = fd.askdirectory(
        title='Open a Directory',
        initialdir='/')
    if(dirName != ""):
        curr_dir_str=realpath(Path(dirName))
        global root_dir_path
        root_dir_path=curr_dir_str

        global dirs_dict
        dirs_dict = crawler.crawl_dir(curr_dir_str)
        
        set_dir_canvas_with_data(dirs_dict, curr_dir_str)

def set_dir_canvas_with_data(dirs_dict, curr_dir_str):
    
    canvas_clear(listBoxCanvas)
    canvas_clear(graphCanvas)

    global curr_dir_path
    curr_dir_path=curr_dir_str # Important step while walking up-down the tree

    curr_dir_detail = dirs_dict[curr_dir_path]

    curr_dir_size = format_bytes(curr_dir_detail.size)
    print(f"Curr_dir_path:{curr_dir_path} curr_dir_size:{curr_dir_size}")
    curr_dir_label['text'] = 'Current Dir: '+ format_obj_name(curr_dir_detail, True) + f' [{curr_dir_size}]' #curr_dir_path

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

        chartViewDetailList.append(ChartViewDetail(i, obj, (obj.size/curr_dir_detail.size)))  # round((obj.size/curr_dir_detail.size)*360, 3)
        totalTopObjSize+=obj.size
    chartViewDetailList.append(ChartViewDetail(6, DirectoryDetail('OTHERS', None, None, None, None), ((curr_dir_detail.size - totalTopObjSize)/curr_dir_detail.size)))  # round(((curr_dir_detail.size - totalTopObjSize)/curr_dir_detail.size)*360, 3)

    graph_dropdown_opt = [const.barchart, const.piechart]
    graph_dropdown_val = StringVar(graphCanvas)
    graph_dropdown_val.set(global_state['graph_selected']) #selected value in dropdown
    graph_dropdown = OptionMenu(graphCanvas, graph_dropdown_val, *graph_dropdown_opt, command = lambda selected_val=graph_dropdown_val.get(), curr_dir_obj=curr_dir_detail, data=chartViewDetailList : dropdown_changed(selected_val, data))
    graph_dropdown.config(bg="white",border=2,relief="raised")
    graph_dropdown["menu"].config(bg="white")
    graph_dropdown.place(x=10, y=10)

    draw_graph(chartViewDetailList)

    
################################
    # Updating the ListBoxes
    yHeight = 0
    counter=0

    for obj in child_objects:
        # Creating new ListBoxes for the current Scan Dir result
        labelFrame = LabelFrame(listBoxCanvas, border=0)
        labelFrame.grid(column=0, row=0, padx=2, pady=2)
        label1 = Label(labelFrame,text=format_bytes(obj.size), font=("Courier", 9), compound=RIGHT, bg="#AAAAAA", bd=0)
        label2 = Label(labelFrame,text=format_obj_name(obj), font=("Courier", 9), compound=RIGHT, bg="white")
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
        listBoxCanvas.bind_all("<MouseWheel>", _on_mousewheel)

    print(f"yHeight:{yHeight}, listBoxCanvas.winfo_height:{listBoxCanvas.winfo_height()}")

def dropdown_changed(dropdown_val, data):
    global_state['graph_selected']=dropdown_val
    draw_graph(data)

def draw_graph(data):
    canvas_clear(graphCanvas)

    global curr_dir_path
    curr_dir_detail = dirs_dict[curr_dir_path]
    if(curr_dir_detail.size==0): 
        return

    if(global_state['graph_selected']==const.barchart):
        draw_barchart(data)
    elif(global_state['graph_selected']==const.piechart):
        draw_piechart(data)
    else:
        pass
    
def draw_barchart(chartViewDetailList):
    # The variables below size the bar graph
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
        graphBar = graphCanvas.create_rectangle(bar_chart_x0, bar_chart_y0, bar_chart_x1, bar_chart_y1, fill=const.chart_colors[item.rank])  # Draw the bar
        graphCanvas.create_text(bar_chart_x0 + 2, bar_chart_y0, anchor=SW, text=f"{str(bar_chart_item_val)}%" ) # Put the y value above the bar
        graphCanvas.tag_bind(graphBar,"<Button-1>",lambda event,item=item : graph_pie_clicked(event, item.directoryDetail))

def draw_piechart(chartViewDetailList):
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
        # canvasItem = graphCanvas.find_withtag("pie"+str(item.rank))

        pie_angle_width=round((item.obj_size_fraction)*360, 3)
        tot_angle+=pie_angle_width  #tot_angle+=item.pie_angle_width

        print(f"BEFORE start_angle:{start_angle}, pie_angle_width:{pie_angle_width}")

        if(start_angle>=359):
            continue
        elif(start_angle+pie_angle_width>359):
            pie_angle_width-=start_angle+pie_angle_width-359

        # if(tot_angle>359.9):
        #     # print(f"tot_angle:{tot_angle}, pie_angle_width_before:{item.pie_angle_width}, pie_angle_width_after:{item.pie_angle_width-(tot_angle-359.99)}")
        #     pie_angle_width-=(tot_angle-359.9) # item.pie_angle_width-=(tot_angle-359.9)
        #     tot_angle=359.9
        # else:
        #     # print(f"tot_angle:{tot_angle}, pie_angle_width:{item.pie_angle_width}")
        #     pass
        print(f"AFTER start_angle:{start_angle}, pie_angle_width:{pie_angle_width}")

        graphPie = graphCanvas.create_arc((35,35,360,360), activedash=(50,10), fill=const.chart_colors[item.rank], outline="white", start=start_angle, extent=pie_angle_width, tag="pie"+str(item.rank))
        graphCanvas.tag_bind(graphPie,"<Button-1>",lambda event,item=item : graph_pie_clicked(event, item.directoryDetail))
        
        # Percentage of each Pie is Drawn as text outside each Pie.
        percentage=round((item.obj_size_fraction)*100, 2)
        if(percentage>0.00):
            txt = graphCanvas.create_text(1, 1, text=f'{percentage}%')
            graphCanvas.itemconfig(txt)
            _x = math.cos(math.radians(-(start_angle + pie_angle_width/2))) * 180 + 200
            _y = math.sin(math.radians(-(start_angle + pie_angle_width/2))) * 180 + 200
            graphCanvas.coords(txt, _x, _y)
            graphCanvas.lift(txt, graphPie) # superimpose txt on top of Pie

        start_angle+=pie_angle_width  # start_angle+=item.pie_angle_width

def format_obj_name(obj, is_top_display=False):
    max_name_len=const.listbox_max_name_len if(obj.is_dir) else const.listbox_max_name_len+len(const.dir_label)+1
    if(is_top_display):
        max_name_len=const.topdisplay_max_name_len
    name=obj.full_path if is_top_display else Path(obj.full_path).name
    if(len(name)>max_name_len):
        charLenToStrip=len(name)-max_name_len+3  # Here 3 is for the 3 dots ... to be displayed in cropped final String.
        listbox_large_name_strip_start_idx=int(max_name_len/2)
        name = name[0: listbox_large_name_strip_start_idx:] + '...' + name[listbox_large_name_strip_start_idx + charLenToStrip::]
    return name

def format_bytes(size):
    power = 2**10  # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    size=round(size,2)
    return f'{size:>6} {power_labels[n]}'

def listBoxWindow_clicked(dir_full_path):
    set_dir_canvas_with_data(dirs_dict, dir_full_path)

def display_parent_dir():
    global dirs_dict
    global curr_dir_path
    global root_dir_path
    if(curr_dir_path != root_dir_path):
        curr_dir_path=realpath(Path(curr_dir_path).parent)
        set_dir_canvas_with_data(dirs_dict, curr_dir_path)


app_label = Label(topFrame, text = "Neat Directory Viewer",font=("Arial", 18), bg='white')
scan_dir_btn = Button(topFrame, text = "Scan Dir",font=("Arial", 9), bg='white', command=scan_dir)
back_dir_btn = Button(topFrame, text = "Back",font=("Arial", 9), bg='white', command=display_parent_dir)

curr_dir_label = Label(topFrame, text = f"Current Dir: ",font=("Arial", 11), bg='white', fg="black")
dir_img = Image.open(join(Path(__file__).resolve().parent, "Untitled.png"))
dir_img_photo = ImageTk.PhotoImage(dir_img)
dir_img_label = Label(topFrame, image=dir_img_photo, bg='white', cursor="hand2")
dir_img_label.bind("<Button-1>", lambda e: tkinter.messagebox.showinfo("Directory full path", f"{curr_dir_path} \n[{dirs_dict[curr_dir_path].size} Byte]"))

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


##################################################
graphCanvas = Canvas(graphFrame, width=400, height=400, bg='white', highlightthickness=0)

is_graph_clicked = False

def canvas_clear(canvas):
    canvas.delete("all")

def graph_canvas_clicked(event):
    global is_graph_clicked
    if is_graph_clicked == False:
        print(f'Clicked canvas. Co-ordinate: [{event.x}, {event.y}], event.widget: {event.widget}')
    is_graph_clicked = False

def graph_pie_clicked(event, obj):
    global is_graph_clicked
    is_graph_clicked = True
    if(obj and obj.is_dir):
        set_dir_canvas_with_data(dirs_dict, obj.full_path)
    # item = graphCanvas.find_closest(event.x, event.y)
    print(f"Clicked object. Co-ordinate: [{event.x}, {event.y}] , event.num: {event.num}, full_path:{obj.full_path}")
    # graphCanvas.itemconfigure(item, fill="blue")

graphCanvas.bind('<Button-1>', graph_canvas_clicked)

graphCanvas.pack(expand=1, side = RIGHT)

############################################################
def _on_mousewheel(event):
    listBoxCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

listBoxCanvas = Canvas(listBoxFrame, bg="white", width=400, height=400, highlightthickness=0)
listBoxCanvas.pack( side = LEFT, fill = BOTH , expand = 2, pady=5)


#######################################33

tk.mainloop()