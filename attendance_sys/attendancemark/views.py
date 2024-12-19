import threading
import cv2
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
import numpy as np
import base64
from .models import Student, Attendance
from queue import Queue
from django.utils.timezone import now, timedelta
import keras
from django.db.models import Count

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

mask_model = keras.models.load_model("C:/Users/Navan/Desktop/attendence.system/attendance_sys/mask_detection/masks.h5")

# Preload known encodings
def knownEncodings():
    students = Student.objects.all()
    known_students_encoding = []
    known_student_details = []
    for student in students:
        simageload = face_recognition.load_image_file(student.image.path)
        student_encoding = face_recognition.face_encodings(simageload)[0]
        known_students_encoding.append(student_encoding)
        known_student_details.append({
            "name": student.name,
            "branch": student.branch,
            "year": student.year,
            "rollnum": student.rollnum
        })
    return known_students_encoding, known_student_details


recognized_dude_queue = Queue()
known_students_encoding, known_student_details = knownEncodings()


@csrf_exempt
def recognize_face(request):
    if request.method == "POST":
        data = request.POST.get("frame")
        if not data:
            return JsonResponse({"success": False, "message": "No frame data received"})

        try:
            frame_data = base64.b64decode(data.split(",")[1])
            np_arr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            roi_status=0
            for (x, y, w, h) in faces:
                gray_frame = gray_frame[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                det_face = face_cascade.detectMultiScale(gray_frame)
                if len(faces) == 0:
                    return JsonResponse({"success": False, "message": "No faces detected"})
                else:
                    for (ex, ey, ew, eh) in det_face:
                        face_roi = roi_color[ey:ey+eh, ex:ex+ew]
                        roi_status = 1
            final_flag = 0
            if roi_status== 1:
                final = cv2.resize(face_roi, (224, 224))
                final = np.expand_dims(final, axis = 0)
                final = final/255.0
                final_flag = 1

            if final_flag ==1:
                predictions = mask_model.predict(final)
                if predictions[0][0] < 0.5:
                    return JsonResponse({
                        "success":False,
                        "message": "Please Remove your mask"
                    })
                else:
                    face_encoding = face_encodings[0]
                    matches = face_recognition.compare_faces(known_students_encoding, face_encoding, tolerance=0.45)

                    if True in matches:
                        match_index = matches.index(True)
                        recognized_dude = known_student_details[match_index]
                        recognized_dude_queue.put(recognized_dude)
                        attendance_status = Mark_Att({"success": True, "student": recognized_dude})
                        return JsonResponse({
                            "success": True,
                            "student": recognized_dude,
                            "attendance_status": attendance_status,
                            "message": attendance_status.get("message", "")
                        })
                    
            return JsonResponse({"success": False, "message": "No matching face found"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})


def Mark_Att(response):
    if response["success"] == True:
        dude = response["student"]
        try:
            student = Student.objects.get(name=dude["name"])  # Fetch the Student instance
        except Student.DoesNotExist:
            return {"success": False, "message": "Student not found"}

        # Check for recent attendance within 30 seconds
        thirty_seconds_ago = now() - timedelta(seconds=60)
        recent_attendance = Attendance.objects.filter(
            rollnum=student,  # Use the Student instance here
            date__gte=thirty_seconds_ago,
            status=True
        )

        if recent_attendance.exists():
            return {"success": True, "message": "Attendance already marked"}
        else:
            Attendance.objects.create(
                rollnum=student,  # Use the Student instance here
                date=now(),
                status=True
            )
            return {"success": True, "message": "Attendance marked"}

    return {"success": False, "message": "Face not recognized"}
    

def get_attendance_details(request):
    # Fetch all students
    students = Student.objects.all()
    attendance_data = []

    for student in students:
        total_classes = Attendance.objects.filter(rollnum=student).count()
        attended_classes = Attendance.objects.filter(rollnum=student, status=True).count()
        attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0

        # Append data for each student
        attendance_data.append({
            "name": student.name,
            "roll_number": student.rollnum,
            "present": Attendance.objects.filter(rollnum=student, date__gte=now() - timedelta(minutes=1), status=True).exists(),
            "attendance_percentage": round(attendance_percentage, 2)
        })

    return JsonResponse({"attendance": attendance_data})

attendance_tracking_active = False

def start_day(request):
    global attendance_tracking_active
    if request.method == "POST":
        if attendance_tracking_active:
            return JsonResponse({"success": False, "message": "Day already started!"})
        
        attendance_tracking_active = True

        # Start the attendance tracking thread
        threading.Thread(target=track_attendance).start()

        return JsonResponse({"success": True, "message": "Day started! Attendance tracking is active."})
    
    return JsonResponse({"success": False, "message": "Invalid request method."})


def track_attendance():
    """
    Track attendance every hour (1 minute for testing) for the next 4 hours.
    """
    global attendance_tracking_active
    try:
        for i in range(4):  # Loop for 4 hours
            current_time = now()

            # Get all students and check their presence
            students = Student.objects.all()
            for student in students:
                # Check if the student is marked present within this hour
                present = Attendance.objects.filter(
                    rollnum=student, 
                    date__gte=current_time - timedelta(minutes=1),
                    date__lte=current_time,
                    status=True
                ).exists()

                if not present:
                    # Mark the student absent for this hour
                    Attendance.objects.create(
                        rollnum=student,
                        date=current_time,
                        status=False  # Absent
                    )
            
            # Wait 1 minute before the next hour (testing purposes)
            threading.Event().wait(60)
        
    except Exception as e:
        print(f"Error in attendance tracking: {e}")
    
    # Stop tracking after 4 hours
    attendance_tracking_active = False

def index(request):
    return render(request, 'attendancemark/index1.html')

def admin_page(request):
    return render(request, 'attendancemark/adminpage.html')