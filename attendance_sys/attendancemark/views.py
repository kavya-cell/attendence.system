from django.shortcuts import render, HttpResponse
import cv2, json, base64
# from io import BytesIO
# import numpy as np
# from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
from .models import Student, Attendance

# Create your views here.

def recognition():
    video_capture = cv2.VideoCapture(0)
    students = Student.objects.all()
    known_students_encoding = []
    for student in students:
        simageload = face_recognition.load_image_file(student.image)
        student_encoding = face_recognition.face_encodings(simageload)[0]
        known_students_encoding.append({'encoding': student_encoding,
                                        'name': student.name})
        recognized_dude = None

        while True:
            ret, frame = video_capture.read()
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            for i in face_encodings:
                matches = face_recognition.compare_faces(known_students_encoding, i)
                if True in matches: 
                    match_index = matches.index(True)
                    recognized_dude.append({
                        'name': student.name,
                        'rollno': student.rollnum,
                    })
                    break

            cv2.imshow("video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    video_capture.release()
    cv2.destroyAllWindows()
    return recognized_dude
        


@csrf_exempt
def index(request):
    if request.method == 'POST':
        recognized_dude = recognition()
        if recognized_dude:
            data = {
                'name' : recognized_dude.name
            }
            return JsonResponse({'success' : True, 'person': data})
        else: 
            return JsonResponse({'success': False, 'message':'Couldnt recognize face'})
    return render(request, 'attendancemark/index.html')

# def recognize(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         image_data = data.get('image')

#         if image_data.startswith('data:image/jpeg;base64,'):
#             image_data = image_data[len('data:image/jpeg;base64,'):]

#         img_data = base64.b64decode(image_data)
#         image = Image.open(BytesIO(img_data))
#         frame = face_recognition.load_image_file(BytesIO(img_data))

#         face_locations = face_recognition.face_locations(frame)
#         face_encodings = face_recognition.face_encodings(frame, face_locations)

#         recognized_dude = []

#         for i in face_encodings:
#             for student in Student.objects.all():
#                 student_encoding = face_recognition.face_encodings(student.image)[0]
#                 matches = face_recognition.compare_faces([student_encoding], i)

#                 if True in matches: 
#                     recognized_dude.append({
#                         'name': student.name,
#                         'rollno': student.rollnum,
#                     })
    
#         return JsonResponse({'recognized_dude': recognized_dude})
#     return JsonResponse({'error': 'Invalid request'}, status=400)
