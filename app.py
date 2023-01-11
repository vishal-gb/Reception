from flask import Flask, render_template, Response, request,jsonify
from flask import redirect,url_for
import cv2
import datetime, time
import os, sys
from fpdf import FPDF 
import pandas as pd 
import numpy as np
from threading import Thread
import pandas as pd
import os


global capture,rec_frame, grey, switch, neg, face, rec, out 
capture=0
grey=0
neg=0
face=0
switch=1
rec=0


PORT = os.environ["PY_PORT"]

PATH = os.environ["PATH"]

PATHS = os.environ["PATHS"]


#instatiate flask app  
app = Flask(__name__, template_folder='./templates')


# camera = cv2.VideoCapture(-1)


@app.route('/webcam')

def index():
    global camera
    camera = cv2.VideoCapture(0)
    return render_template('index.html')

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)


def gen_frames():  # generate frame by frame from camera
    global out, capture,rec_frame
    while True:
        global frame
        success, frame = camera.read() 
        if success:

            if(capture):
                capture=0
                global now 
                now = datetime.datetime.now()
                p = os.path.sep.join(['/home/snekha/hackathons/Reception_SJCE/Reception_website/Final_website/static/shot','new.jpg'])
                global frames
                frames=frame
             
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass

    
    
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=['POST','GET'])
def tasks():
    
    global camera
    if request.method == 'POST':
      
        if request.form.get('click') == 'Capture':
            global capture
            capture=1
        
        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                global now
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                # out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                out = cv2.VideoWriter('new.jpg', fourcc, 20.0, (640, 480))
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
                      

       
                          
                 
    elif request.method=='GET':
        return render_template('index.html')
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
def home():

    camera.release()
    cv2.destroyAllWindows()   
    if request.method == 'POST':
        data= request.form
        print(data)
        # print(data1)
        dfs = []
        dfs.append(pd.DataFrame([data]))
        
   
        df = pd.concat(dfs, ignore_index=True, sort=False)
        df["Pic_loc"]=PATHS
        df["Pdf_loc"]="../static/shot/"
        # df.drop(['userName'], 
        #     axis = 1, inplace = True)
        df.to_csv('input.csv',index=False)

        df2 = pd.read_csv('input.csv', header=None)
        df2=df2.transpose()
        dfa=df2.iloc[:,-1:]
        dfa=dfa.transpose()
        dfa.to_csv('add.csv', mode='a', index=False, header=False)
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.set_margins(0, 0, 0)
        
        # pdf.set_font("Arial", size = 15) 
        
        # create a cell 
        # pdf.cell(w = 40, h = 10,  "St.Joseph's College of Engineering" , border = 0, ln = 1, align = '', fill = False, link = '')
        # pdf.cell(w = 40, h = 10,  "Name"+":    "+df[-1][1] , border = 0, ln = 1, align = '', fill = False, link = '')
        # pdf.cell(100, 20, "St.Joseph's College of Engineering", 0, 1, 'C')
        pdf.set_font('Arial', '', 13)
        pdf.ln(2)
        df = pd.read_csv("input.csv")
        clg = df.iloc[-1,0]
        pdf.cell(85, 15,clg , 1,1,'C')
        # pdf.ln(2)
        name="Name"+": "+df.iloc[-1,1]+"    Reason"+": "+df.iloc[-1,8]
        pdf.cell(90, 15,name , 0,1,'C')
        
        #pdf.ln(1)
        # name="Reason"+": "+df.iloc[-1,8]
        # pdf.cell(90, 15,name , 0,1,'C')
        # #pdf.ln(1)
        
        #pdf.ln(1)
        name="Dept"+": "+df.iloc[-1,9]
        pdf.cell(90, 15,name , 0,1,'C')

        #pdf.ln(1)
        name="Meeting:"+" "+df.iloc[-1,10]
        pdf.cell(90, 15,name , 0,1,'C')
        name="Number of people"+": "+str(df.iloc[-1,11])
        pdf.cell(90, 15,name , 0,1,'C')
        #pdf.ln(1)
        name="Timestamp"+": "+str(now)
        pdf.cell(90, 15,name , 0,1,'C')
        pdf.cell(150, 15,' Signature of the staff                                Department Seal' , 0,1,'C')
        #pdf.ln(1)
        
        global pdf_loc
        pdf_loc=str(df.iloc[-1,13])
        global n
        n=str(df.iloc[-1,7])
        p = os.path.sep.join([PATH,n+'.jpg'])
        cv2.imwrite(p, frames)
        img=str(df.iloc[-1,12])
        pdf.image(img+"/static/shot/"+n+".jpg", x = 95, y = 55, w = 40, h = 0, type = '', link = '')
        # TEXTFILE = open("input.csv", "w")
        # TEXTFILE.truncate()
        pdf.output(PATH+n+".pdf")
        return redirect(url_for('pdfview'))
        # return render_template('result.html')

    return render_template('Reception.html')


@app.route('/pdfview', methods=['GET', 'POST'])
def pdfview():
    # df = pd.read_csv("input.csv")
      pdf_locs=pdf_loc+n+".pdf"
      
    # pdf_loc=str(df.iloc[-1,13])
    # pdfs=pdf_loc
      return render_template('pdfview.html',pdf_locs=pdf_locs)

@app.route('/success', methods=['GET', 'POST'])
def success():
     os.remove(PATH+n+".pdf")
     os.remove(PATH+n+".jpg")
     return render_template("success.html")

@app.route('/', methods=['GET', 'POST'])
def landing_page():
     
     return render_template("start.html")

if __name__ == '__main__':
     app.run(host="0.0.0.0",port=PORT)
    
camera.release()
cv2.destroyAllWindows()      
   