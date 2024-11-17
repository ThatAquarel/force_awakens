import io
import numpy as np
from OpenGL.GL import *
from PIL import Image
import importlib.resources


import force_awakens.images


# initialize buffers
def create_vbo(data):
    # vertex buffer object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo


# function that updates the vbo (a buffer); using new data from the beggining of the buffer
def update_vbo(vbo, data):
    # change vertex buffer object data
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferSubData(GL_ARRAY_BUFFER, 0, data.nbytes, data)
    glBindBuffer(GL_ARRAY_BUFFER, 0)


def draw_vbo(vbo, stride, draw_type, n, v_ptr=3, c_ptr=3):
    # bind to VBO
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    # enable vertex followed by color within VBOs
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(v_ptr, GL_FLOAT, stride, ctypes.c_void_p(0))
    glEnableClientState(GL_COLOR_ARRAY)

    # calculate color offset (assuming data is tightly packed)
    # color comes after vertex
    size = stride // (v_ptr + c_ptr)
    glColorPointer(c_ptr, GL_FLOAT, stride, ctypes.c_void_p(v_ptr * size))

    # draw VBO
    glDrawArrays(draw_type, 0, n)

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, 0)


# function for initializing all of the images, the bits, their settings, their width and returns those parameters appropriated for the given images
def load_texture_simple(image_path, size=None):
    # obtain resource
    bits = importlib.resources.read_binary(force_awakens.images, image_path)
    image = Image.open(io.BytesIO(bits))

    # convverts images to bytes
    if type(size) != type(None):
        # if we want a fixed size, create buffer to store image
        buf = np.zeros((*size, 4), dtype=np.uint8)

        # copy image data into fixed size buffer
        img = np.array(image.convert("RGBA"))
        h, w, _ = np.min([buf.shape, img.shape], axis=0)
        buf[:h, :w] = img[:h, :w]

        # convert to bytes and calculate buffer size
        img_data = buf.tobytes()
        width, height = size[::-1]
    else:
        # directly convert to bytes
        img_data = image.convert("RGBA").tobytes()
        width, height = image.size

    # bind texture
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data
    )

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id, width, height
