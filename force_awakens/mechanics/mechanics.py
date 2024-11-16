import numpy as np

from OpenGL.GL import *

from force_awakens.graphics.draw import rotation_matrix

T = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])

def add_body(render_calls, mask, s, v, zoom, cam_t):
    modelview_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    modelview_matrix = np.array(modelview_matrix).reshape(4, 4)
    vector = np.array([0.0, 0.0, -1.0, 1])
    transformed_vector = np.dot(modelview_matrix, vector)

    vec = transformed_vector[:3]

    vector_2 = np.array([0, 10, -10.0, 1.0]) - np.array([*cam_t, 0, 0])
    transformed_vector = np.dot(modelview_matrix, vector_2)
    vec_t = transformed_vector[:3]

    i = np.argmin(mask)

    s[i] = vec_t @ np.linalg.inv(T)
    v[i] = vec @ np.linalg.inv(T)

    mask[i] = True
    render_calls[i].prev_n = 0
