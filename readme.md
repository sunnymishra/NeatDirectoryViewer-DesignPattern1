App limitation:
- Directory or sub-directory with Path longer than 260 characters will be ignored by the App in size calculation, [Windows API](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation)
- Large Directory scan takes time and UI freezes. Currently there is no 'Progress bar' or a 'Stop Scan' button feature.
- Pie chart doesn't show any pie having less than 1* value out of total 360*

Use PyInstaller to bundle entire project into Windows Exe file:

$ pyinstaller --onefile --windowed --paths=src --add-data "src/asset/file-open-icon.png;asset" --name "NeatDirectoryViewer" main.py