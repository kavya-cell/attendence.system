import tensorflow as tf
import keras
from keras import layers
import cv2 as cv
import os 
import matplotlib.pyplot as plt
import numpy as np
import random
import pickle

training_data = []
DataDir = "C:/Users/Navan/Desktop/attendence.system/attendance_sys/dataset/"
classes = ["with_mask", "without_mask"]
def create_training_data():
    for category in classes:
        path = os.path.join(DataDir, category)
        class_num = classes.index(category)
        for i in os.listdir(path):
            try:
                img_array = cv.imread(os.path.join(path,i))
                new_array = cv.resize(img_array, (224, 224))
                training_data.append([new_array, class_num])
            except Exception as e:
                pass
#to load images from the dataset folder.
create_training_data()
random.shuffle(training_data)

X= []    #data
y = []    #label
#feat = features, lab = labels
for feat, lab in training_data:
    X.append(feat)
    y.append(lab)

X = np.array(X).reshape(-1, 224, 224, 3)
y = np.array(y)
X = X/255.0

pickle_out = open("X.pickle", "wb")
pickle.dump(X, pickle_out)
pickle_out.close()
pickle_out = open("y.pickle", "wb")
pickle.dump(y, pickle_out)
pickle_out.close()

pickle_in = open("X.pickle", "rb")
X = pickle.load(pickle_in)
pickle_in = open("y.pickle", "rb")
y = pickle.load(pickle_in)

base_model = keras.applications.mobilenet.MobileNet(weights="imagenet", include_top=False, input_shape=(224, 224, 3)) # <- Pre trained model that we are going to use and to identify faces with and without mask, using transfer learning
                                                 # Transfer learning : using existing solution, and modifyin some layers of the pre trained model to fit out needs.


base_output = base_model.output  # Output of the pre-trained model
flat_layer = layers.GlobalAveragePooling2D()(base_output)  # Flatten feature maps
dense_layer = layers.Dense(128, activation='relu')(flat_layer)  # Add a dense layer
final_output = layers.Dense(1, activation='sigmoid')(dense_layer)  # Final binary classification

# Create a New Model
new_model = keras.Model(inputs=base_model.input, outputs=final_output)

# Freeze the Base Model Layers
for layer in base_model.layers:
    layer.trainable = False
# Compile the Model
new_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
new_model.fit(X,y,epochs = 2, validation_split = 0.1)



new_model.save('masks.keras', save_format='h5')
new_model = keras.models.load_model('masks.keras')

frame = cv.imread('C:/Users/Navan/Desktop/attendence.system/attendance_sys/mask_detection/mask.jpg')
 
face = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

faces = face.detectMultiScale(gray, 1.1, 4)
for x,y,w,h in faces:
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = frame[y:y+h, x:x+w]
    facess = face.detectMultiScale(roi_gray)
    if len(facess) == 0:
        print("Face not detected")
    else:
        for (ex, ey, ew, eh) in facess:
            face_roi = roi_color[ey:ey+eh, ex:ex+ew]
final = cv.resize(face_roi, (224, 224))
final = np.expand_dims(final, axis = 0)
final = final/255.0

predictions = new_model.predict(final)

print(predictions)