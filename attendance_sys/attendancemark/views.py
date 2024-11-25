from django.shortcuts import render, HttpResponse
import cv2, json, base64
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
from queue import Queue
from .models import Student, Attendance


# Create your views here.

'''Separated the process of encoding known students faces from the main recognition code as this doesnt need to be
executed everytime a new frame is sent from a frontend, which makes the program dead slow and buggy'''
def knownEncodings():
    students = Student.objects.all()
    known_students_encoding = []
    known_student_details = []
    for student in students:
        simageload = face_recognition.load_image_file(student.image.path)
        student_encoding = face_recognition.face_encodings(simageload)[0]
        known_students_encoding.append(student_encoding)
        known_student_details.append({
            "name":student.name,
            "branch":student.branch,
            "year": student.year,
            "rollnum":student.rollnum
        })

    return known_students_encoding, known_student_details

#Made this queue global as it is required in almost all the functions
#I changed it from a list to a Queue since the FIFO nature of queue comes in handy while trying to retrieve the most recent person recognized.
recognized_dude_queue = Queue()
known_students_encoding, known_student_details = knownEncodings()

def recognition():
    
    video_capture = cv2.VideoCapture(0)
    try: 
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            status = False

            for (top, right, bottom, left), i in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_students_encoding, i)
                name = "Unknown"
                if True in matches: 
                    status = True
                    match_index = matches.index(True)
                    recognized_dude = known_student_details[match_index]
                    name = recognized_dude["name"]
                    
                    if recognized_dude_queue.empty():
                        recognized_dude_queue.put(recognized_dude)
                    else:
                        recognized_dude_queue.get()
                        recognized_dude_queue.put(recognized_dude)
                #Below two lines are to draw a rectangle around the face of the person in the video feed and write their name over the box.    
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            if not status and not recognized_dude_queue.empty():
                recognized_dude_queue.get()

            _, jpeg_frame = cv2.imencode('.jpg', frame)
            frame_bytes = jpeg_frame.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally: 
        video_capture.release()

        

@csrf_exempt
def video_feed(request):
    """Stream video feed to the frontend."""
    return StreamingHttpResponse(
        recognition(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


#This function is supposed to return the details of the person who was recognized most recently. 
def get_recognized_student(request):

    if not recognized_dude_queue.empty():
        recognized_dude = recognized_dude_queue.get()
        return JsonResponse({'success': True, 'student': recognized_dude})
    return JsonResponse({'success': False, 'message': 'No face recognized yet'})


def index(request):
    return render(request, 'attendancemark/index2.html')



