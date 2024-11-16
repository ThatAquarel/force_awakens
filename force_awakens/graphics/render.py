from OpenGL.GL import (
    glGenBuffers,
    glBindBuffer,
    glBufferData,
    glBufferSubData,
    GL_ARRAY_BUFFER,
    GL_DYNAMIC_DRAW,
)


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
