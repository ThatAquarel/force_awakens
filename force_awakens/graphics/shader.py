import importlib.resources

from OpenGL.GL import glUseProgram, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
from OpenGL.GL.shaders import compileShader, compileProgram

import force_awakens.graphics


def load_shader(file, type):
    s = importlib.resources.read_text(force_awakens.graphics, file)
    return compileShader(s, type)


def get_shader_program():
    v = load_shader("vertex_shader.glsl", GL_VERTEX_SHADER)
    f = load_shader("fragment_shader.glsl", GL_FRAGMENT_SHADER)

    return compileProgram(v, f)
