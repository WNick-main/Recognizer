from keras.models import load_model
from os import path
import cv2
from numpy import argmax


def get_img(file_path):
	'''Загружаем и обрабатываем картинку'''
	image_size = (150, 150)

	image = cv2.imread(file_path)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image = cv2.resize(image,image_size)
	return image


def recognize_img(image):
	'''Распознаем картинку'''
	class_names=['buildings', 'forest', 'glacier','mountain','sea','street']
	class_names_label = {class_name:i for i, class_name in enumerate(class_names)}
	print(class_names_label)

	origin_path = path.dirname(__file__)
	# origin_path = '/scripts/recognizer'  # os.path.abspath("") # '/scripts/recognizer'  #
	model = load_model(origin_path + "/model")

	y_pred=model.predict(image.reshape(1, 150,150,3))
	print("Results of image classification:", y_pred)
	pred_label = argmax(y_pred, axis=1)
	print("Our image belongs to class:", class_names[pred_label[0]])

	probabilities = dict(zip(class_names, y_pred[0]))
	del model

	return probabilities, class_names[pred_label[0]]


def start_recognition(img_path):
	'''Основной процесс'''
	img = get_img(img_path)
	result = recognize_img(img)
	del img
	return result
