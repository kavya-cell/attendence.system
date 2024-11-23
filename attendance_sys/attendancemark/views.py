from django.shortcuts import render, HttpResponse
import cv2, json, base64
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
from .models import Student, Attendance


# Create your views here.

#Made this list global as it is required in almost all the functions
recognized_dude = []

def recognition():
    global recognized_dude 
    
    students = Student.objects.all()
    known_students_encoding = []
    known_student_details = []
    #Loop to encode students faces from the database and store it in the list as the encoding is not available in the database.
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
    
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for (top, right, bottom, left), i in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_students_encoding, i)
            name = "Unknown"
            if True in matches: 
                match_index = matches.index(True)
                recognized_dude = known_student_details[match_index]
                name = recognized_dude["name"]
            #Below two lines are to draw a rectangle around the face of the person in the video feed and write their name over the box.    
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        _, jpeg_frame = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg_frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
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
    global recognized_dude
    if recognized_dude:
        return JsonResponse({'success': True, 'student': recognized_dude})
    return JsonResponse({'success': False, 'message': 'No face recognized yet'})


def index(request):
    return render(request, 'attendancemark/index2.html')



