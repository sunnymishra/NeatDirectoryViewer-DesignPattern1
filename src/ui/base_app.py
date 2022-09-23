from tkinter import *
from os.path import join, realpath
from src.model.crawler import ObjectDetail
import src.util.constant as const
from src.ui.frames import TopFrame, ChartFrame, ListingFrame, InfoFrame


class ChartViewDetail:
    def __init__(self, rank: int, objectDetail: ObjectDetail, obj_size_fraction:float):
        self.rank=rank
        self.objectDetail=objectDetail
        self.obj_size_fraction=obj_size_fraction


class BaseApp(Tk):
    def __init__(self):
        super().__init__()

        self.geometry("800x500")
        self.title(const.app_str)
        self.resizable(0, 0)
        self['bg'] = 'white'
        
        self.state = {'dirs_dict':{}, 'chart_selected': const.barchart_str, 'curr_dir_path': '', 'root_dir_path': ''}

        self.create_widgets()


    def create_widgets(self):
        self.topFrame = TopFrame(self)
        self.topFrame.pack_propagate(0)
        self.topFrame.pack(side='top', expand='True', padx=0, pady=0)

        self.chartFrame = ChartFrame(self)
        self.chartFrame.pack_propagate(0)
        self.chartFrame.pack(fill='x', side='left', expand='True', anchor='s')

        self.listingFrame = ListingFrame(self)
        self.listingFrame.pack_propagate(0)
        self.listingFrame.pack(fill='x', side='right', expand='True', anchor='s')

        self.infoFrame = InfoFrame(self)
        

    def draw_all(self, curr_dir_str):
        print("reached draw_all()")
        self.clear_canvas()

        self.state['curr_dir_path']=curr_dir_str # Important step while walking up-down the tree
        
        curr_dir_detail = self.state['dirs_dict'][curr_dir_str]

        self.topFrame.update_dir_size(curr_dir_detail)

        if(curr_dir_detail.size==0): 
            return

        child_objects = self.get_child_obj(curr_dir_detail)
        chartPortions = self.get_chart_portions(curr_dir_detail, child_objects)

        self.chartFrame.draw_chart_dropdown(curr_dir_detail, chartPortions)
        self.chartFrame.draw_chart(chartPortions)
        self.listingFrame.draw_listbox(chartPortions, child_objects)


    def clear_canvas(self, frame=None):
        if(frame is not None):
            frame.chartCanvas.delete("all")
        else:
            self.chartFrame.chartCanvas.delete("all")
            self.listingFrame.listBoxCanvas.delete("all")


    def get_child_obj(self, curr_dir_detail):
        child_object_names = curr_dir_detail.sub_files + curr_dir_detail.sub_dirs
        child_objects = []
        for obj_name in child_object_names:
            try:
                child_objects.append(self.state['dirs_dict'][join(self.state['curr_dir_path'],obj_name)])
            except KeyError:
                print(f"In get_dir_view_data: KeyError for Path: {join(self.state['curr_dir_path'], child_object_names)}")
                pass
        # Sort child_objects in Descending order of size
        child_objects = sorted(child_objects, key=lambda obj: obj.size, reverse=True)
        return child_objects


    def get_chart_portions(self, curr_dir_detail, child_objects):
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


