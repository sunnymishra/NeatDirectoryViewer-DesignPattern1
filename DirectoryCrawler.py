import os
from os.path import join, getsize
from pathlib import Path
from re import S

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
        # Walk the diredctory tree from bottom to top fashion.
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

    