import face_recognition
import cv2
import numpy as np
known_image_1 = face_recognition.load_image_file("static/attendancemark/known_person_1.png")
known_image_1_encoding = face_recognition.face_encodings(known_image_1)[0]

# known_image_2 = face_recognition.load_image_file("static/attendancemark/known_person_2.png")
# known_image_2_encoding = face_recognition.face_encodings(known_image_2)[0]

known_face_encodings = [known_image_1_encoding]
known_face_names = ["Person 1", "Person 2"]
unknown_image = face_recognition.load_image_file("static/attendancemark/unknown.jpg")
face_locations = face_recognition.face_locations(unknown_image)
face_encodings = face_recognition.face_encodings(unknown_image, face_locations)


image_to_display = cv2.cvtColor(unknown_image, cv2.COLOR_RGB2BGR)


for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    name = "Unknown"

    if True in matches:
        match_index = matches.index(True)
        name = known_face_names[match_index]

  
    cv2.rectangle(image_to_display, (left, top), (right, bottom), (0, 255, 0), 2)

 
    cv2.putText(image_to_display, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow("Face Recognition", image_to_display)
cv2.waitKey(0)
cv2.destroyAllWindows()