


 

from reportlab.pdfgen.canvas import Canvas
import matplotlib.pyplot as plt
import matplotlib
#import cStringIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import Paragraph, Frame, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import Color, white, black, blue, red
from datetime import date
import pickle
import os.path
import numpy as np
from PyPDF2 import PdfFileMerger, PdfFileReader

global PDF_FILE
PDF_FILE = '/GPFS/XF03ID1/home/xf03id/startup/eLog_info_for_gui.obj'
#PDF_FILE = r'C:\Users\pattammattel\Desktop\Python_Codes\Qt_Learning\Ajith_Gui_06222020\eLog_info_for_gui.obj'

global DPI
DPI=300

global PDF_CTS
PDF_CTS = 1

global BOUND
BOUND = 1

class exp_info_for_gui:
    fname = 'eLog.pdf'
    date = date.today().isoformat()
    sample = ''
    experimenter = ''
    pic = ''

global G_INFO
G_INFO = exp_info_for_gui()

if os.path.isfile(PDF_FILE):
    infoFile = open(PDF_FILE,'rb')
    G_INFO = pickle.load(infoFile)

global PDF_C
PDF_C = Canvas('tmp_fig.pdf',pagesize=letter)


#matplotlib.use('Agg')


styles = getSampleStyleSheet()


class fig_info_for_gui:
    def __init__(self,title,note):
        self.title = title
        self.note = note

class TitlePage:
    def __init__(self,info,c):
        self.info = info
        self.c = c

    def create(self):
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleN.alignment = TA_CENTER
        styleH = styles['Heading1']
        styleH.alignment = TA_CENTER
        story = []
        #add some flowables
        story.append(Paragraph(self.info.date,styleH))
        story.append(Paragraph('Sample: '+self.info.sample,styleH))
        story.append(Paragraph('Experimenters: '+self.info.experimenter,styleH))
        if self.info.pic != '':
            image = Image(self.info.pic, 5*inch,5*inch)
            story.append(image)
        #c = Canvas(self.info.fname,pagesize=letter)
        f = Frame(inch, inch, 6*inch, 9*inch, showBoundary=0)
        f.addFromList(story,self.c)
        self.c.save()


class FigPage_for_gui:
    def __init__(self,c,fig,fig_info_for_gui, pos):
        self.c = c
        self.fig= fig
        self.fig_info_for_gui = fig_info_for_gui
        self.pos = pos
    def create(self):
        styleN = styles['Normal']
        styleN.alignment = TA_CENTER
        #imgdata = cStringIO.StringIO()
        self.fig.savefig('tmp_img.png',dpi=DPI,format='png')
        #imgdata.seek(0)  # rewind the data
        image = Image('tmp_img.png',3.5*inch,2.75*inch)
        story = []
        story.append(Paragraph(self.fig_info_for_gui.title,styleN))
        story.append(image)
        story.append(Paragraph(self.fig_info_for_gui.note,styleN))
        if np.mod(self.pos,2):
            col = 1
            row = (self.pos-1)/2 + 1
        else:
            col = 2
            row = self.pos/2
        f = Frame(((col-1)*4+0.15)*inch, (7.5-(row-1)*3.5)*inch, 4.*inch, 3.25*inch, showBoundary=BOUND)
        f.addFromList(story,self.c)

class PicPage_for_gui:
    def __init__(self,c,picFile,fig_info_for_gui, pos):
        self.c = c
        self.image = Image(picFile,3.5*inch,2.75*inch)
        self.fig_info_for_gui = fig_info_for_gui
        self.pos = pos
    def create(self):
        styleN = styles['Normal']
        styleN.alignment = TA_CENTER
        story = []
        story.append(Paragraph(self.fig_info_for_gui.title,styleN))
        story.append(self.image)
        story.append(Paragraph(self.fig_info_for_gui.note,styleN))
        if np.mod(self.pos,2):
            col = 1
            row = (self.pos-1)/2 + 1
        else:
            col = 2
            row = self.pos/2
        f = Frame(((col-1)*4+0.15)*inch, (7.5-(row-1)*3.5)*inch, 4.*inch, 3.25*inch, showBoundary=BOUND)
        f.addFromList(story,self.c)

