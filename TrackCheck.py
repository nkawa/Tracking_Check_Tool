import cv2

from tkinter import *
from PIL import Image, ImageTk, ImageOps  # 画像データ用
import sys
import tkinter as tk
from tkinter import filedialog
import glob
import pandas as pd
from pathlib import Path
import json


def ts2sec(tstr):
    h = int(tstr[:-6])
    m = int(tstr[-5:-3])
    s = int(tstr[-2:])
    return h*3600+m*60+s
def sec2ts(sec):
    s = sec%60
    m = int(sec/60)%60
    h = int(sec/3600)
    return "{:02d}{:02d}{:02d}".format(h,m,s)

def sec2ts2(sec):
    s = sec%60
    m = int(sec/60)%60
    h = int(sec/3600)
    return "{:02d}:{:02d}:{:02d}".format(h,m,s)

# 時刻の先頭に 0　を追加するだけ。
def add_recog_0(x):
    return ("0"+x)[-8:]

def read_timestamp(fname):
    df = pd.read_csv(fname, usecols=[0,1,2,3,4])
    df['recog']=df['recog'].map(add_recog_0)
    df['sec']= df['recog'].map(ts2sec)
    return df

def check_timestamp(df):
    ldiff = df['sec'][0]
    error_index = []
    for i,row in df.iterrows():
        diff = row['sec']
        if ldiff +1 != diff and ldiff !=diff:
            print(i,"vid",row['vid_idx'],"frm",row['frm_idx'],lstr,ldiff,row['recog'],diff)
            error_index.append(i)
        lstr = row['recog']
        ldiff = diff

    return error_index


class App(tk.Frame):
    def __init__(self,master = None):
        super().__init__(master)

        self.button_frame = tk.Frame(self.master)
        self.log_frame = tk.Frame(self.master)

        self.csv_file = tk.Label(self.button_frame, text = "TrackJSON: Not set")
        self.csv_file.pack(expand = True, padx=10, pady=10)

        self.csv_button = tk.Button(self.button_frame, text="Open JSON", command=self.openJSON, width=40)
        self.csv_button.pack(expand = True, fill = tk.X, padx=10, pady=10)

        self.frame_num = tk.Label(self.button_frame,text="")
        self.frame_num.pack(expand=True, fill= tk.X, padx = 10, pady = 10)

        self.go_button = tk.Button(self.button_frame, text="同じフレームに同じ番号があるか確認", command=self.check_same_id_in_same_frame, width=40)
        self.go_button.pack(expand = True, fill = tk.X, padx=10, pady=10)


        self.log_text = tk.Text(self.log_frame, width=40, height=40)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        self.scrollY = tk.Scrollbar(self.log_frame,orient=tk.VERTICAL, command=self.log_text.yview)
        self.scrollY.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text["yscrollcommand"] = self.scrollY.set

        self.button_frame.grid(column=1, row=1)
        self.log_frame.grid(column=0, row=1)

        self.master.grid_rowconfigure(0, weight=2)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=2)
        self.master.grid_columnconfigure(1, weight=1)


    def openJSON(self):
        path = filedialog.askopenfilename(defaultextension=".json",filetypes=[("JSON","*.json")],title="Open JSON file")
        print(path)
#        self.csv_file["text"]="JSON:"+path
        self.csv_file["text"]="JSON:loaded"
        if len(path)>0:
            with open(path, 'r') as file:
                self.workers = json.load(file)
                print(len(self.workers))


    def check_same_id_in_same_frame(self):
        for frame in self.workers:
            tid = []
            eid = []
            for track in frame['tracks']:
                if track['track_id'] in tid:
                    if track['track_id'] not in eid:
                        eid.append(track['track_id'])
                        print("frame",frame['frame_id'],"  track_id",track['track_id'], "duplicated")
                        self.log_text.insert(tk.END, "frame:"+str(frame['frame_id'])+"  track_id:"+str(track['track_id'])+" duplicated\n")
                else:                    
                    tid.append(track['track_id'])

    
if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()
