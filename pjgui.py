from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter import ttk
import numpy as np
import cv2 as cv
from moviepy.editor import VideoFileClip
import os
from natsort import natsorted
import re
import numpy as np
import argparse
import glob
from moviepy.editor import concatenate_videoclips
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import time
import shutil
from datetime import datetime

import pathlib  
st=pathlib.Path().absolute()
pth=(st.as_posix())

data=[]
hist=[]
video_path=""
folder_selected=""

top = Tk()
top.state('zoomed')
top.title("Video Summary")
top.config(bg='#ff6666')
lb1=Label(top,text="Video Summarizing Tool",fg='red',font=("calibri Bold",25),padx=30,pady=30,bg='#dfff80')
lb1.grid(row=0,column=1)
ttk.Separator(top, orient=HORIZONTAL).grid(column=0, row=1, columnspan=200, sticky=W+E,padx=10,pady=10)

def videotoframes(video_path): #converts selected video to frames
    vidcap = cv.VideoCapture(video_path)
    def getFrame(sec):
        vidcap.set(cv.CAP_PROP_POS_MSEC,sec*1000)
        hasFrames,image = vidcap.read()
        if hasFrames:
            cv.imwrite(str(count)+".jpg", image)
        return hasFrames


    sec = 0
    frameRate = 1
    count=1

    clip = VideoFileClip(video_path)
    success = getFrame(sec)
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success = getFrame(sec)
        if count>=round(clip.duration/frameRate):
            break

def applytechnique():
    conflb=Label(top,text="Technique choosed is :"+str(var.get()),font=("Arial Bold", 12))
    conflb.grid(row=7,column=1,padx=10,pady=10)
    
    if var.get()=="Equalized":
        #########################################################
        filenames = glob.glob(pth+"/*.jpg")
        filenames.sort(key=lambda f: int(re.sub('\D', '', f)))

        
        for img in filenames:
            data.append(cv.imread(img))

        if not os.path.exists('equ'):
            os.makedirs('equ')
            
        for i in range(len(data)):
            img_to_yuv = cv.cvtColor(data[i],cv.COLOR_BGR2YUV)
            img_to_yuv[:,:,0] = cv.equalizeHist(img_to_yuv[:,:,0])
            hist_equalization_result = cv.cvtColor(img_to_yuv, cv.COLOR_YUV2BGR)
            cv.imwrite(pth+'/equ/eq{}.jpg'.format(i),hist_equalization_result)
            #above enter path of this python file

        """filenames1 = glob.glob("C:/Users/sagar/onedrive/Desktop/gui/equ/*.jpg")
        filenames1.sort(key=lambda f: int(re.sub('\D', '', f)))
        for img in filenames1:
            #cv.imread(img)
            data.append(cv.imread(img))"""
        
    else:
        pass
    #########################################################
    filenames = glob.glob(pth+"\\*.jpg")
    filenames.sort(key=lambda f: int(re.sub('\D', '', f)))
        
    for img in filenames:
        data.append(cv.imread(img))
        
        
    hsv=[]
    for i in range(len(data)):
        hsvimage = cv.cvtColor(data[i], cv.COLOR_BGR2HSV)
        hsv.append(hsvimage)

    h_bins = 50
    s_bins = 60
    histSize = [h_bins, s_bins]

    h_ranges = [0, 180]
    s_ranges = [0, 256]
    ranges = h_ranges + s_ranges 

    channels = [0, 1]


    for i in range(len(hsv)):
        temp = cv.calcHist([hsv[i]], channels, None, histSize, ranges, accumulate=False)
        cv.normalize(temp, temp, alpha=0, beta=1, norm_type=cv.NORM_MINMAX)
        hist.append(temp)


