from tkinter import *
import math
import src.util.constant as const


class BarChart():
    def __init__(self, parent):
        # super().__init__(parent, )
        # self.create_widgets()
        self.parent=parent
        
    def draw(self, chartViewDetailList):
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
            chartBar = self.parent.chartCanvas.create_rectangle(bar_chart_x0, bar_chart_y0, bar_chart_x1, bar_chart_y1, fill=const.chart_colors[item.rank])  # Draw the bar
            self.parent.chartCanvas.create_text(bar_chart_x0 + 2, bar_chart_y0, anchor=SW, text=f"{str(bar_chart_item_val)}%" ) # Put the y value above the bar
            self.parent.chartCanvas.tag_bind(chartBar,"<Button-1>",lambda event,item=item : self.parent.pie_chart_clicked(event, item.objectDetail))



class PieChart():
    def __init__(self, parent):
        # super().__init__(parent, )
        # self.create_widgets()
        
        self.parent=parent

    def draw(self, chartViewDetailList):
        start_angle=0
        tot_angle=0
        for x,item in enumerate(chartViewDetailList):
            # print(f"ChartViewDetail: rank:{item.rank}, pie_angle_width:{item.pie_angle_width}, \
            #     ObjectDetail: name:{None if(item.objectDetail is None) else Path(item.objectDetail.full_path).name}, \
            #     size:{None if(item.objectDetail is None) else item.objectDetail.size}, \
            #     is_dir:{None if(item.objectDetail is None) else item.objectDetail.is_dir}, \
            #     sub_files:{None if(item.objectDetail is None) else item.objectDetail.sub_files}, \
            #     sub_dirs:{None if(item.objectDetail is None) else item.objectDetail.sub_dirs}, ")

            pie_angle_width=round((item.obj_size_fraction)*360, 3)
            tot_angle+=pie_angle_width

            if(start_angle>=359):
                continue
            elif(start_angle+pie_angle_width>359):
                pie_angle_width-=start_angle+pie_angle_width-359

            # print(f"AFTER start_angle:{start_angle}, pie_angle_width:{pie_angle_width}")

            chartPie = self.parent.chartCanvas.create_arc((35,35,360,360), activedash=(50,10), fill=const.chart_colors[item.rank], outline="white", start=start_angle, extent=pie_angle_width, tag="pie"+str(item.rank))
            self.parent.chartCanvas.tag_bind(chartPie,"<Button-1>",lambda event,item=item : self.parent.pie_chart_clicked(event, item.objectDetail))
            
            # Percentage of each Pie is Drawn as text outside each Pie.
            percentage=round((item.obj_size_fraction)*100, 2)
            if(percentage>0.00):
                txt = self.parent.chartCanvas.create_text(1, 1, text=f'{percentage}%')
                self.parent.chartCanvas.itemconfig(txt)
                _x = math.cos(math.radians(-(start_angle + pie_angle_width/2))) * 180 + 200
                _y = math.sin(math.radians(-(start_angle + pie_angle_width/2))) * 180 + 200
                self.parent.chartCanvas.coords(txt, _x, _y)
                self.parent.chartCanvas.lift(txt, chartPie) # superimpose txt on top of Pie

            start_angle+=pie_angle_width
