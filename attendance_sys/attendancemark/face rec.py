import cv2, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition

known_face_encodings = []
known_face_names = []

# Load known images and encode faces

known_person1_image = face_recognition.load_image_file(r"C:\Users\Navan\Desktop\attendence.system\attendance_sys\attendancemark\static\attendancemark\images\known_person_1.png")
known_person2_image = face_recognition.load_image_file(r"C:\Users\Navan\Desktop\attendence.system\attendance_sys\attendancemark\static\attendancemark\images\known_perosn_2.png")
known_person3_image = face_recognition.load_image_file(r"C:\Users\Navan\Desktop\attendence.system\attendance_sys\attendancemark\static\attendancemark\images\unknown.jpg")

# Encode known faces
known_person1_encoding = face_recognition.face_encodings(known_person1_image)[0]
known_person2_encoding = face_recognition.face_encodings(known_person2_image)[0]
known_person3_encoding = face_recognition.face_encodings(known_person3_image)[0]

known_face_encodings.append(known_person1_encoding)
known_face_encodings.append(known_person2_encoding)
known_face_encodings.append(known_person3_encoding)

known_face_names.append("kavya")
known_face_names.append("keerthana")
known_face_names.append("sharukh khan")

video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"  

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]


        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)


    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


video_capture.release()
cv2.destroyAllWindows()