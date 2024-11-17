import io
import numpy as np
from OpenGL.GL import *
from PIL import Image
import importlib.resources


import force_awakens.images


# initialize buffers
def create_vbo(data):
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo


# function that updates the vbo (a buffer); using new data from the beggining of the buffer
def update_vbo(vbo, data):
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferSubData(GL_ARRAY_BUFFER, 0, data.nbytes, data)
    glBindBuffer(GL_ARRAY_BUFFER, 0)


def draw_vbo(vbo, stride, draw_type, n, v_ptr=3, c_ptr=3):
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(v_ptr, GL_FLOAT, stride, ctypes.c_void_p(0))
    glEnableClientState(GL_COLOR_ARRAY)
    size = stride // (v_ptr + c_ptr)
    glColorPointer(c_ptr, GL_FLOAT, stride, ctypes.c_void_p(v_ptr * size))

    # glPointSize(1.0)
    glDrawArrays(draw_type, 0, n)

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, 0)


# function for initializing all of the images, the bits, their settings, their width and returns those parameters appropriated for the given images
def load_texture_simple(image_path):
    bits = importlib.resources.read_binary(force_awakens.images, image_path)
    image = Image.open(io.BytesIO(bits))
    # convverts images to bytes
    img_data = image.convert("RGBA").tobytes()
    width, height = image.size
    # just importing and initialzing a bunch of parameters that will be used later in the program
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data
    )

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id, width, height
