import Constant as const
from pathlib import Path

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