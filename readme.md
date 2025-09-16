This project is a Windows Directory viewer tool written in Python. 
For non-technical person, do following:
- You don't need Python software to be installed in your machine
- Download the following file from the Git project -> "dist/NeatDirectoryViewer.exe"
- Run this EXE file. That itself should ideally launch the program if there are no Windows environment dependency challenges faced. If you are however a Software developer, you can go through the main.py file in the root folder and the rest of the code inside SRC folder to understand. 

For technical person, do following:
- cd <root directory after downloading code from GIt>
- pip install -r requirements.txt
- python main.py
Above commands should launch the software.

App limitation:
- Currently when you search for any Windows directory multiple times, after sometime when you try to close the Window clicking on the Cross button on top right, it hangs the software for few seconds. This is a known issue and needs to be fixed in software.
- For some Windows folders the Scan Dir actually fails permanently. You might then need to stop this software and re-launch it again. This is a known issue and needs to be fixed in software.
- Directory or sub-directory with Path longer than 260 characters will be ignored by the App in size calculation, [Windows API](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation)
- Large Directory scan takes time and UI screen freezes. Currently there is no 'Progress bar' or a 'Stop Scan' button feature.
- Pie chart doesn't show any pie having less than 1* value out of total 360*

For software engineers who want to add new features or fix bugs in this codebase:
- Once code is modiied locally, you can use PyInstaller to bundle entire project into Windows Exe file:

$ pyinstaller --onefile --windowed --paths=src --add-data "src/asset/file-open-icon.png;asset" --name "NeatDirectoryViewer" main.py
OR
$ pyinstaller NeatDirectoryViewer.spec