class NotePage_for_gui:
    def __init__(self,c,note,pos):
        self.c = c
        self.note = note
        self.pos = pos
    def create(self):
        styleN = styles['Normal']
        styleN.alignment = TA_LEFT
        story = []
        story.append(Paragraph(self.note,styleN))
        if np.mod(self.pos,2):
            col = 1
            row = (self.pos-1)/2 + 1
        else:
            col = 2
            row = self.pos/2
        f = Frame(((col-1)*4+0.15)*inch, (7.5-(row-1)*3.5)*inch, 4.*inch, 3.25*inch, showBoundary=BOUND)
        f.addFromList(story,self.c)

class BlankPage_for_gui:
    def __init__(self,c,pos):
        self.c = c
        self.pos = pos
    def create(self):
        styleN = styles['Normal']
        styleN.alignment = TA_CENTER
        story = []
        self.c.setFillColor(white)
        story.append(self.c.rect(0,0,4.*inch,3.25*inch,fill=1))
        if np.mod(self.pos,2):
            col = 1
            row = (self.pos-1)/2 + 1
        else:
            col = 2
            row = self.pos/2
        f = Frame(((col-1)*4+0.15)*inch, (7.5-(row-1)*3.5)*inch, 4.*inch, 3.25*inch, showBoundary=BOUND)
        f.addFromList(story,self.c)


def setup_pdf_for_gui(tmp_file, tmp_date, tmp_sample, tmp_experimenter, tmp_pic):
    global G_INFO
    if os.path.isfile(PDF_FILE):
        infoFile = open(PDF_FILE,'rb')
        new_info = pickle.load(infoFile)
    else:
        new_info = exp_info_for_gui()
    #print('Create a pdf eLog file and record experiment information. Press ENTER to accept existing values.')
    #tmp_file = input('Please enter file name '+'('+new_info.fname+')'+':')
    if tmp_file != '':
        new_info.fname = tmp_file
    if os.path.isfile(new_info.fname):
        print('{} already exists.'.format(new_info.fname)+' New pages will be appended.')
    #tmp_date = input('Please enter date'+'('+new_info.date+')'+':')
    if tmp_date != '':
        new_info.date = tmp_date
    #tmp_sample = input('Please enter sample description'+'('+new_info.sample+')'+':')
    if tmp_sample != '':
        new_info.sample = tmp_sample
    #tmp_experimenter = input('Please enter experimenters'+'('+new_info.experimenter+')'+':')
    if tmp_experimenter != '':
        new_info.experimenter = tmp_experimenter
    #tmp_pic = input('Please specify the image file you want to attach. Type no if no image will be attached'+'('+new_info.pic+')'+':')
    if tmp_pic !='':
        if tmp_pic == 'no':
            new_info.pic = ''
        else:
            new_info.pic = tmp_pic
    infoFile = open(PDF_FILE,'wb')
    pickle.dump(new_info,infoFile)
    G_INFO = new_info

def insertTitle_for_gui():
    global G_INFO
    if os.path.isfile(G_INFO.fname):
        c = Canvas('tmp_title.pdf',pagesize=letter)
        tp = TitlePage(G_INFO,c)
        tp.create()
        pdf_append_for_gui(G_INFO.fname,'tmp_title.pdf')
    else:
        c = Canvas(G_INFO.fname,pagesize=letter)
        tp = TitlePage(G_INFO,c)
        tp.create()

def insertFig_for_gui(note='',title ='', *, fig=None):
    global PDF_CTS
    global PDF_C
    if title == '':
        title = scan_command(-1)
    fi = fig_info_for_gui(title,note)
    if fig is None:
        fig = plt.gcf()
    if PDF_CTS == 6:
        #print(PDF_CTS)
        fp = FigPage_for_gui(PDF_C,fig,fi,PDF_CTS)
        fp.create()
        PDF_C.save()
        PDF_CTS = 1
        if os.path.isfile(G_INFO.fname):
            pdf_append_for_gui(G_INFO.fname,'tmp_fig.pdf')
        else:
            os.rename('tmp_fig.pdf',G_INFO.fname)
    elif PDF_CTS == 1:
        #print(PDF_CTS)
        PDF_C = Canvas('tmp_fig.pdf',pagesize=letter)
        fp = FigPage_for_gui(PDF_C,fig,fi,PDF_CTS)
        fp.create()
        PDF_CTS = PDF_CTS + 1
        #print(PDF_CTS)
    else:
        #print(PDF_CTS)
        fp = FigPage_for_gui(PDF_C,fig,fi,PDF_CTS)
        fp.create()
        PDF_CTS = PDF_CTS + 1

