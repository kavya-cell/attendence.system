from django.shortcuts import render, HttpResponse
import cv2, json, base64
from io import BytesIO
import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
from .models import Student, Attendance
import logging
logger = logging.getLogger(__name__)
# Create your views here.
@csrf_exempt
def index(request):
    if request.method == 'GET':
        return render(request, "attendancemark/index.html")
    elif request.method == 'POST':
        # data = json.loads(request.body)
        # image_data = data.get('image')

        # if image_data.startswith('data:image/jpeg;base64,'):
        #     image_data = image_data[len('data:image/jpeg;base64,'):]

        # img_data = base64.b64decode(image_data)
        # image = Image.open(BytesIO(img_data))
        # frame = face_recognition.load_image_file(BytesIO(img_data))
        logger.info("Recieved")
        data = request.body.decode("utf-8")
        frame_data = base64.b64decode(data.split(",")[1])  # Remove the "data:image/jpeg;base64," part
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        logger.info("Frame decoded")

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        recognized_dude = []

        for i in face_encodings:
            for student in Student.objects.all():
                simageload = face_recognition.load_image_file(student.image)
                student_encoding = face_recognition.face_encodings(simageload)[0]
                matches = face_recognition.compare_faces([student_encoding], i)

                if True in matches: 
                    recognized_dude.append({"name": "Alice", "rollno": "002"}
                    #                        {
                    #     'name': student.name,
                    #     'rollno': student.rollnum,
                    # }
                    )
        return JsonResponse({"recognized_dude": [{"name": "Alice", "rollno": "002"}]})
        # return JsonResponse({'recognized_dude': recognized_dude})
    return JsonResponse({'error': 'Invalid request'}, status=400)



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
