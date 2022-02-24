from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import tensorflow as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
def main(img_path):
    model = ResNet50(weights='imagenet')
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    with tf.get_default_graph().as_default():
        preds = model.predict(x)
        predection_label=decode_predictions(preds, top=1)[0]
    return predection_label[0][1]
# img_path='ele.jpeg'
# print(main(img_path))