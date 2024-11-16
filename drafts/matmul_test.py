import numpy as np

# Example matrices (n x 3 x 3) and points (n x 3)
matrices = np.array(
    [
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[0, -1, 0], [1, 0, 0], [0, 0, 1]],
        [[0, 0, 1], [0, 1, 0], [-1, 0, 0]],
        [[0, 0, 1], [0, 1, 0], [-1, 0, 0]],
    ]
)  # Shape: (3, 3, 3)

points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [7, 8, 9]])  # Shape: (3, 3)

# Reshape points to (n, 3, 1) to treat them as column vectors
points = points[:, :, np.newaxis]  # Shape: (n, 3, 1)

# Perform matrix multiplication (n x 3 x 3) @ (n x 3 x 1)
transformed_points = np.matmul(matrices, points)  # Shape: (n, 3, 1)

# Remove the last dimension to get back to (n, 3)
transformed_points = transformed_points.squeeze(-1)

print("Original Points:\n", points.squeeze(-1))
print("\nMatrices:\n", matrices)
print("\nTransformed Points:\n", transformed_points)
