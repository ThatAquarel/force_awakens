import numpy as np

from OpenGL.GL import *

from force_awakens.graphics.draw import rotation_matrix
# creates a numpy array 
T = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
# function that gets the camera homogenous transformation projection matrixes
def add_body(render_calls, mask, s, v, zoom, cam_t):
    modelview_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    modelview_matrix = np.array(modelview_matrix).reshape(4, 4)
    #vector that points out of the camera and is then transformed into the one representing the camera's perspective
    vector = np.array([0.0, 0.0, -1.0, 1])
    transformed_vector = np.dot(modelview_matrix, vector)
    
    vec = transformed_vector[:3]
    # get the x y z coordinates of the resulting vector (position vector)
    vector_2 = np.array([0, 10, -10.0, 1.0]) - np.array([*cam_t, 0, 0])
    transformed_vector = np.dot(modelview_matrix, vector_2)
    vec_t = transformed_vector[:3]

    i = np.argmin(mask)
    #getting the first body that avalaible that we can draw (in relation to the mouse cursor)
    s[i] = vec_t @ np.linalg.inv(T)
    v[i] = vec @ np.linalg.inv(T)

    mask[i] = True
    render_calls[i].prev_n = 0
    render_calls[i].intro = True

    return i
