import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
glClearColor(0.1, 0.1, 0.1, 1)  # Set background color

# Shader code
vertex_shader_code = """
#version 130
in vec3 position;
in vec2 texcoord;
out vec2 v_texcoord;
void main() {
    gl_Position = vec4(position, 1.0);
    v_texcoord = texcoord;
}
"""

fragment_shader_code = """
#version 130
in vec2 v_texcoord;
out vec4 color;
uniform sampler2D texSampler;
void main() {
    vec4 texColor = texture(texSampler, v_texcoord);
    if (texColor.r > 0.8 && texColor.g > 0.8 && texColor.b > 0.8) {
        color = texColor;  # Keep bright parts
    } else {
        color = vec4(0.0, 0.0, 0.0, 0.0);  # Darken the others
    }
}
"""


def compile_shader(shader_code, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, shader_code)
    glCompileShader(shader)

    # Check for compilation errors
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error_message = glGetShaderInfoLog(shader)
        print(f"Shader compilation failed: {error_message}")
        return None
    return shader


def create_program(vertex_shader_code, fragment_shader_code):
    vertex_shader = compile_shader(vertex_shader_code, GL_VERTEX_SHADER)
    if vertex_shader is None:
        raise RuntimeError("Vertex shader compilation failed")

    fragment_shader = compile_shader(fragment_shader_code, GL_FRAGMENT_SHADER)
    if fragment_shader is None:
        raise RuntimeError("Fragment shader compilation failed")

    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)

    # Check for program linking errors
    if not glGetProgramiv(program, GL_LINK_STATUS):
        error_message = glGetProgramInfoLog(program)
        print(f"Program linking failed: {error_message}")
        return None

    return program


# Create shaders and program
program = create_program(vertex_shader_code, fragment_shader_code)

# Create simple quad to render
vertices = np.array(
    [
        -1.0,
        -1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        -1.0,
        0.0,
        1.0,
        0.0,
        1.0,
        1.0,
        0.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        0.0,
        0.0,
        1.0,
    ],
    dtype=np.float32,
)

indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

# Create VAO, VBO, and EBO
vao = glGenVertexArrays(1)
vbo = glGenBuffers(1)
ebo = glGenBuffers(1)

glBindVertexArray(vao)

# VBO
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

# EBO
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

# Position attribute
glVertexAttribPointer(
    0, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(0)
)
glEnableVertexAttribArray(0)

# Texture coordinate attribute
glVertexAttribPointer(
    1,
    2,
    GL_FLOAT,
    GL_FALSE,
    5 * vertices.itemsize,
    ctypes.c_void_p(3 * vertices.itemsize),
)
glEnableVertexAttribArray(1)

glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

# Texture
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

# Simple color texture
image = np.zeros((256, 256, 3), dtype=np.uint8)
image[100:200, 100:200] = [255, 255, 255]  # Bright white square
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 256, 256, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

glUseProgram(program)
glUniform1i(glGetUniformLocation(program, "texSampler"), 0)

# Rendering loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Render the scene (here we use the quad)
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
