from keras.models import load_model
import os
import cv2
import numpy as np

def get_path():
	'''Генерим путь к файлу'''
	directory=os.path.abspath("")
	test_image_filename='input_img.jpg'
	img_path=os.path.join(directory,test_image_filename)
	return img_path


def get_img(file_path):
	'''Загружаем и обрабатываем картинку'''
	image_size=(150,150)

	image=cv2.imread(file_path)
	image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image=cv2.resize(image,image_size)
	return image


def recognize_img(image):
	'''Распознаем картинку'''
	class_names=['buildings', 'forest', 'glacier','mountain','sea','street']
	class_names_label = {class_name:i for i, class_name in enumerate(class_names)}
	nb_classes=len(class_names)
	print(class_names_label)

	origin_path = '/scripts/recognizer'  # os.path.abspath("") #
	model = load_model(origin_path + "/model")

	y_pred=model.predict(image.reshape(1, 150,150,3))
	print("Results of image classification:", y_pred)
	pred_label = np.argmax(y_pred, axis=1)
	print("Our image belongs to class:", class_names[pred_label[0]])

	probabilities = dict(zip(class_names, y_pred[0]))

	return probabilities, class_names[pred_label[0]]


def start_recognition(img_path):
	'''Основной процесс'''
	# img_path = get_path()
	img = get_img(img_path)
	result = recognize_img(img)
	return result
