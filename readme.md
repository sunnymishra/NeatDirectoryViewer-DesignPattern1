App limitation:
- If User scans Directory with 100k+ sub-dir/files then it takes time. To solve this either show a Progress bar/percentage(https://stackoverflow.com/a/19332602/1316967), or add a Stop Scan button.
- Pie chart doesn't show any pie having less than 1* value out of total 360*


Pending items:
- Catch all Exception at Root level and show Oops, failure msg in bottom 2 Canvas center


Vid steps:
- Break monolith function set_dir_canvas_with_data() into smaller function "Single responsibility SOLID"
- Gibberish short names to variables,functions be changed to meaningful names. Add function comments if required.
- Move labels, string literals, repeated constant values to Constant file.
- Introduce OOPS Class concept in code completely and remove Global variables, instead use Instance variables and pass important variables around in function arguments.
- https://stackoverflow.com/q/49699802/1316967 uses `self`.rect to delete the rectangle in the callback func-> def oval_func(self,event): self.c.delete(self.rect)
- Add desired Design patterns(Chain of responsibility for Logger type, Builder, Singleton, Factory Method)


Done items:
- Fix bug in c:/winutils Graph Pie is not showing all Pies
- Testing: test "C:\opt" as 1st Scan dir after App load. YOu will notice 5 Pies in UI, but there are only 2 Pies in Log.
- Hide bottom 2 Canvas, when App loads first time.
- LineChart: Top 5 Lines(clickable) + Others Line(non clickable). If current folder only has less than 5 Lines, then show only that many Lines on screen. All Lines arranged in Descending order of folder size.
- RightFrame: 3 columns - 1.) Color coding square with folder size inside it, 2.) folder name, 3.) [folder]/[file] as metadata
- RightFrame: Back button on 1st line as 2 dots ".." . If on My Computer screen, Back button is not clickable or doesn't do anything. All rows arranged in Descending order of folder size.
- In Display "Current Directory" label, strip/crop characters if dir full length is more than 82 chars.
- In ListBox, strip/crop characters if file/dir name is more than 35 chars
- PieChart: Top 5 pie(clickable) + Others pie(non clickable). If current folder only has less than 5 Pie, then show only that many pies on screen.  All Pies arranged in Descending order of folder size.
- Add exact Bytes value in Popup view Button on right of the Root directory name label
- Add red color for biggest size directory(in Bar chart+Pie chart), then Orange, then dark green, then light green,then grey
- Add a drop down to choose Pie chart or Bar chart
- [Not accepted] Disable BACK buttom once u reach root of current scan dir, after user clicks on BACK multiple times. Cant allow user to go to C:/ Root.
- Stop reverse scroll on ListBoxWindow
- Add Pie chart Percentage label above each Pie. Just like in Bar chart.
- Bug: Pie Chart not working properly when last pie is less than 1 degree width.
	- Check Pie chart view for -> C:\DOCS\Analytics-KT\Hadoop-Training\Day-4
	- Check Pie+Bar chart view for -> C:\msys64\home\smishra5
	- Check Bar chart view for -> C:\DOCS\~~~CAB-approval-July2022-New__SME
	- Check Bar chart view for -> C:\DOCS\Personal\Personal-dev
	- Check Bar chart view for -> C:\DOCS\Analytics-KT\Hadoop-Training\Day-5