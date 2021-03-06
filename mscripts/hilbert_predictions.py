import os
import warnings

import keras
from keras import layers
from keras import models
from keras import backend

import keras
import pickle
import tensorflow as tf
import numpy as np
from keras import backend as K
from keras.models import *
from keras.layers import *

from sklearn.linear_model import LogisticRegression


def dense_block(x, blocks, name):
    """A dense block.
    # Arguments
        x: input tensor.
        blocks: integer, the number of building blocks.
        name: string, block label.
    # Returns
        output tensor for the block.
    """
    for i in range(blocks):
        x = conv_block(x, 32, name=name + '_block' + str(i + 1))
    return x


def transition_block(x, reduction, name):
    """A transition block.
    # Arguments
        x: input tensor.
        reduction: float, compression rate at transition layers.
        name: string, block label.
    # Returns
        output tensor for the block.
    """
    bn_axis = 3 if backend.image_data_format() == 'channels_last' else 1
    x = layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5,
                                  name=name + '_bn')(x)
    x = layers.Activation('relu', name=name + '_relu')(x)
    x = layers.Conv2D(int(backend.int_shape(x)[bn_axis] * reduction), 1,
                      use_bias=False,
                      name=name + '_conv')(x)
    x = layers.AveragePooling2D(2, strides=2, name=name + '_pool')(x)
    return x


def conv_block(x, growth_rate, name):
    """A building block for a dense block.
    # Arguments
        x: input tensor.
        growth_rate: float, growth rate at dense layers.
        name: string, block label.
    # Returns
        Output tensor for the block.
    """
    bn_axis = 3 if backend.image_data_format() == 'channels_last' else 1
    x1 = layers.BatchNormalization(axis=bn_axis,
                                   epsilon=1.001e-5,
                                   name=name + '_0_bn')(x)
    x1 = layers.Activation('relu', name=name + '_0_relu')(x1)
    x1 = layers.Conv2D(4 * growth_rate, 1,
                       use_bias=False,
                       name=name + '_1_conv')(x1)
    x1 = layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5,
                                   name=name + '_1_bn')(x1)
    x1 = layers.Activation('relu', name=name + '_1_relu')(x1)
    x1 = layers.Conv2D(growth_rate, 3,
                       padding='same',
                       use_bias=False,
                       name=name + '_2_conv')(x1)
    x = layers.Concatenate(axis=bn_axis, name=name + '_concat')([x, x1])
    return x

img_height = 30
img_width = 30

def DenseNet(blocks=[6, 12, 24, 16]):
    
    input_shape = [img_height, img_width, 5]
    img_input = layers.Input(shape=input_shape)
    
    bn_axis = 3 if backend.image_data_format() == 'channels_last' else 1

    x = layers.ZeroPadding2D(padding=((3, 3), (3, 3)))(img_input)
    x = layers.Conv2D(64, 7, strides=2, use_bias=False, name='conv1/conv')(x)
    x = layers.BatchNormalization(
        axis=bn_axis, epsilon=1.001e-5, name='conv1/bn')(x)
    x = layers.Activation('relu', name='conv1/relu')(x)
    x = layers.ZeroPadding2D(padding=((1, 1), (1, 1)))(x)
    x = layers.MaxPooling2D(3, strides=2, name='pool1',dim_ordering="th" )(x)

    x = dense_block(x, blocks[0], name='conv2')
    x = transition_block(x, 0.5, name='pool2')
    x = dense_block(x, blocks[1], name='conv3')
    x = transition_block(x, 0.5, name='pool3')
    x = dense_block(x, blocks[2], name='conv4')
    x = transition_block(x, 0.5, name='pool4')
    x = dense_block(x, blocks[3], name='conv5')

    x = layers.BatchNormalization(
        axis=bn_axis, epsilon=1.001e-5, name='bn')(x)
    x = layers.Activation('relu', name='relu')(x)

    x = layers.GlobalAveragePooling2D(name='avg_pool')(x)
    x = layers.Dense(1, activation='sigmoid', name='fc')(x)

    # Ensure that the model takes into account
    # any potential predecessors of `input_tensor`.
    inputs = img_input
    model = models.Model(inputs, x, name='densenet121')
    return model

def predict_old(x,pred_time):
    model = DenseNet()
    model.summary()
    adam = keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=['accuracy'])
    model.load_weights('weights/Shock_'+str(pred_time)+'hr_densenet_hilbert/weights-hilbert-loop-model_1.hdf5')
    result = model.predict(x, batch_size=1)
    return result[0][0]

def predict(x,pred_time,age,gender):
    model = DenseNet()
    model.summary()
    adam = keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=['accuracy'])
    model.load_weights('weights/Shock_'+str(pred_time)+'hr_densenet_hilbert/weights-hilbert-loop-model_1.hdf5')

    intermediate_layer_model = Model(inputs=model.input, outputs= model.layers[-2].output)
    # global graph
    # graph = tf.get_default_graph()
    # with graph.as_default():
    #     global result
    result = intermediate_layer_model.predict(x)
        # result = result[0][0]
    print(result,age,gender,result.shape)
    demo = (int(age),int(gender))
    demo = np.reshape(demo,(1,2))
    result = np.concatenate((result, demo), axis = 1)

    print(result)

    # mean_calc1 = np.mean(result, axis=0)
    # std_calc1 = np.std(result, axis = 0, ddof = 1)

    # result -= mean_calc1
    # result /= (std_calc1 + K.epsilon())

    print(result,result.shape)
    with open('weights/Shock_'+str(pred_time)+'hr_densenet_hilbert/mimic+hilbert+age+gender+final'+str(pred_time)+'hr.pkl', 'rb') as f:
        clf = pickle.load(f,encoding='latin1')
    result = clf.predict_proba(result)
    return result[0,1]