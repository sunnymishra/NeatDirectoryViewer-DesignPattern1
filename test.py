import tempfile
from os.path import join
import os
import time

tmpD=tempfile.gettempdir()
log_dir=join(tmpD, "NeatViewer_Logs")
print(log_dir)

if not os.path.exists(log_dir):
   os.makedirs(log_dir)
f_name=join(log_dir, "my1.log")
f=open(f_name, "a")
f.write("za1")
f.write("za2")
f.flush()

print('going to sleep...')
time.sleep(15)
print('now awake!')

f.write("za3")
f.write("za4")

f.close()