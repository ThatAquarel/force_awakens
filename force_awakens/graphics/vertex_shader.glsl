#version 330 core

layout(location = 0) in vec3 position;

uniform mat4 camera_projection;
uniform mat4 camera_position;

out vec3 originalPosition;

void main() {
    mat4 rh = mat4(
        1.0, 0.0, 0.0, 0.0,
        0.0, 0.0, -1., 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    );

    gl_Position = vec4(position, 1.0) * rh * camera_position * camera_projection;
    originalPosition = position;
}