def insertPic_for_gui(picFile,note='',title =''):
    global PDF_CTS
    global PDF_C
    fi = fig_info_for_gui(title,note)
    if PDF_CTS == 6:
        #print(PDF_CTS)
        fp = PicPage_for_gui(PDF_C,picFile,fi,PDF_CTS)
        fp.create()
        PDF_C.save()
        PDF_CTS = 1
        if os.path.isfile(G_INFO.fname):
            pdf_append_for_gui(G_INFO.fname,'tmp_fig.pdf')
        else:
            os.rename('tmp_fig.pdf',G_INFO.fname)
    elif PDF_CTS == 1:
        #print(PDF_CTS)
        PDF_C = Canvas('tmp_fig.pdf',pagesize=letter)
        fp = PicPage_for_gui(PDF_C,picFile,fi,PDF_CTS)
        fp.create()
        PDF_CTS = PDF_CTS + 1
        #print(PDF_CTS)
    else:
        #print(PDF_CTS)
        fp = PicPage_for_gui(PDF_C,picFile,fi,PDF_CTS)
        fp.create()
        PDF_CTS = PDF_CTS + 1

def insertNote_for_gui():
    global PDF_CTS
    global PDF_C
    note = input('Please enter your long note:')
    if PDF_CTS == 6:
        #print(PDF_CTS)
        fp = NotePage_for_gui(PDF_C,note,PDF_CTS)
        fp.create()
        PDF_C.save()
        PDF_CTS = 1
        if os.path.isfile(G_INFO.fname):
            pdf_append_for_gui(G_INFO.fname,'tmp_fig.pdf')
        else:
            os.rename('tmp_fig.pdf',G_INFO.fname)
    elif PDF_CTS == 1:
        #print(PDF_CTS)
        PDF_C = Canvas('tmp_fig.pdf',pagesize=letter)
        fp = NotePage_for_gui(PDF_C,note,PDF_CTS)
        fp.create()
        PDF_CTS = PDF_CTS + 1
        #print(PDF_CTS)
    else:
        #print(PDF_CTS)
        fp = NotePage_for_gui(PDF_C,note,PDF_CTS)
        fp.create()
        PDF_CTS = PDF_CTS + 1

def undo_pdf_for_gui():
    global PDF_CTS
    if PDF_CTS == 1:
        print('Page has been saved to the disk. You cannot roll back the block number and erase content.')
    else:
        PDF_CTS = PDF_CTS -1
        fp = BlankPage_for_gui(PDF_C,PDF_CTS)
        fp.create()
        print('Block number is rolled back by 1 and content in it is erased.')


def save_page_for_gui():
    global PDF_CTS
    global PDF_C
    if PDF_CTS != 1:
        PDF_C.save()
        PDF_CTS = 1
        if os.path.isfile(G_INFO.fname):
            pdf_append_for_gui(G_INFO.fname,'tmp_fig.pdf')
        else:
            os.rename('tmp_fig.pdf',G_INFO.fname)
        print('Page has been saved.')
    else:
        print('Page has been saved.')

def pdf_append_for_gui(file1,file2):
    merger = PdfFileMerger()
    merger.append(PdfFileReader(open(file1,'rb')))
    merger.append(PdfFileReader(open(file2,'rb')))
    merger.write(file1)

def output2pdf_for_gui(sid_start,sid_end,elem, mot_name=''):
    for i in range(sid_start,sid_end):
        si = scan_info(i)
        if si.status == 'success':
            #if si.plan == 'FlyPlan1D':
                #plot(i,elem,'sclr1_ch4')
                #time.sleep(1)
                #title = scan_command(i)
                #zpsth = check_baseline(i,'zpsth')
                #smarx = check_baseline(i,'smarx')
                #smary = check_baseline(i,'smary')
                #note = 'smarx={:1.3f} smary={:1.3f} zpsth={:1.3f}'.format(smarx,smary,zpsth)
                #insertFig(note, title)
                #plt.close()
            if si.plan == 'FlyPlan2D':
                plot2dfly(i,elem,'sclr1_ch4')
                #time.sleep(1)
                title = si.command
                if mot_name == '':
                    note = ''
                else:
                    mot_pos = check_baseline(i, mot_name)
                    note = mot_name+'={:1.3f}'.format(mot_pos)
                insertFig(note,title)
                plt.close()