def computedistandsumm():
    global video_path
    global folder_selected
    met=-1
    distconf=Label(top,text="Distance method choosed is :"+str(dist.get()),font=("Arial Bold", 12))
    distconf.grid(row=11,column=1,padx=10,pady=10)
    if dist.get()=="Correlation":

        met=0
    elif dist.get()=="Chi-Square":
        met=1
    elif dist.get()=="Intersection":
        met=2
    elif dist.get()=="Bhattacharyya":
        met=3
    key=[]
    i=0
    s=0
    ct=1
    compval=[]
    while i<len(hist)-1:
        compval.append(cv.compareHist(hist[i],hist[i+1], met))
        i+=1
    for q in compval:
        s+=q
    thr=s/(len(compval))
    i=0
    if not os.path.exists('key'):
        os.makedirs('key')
    if not os.path.exists('cuts'):
        os.makedirs('cuts')
    while i<len(hist)-1:
        hist_value = cv.compareHist(hist[i],hist[i+1], met)
        if hist_value>thr:
            #######################################################################################
            cv.imwrite(pth+"\\key\\Key"+str(ct)+".jpg",data[i+1])
            clip = VideoFileClip(video_path).subclip(i, i+1)
            clip.to_videofile(pth+"\\cuts\\cut{}.mp4".format(ct), codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
            clip.close()
            ct+=1
        i+=1
    L =[]
    ###########################################################################################
    for root, dirs, files in os.walk(pth+"\\cuts"):
        files = natsorted(files)
        for file in files:
            if os.path.splitext(file)[1] == '.mp4':
                filePath = os.path.join(root, file)
                video = VideoFileClip(filePath)
                L.append(video)

    
    final_clip = concatenate_videoclips(L)
    final_clip.to_videofile("output.mp4", fps=24, remove_temp=True)
    b=(os.path.getsize(video_path))/(1024*1024)
    b1=(os.path.getsize("output.mp4"))/(1024*1024)
    orsize=Label(top,text="Size of Original Video(MB) : "+str(b),font=("Arial Bold",12))
    susize=Label(top,text="Size of Summarized Video(MB) : "+str(b1),font=("Arial Bold",12))
    clip = VideoFileClip(video_path)
    ###################################################################
    sumpath=pth+"\\output.mp4"
    clip2=VideoFileClip(sumpath)
    orle=Label(top, text="Length of Original video(sec) : "+str(clip.duration),font=("Arial Bold",12))
    sumle=Label(top, text="Length of Summarized video(sec) : "+str(clip2.duration),font=("Arial Bold",12))
    perc=Label(top, text="Original video is reduced by "+str(round(100-(clip2.duration/clip.duration)*100))+"% in length",font=("Arial Bold",12))
    orle.grid(row=12,column=1,padx=10,pady=10)
    sumle.grid(row=12,column=2,padx=10,pady=10)
    perc.grid(row=13,column=1,padx=10,pady=10)
    orsize.grid(row=13,column=2,padx=10,pady=10)
    susize.grid(row=14,column=1,padx=10,pady=10)
    persize=Label(top,text="Original Video is reduced by "+str(round(100-((b1/b)*100)))+"% in size",font=("Arial Bold",12))
    persize.grid(row=14,column=2,padx=10,pady=10)
    lastlabel=Label(top,text="Video Generated",font=("Arial Bold",12),bg="#00e600")
    lastlabel.grid(row=15,column=1,padx=10,pady=10)
    clip2.close()

    #########################################################################
    dto= datetime.now()
    fname=str(dto).replace(":","_")
    os.rename("output.mp4",fname+".mp4")
    shutil.move(pth+"\\"+fname+".mp4", folder_selected)

    #deletes files that were created except original video
    for file in os.scandir(pth+"/"):
        if file.name.endswith(".jpg"):
            os.unlink(file.path)

    for file in os.scandir(pth+"/cuts/"):
        if file.name.endswith(".mp4"):
            os.unlink(file.path)

    for file in os.scandir(pth+"/key"):
        if file.name.endswith(".jpg"):
            os.unlink(file.path)

    for file in os.scandir(pth+"/equ"):
        if file.name.endswith(".jpg"):
            os.unlink(file.path)


 
def selectvideo():
    global video_path
    ########################################################################
    video_path = askopenfilename(initialdir=pth,
                           filetypes =(("Video File", "*.wmv"),("Video File", "*.mp4"),("Video File","*.avi"),("Video File", "*.flv"),("All Files","*.*")),
                           title = "Choose a video.")
    lb2 = Label(top, text="Video : "+video_path, font=("Arial Bold", 12))
    lb2.grid(row=3,column=1,padx=10,pady=10)

def askoutpath():
    global folder_selected
    folder_selected= filedialog.askdirectory()
    olb2 = Label(top, text="Output path : "+folder_selected, font=("Arial Bold", 12))
    olb2.grid(row=3,column=2,padx=10,pady=10)
    videotoframes(video_path)


B = Button(top, text = "Select a Video", command = selectvideo)
C=Button(top,text="Select Output path",command=askoutpath)
B.grid(row=2,column=1, padx=10,pady=10)
C.grid(row=2,column=2,padx=10,pady=10)
ttk.Separator(top, orient=HORIZONTAL).grid(column=0, row=4, columnspan=200, sticky=W+E,padx=10,pady=10)
lb3 = Label(top, text="Choose a Technique ", font=("Arial Bold", 12))
lb3.grid(row=5,column=1,padx=10,pady=10)
var = StringVar()
techcomb=ttk.Combobox(top,value=["Non-Equalized"],textvariable=var,state='normal')
techcomb.grid(row=6,column=1,padx=10,pady=10)
techbtn=Button(top,text="Confirm this technique",command=applytechnique)
techbtn.grid(row=6,column=2,padx=10,pady=10)

var1=StringVar()
labelTop = Label(top,text = "Choose distance method",font=("Arial Bold", 12))
labelTop.grid(column=1, row=9,padx=10,pady=10)
dist=StringVar()
comboExample = ttk.Combobox(top, values=["Correlation","Chi-Square","Intersection","Bhattacharyya"],textvariable=dist,state='normal')
comboExample.grid(column=1, row=10,padx=10,pady=10)
distbtn=Button(top,text="Confirm this distance method",command=computedistandsumm)
distbtn.grid(row=10,column=2,padx=10,pady=10)
ttk.Separator(top, orient=HORIZONTAL).grid(column=0, row=8, columnspan=5, sticky=E+W,padx=10,pady=10)


top.mainloop()



