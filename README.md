# Attendance Marking System Using Face Recognition

## Software Requirements:

- python <br>
- opencv-python <br>
- cmake<br>
- dlib <br>
- face-recognition <br>
- django <br>
- visual studio code, or a similar text editor <br>

## First update, date: unknown

After completing the set up for this project, aa basic frontend page was created. The code for this page is still present in index.html.
  
## Second update, date: 

A stand alone python file, face rec.py was created to get the basic working of the face recognition system and get an output in the server side. 

## Third Update, date: 24-11-2024

Added few more dummy students to the student database, and integrated the face recognition system with the frontend, however there are some changes that are to be made to the frontend as the div components are not nicely aligned, and some adjustments has to be made to the code in views.py to fix some bugs, such as the recognized_dude list not updating when a new student shows up on the screen. It would also be nice to make some adjustments such that the website doesn't take forever to load. 