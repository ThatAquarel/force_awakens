import numpy as np
from OpenGL.GL import *
from PIL import Image


def create_vbo(data):
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo


def update_vbo(vbo, data):
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferSubData(GL_ARRAY_BUFFER, 0, data.nbytes, data)
    glBindBuffer(GL_ARRAY_BUFFER, 0)


def load_texture(file, face_size=1024):
    atlas = Image.open(file)
    # img = img.transpose(Image.FLIP_TOP_BOTTOM)
    cubemap_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap_texture)

    # Calculate face regions (assumes a 3x2 layout in the atlas)
    faces = [
        (2 * face_size, 0),  # +X
        (0 * face_size, 0),  # -X
        (1 * face_size, 1 * face_size),  # +Y
        (1 * face_size, 0),  # -Y
        (1 * face_size, 0),  # +Z
        (1 * face_size, 1 * face_size),  # -Z
    ]

    for i, (x, y) in enumerate(faces):
        face = atlas.crop((x, y, x + face_size, y + face_size))
        face = face.transpose(Image.FLIP_TOP_BOTTOM)  # Flip for OpenGL
        img_data = np.array(face, dtype=np.uint8)

        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB,
                     face_size, face_size, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    return cubemap_texture
