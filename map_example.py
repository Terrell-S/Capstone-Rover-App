import math
import matplotlib.pyplot as plt

# Example motor/encoder data (left_wheel, right_wheel)
# Each pair represents movement per time step (in rotations)
motor_data = [
    (0.1, 0.1), (0.1, 0.40), (0.1, 0.1),
    (0.1, 0.05), (0.1, 0.1), (0.12, 0.1)
]

# Robot parameters
wheel_radius = 0.05  # meters
wheel_base = 0.2     # meters

# Initial pose (x, y, heading)
x, y, theta = 0, 0, 0

positions = [(x, y)]

for left, right in motor_data:
    # Convert rotations to distance
    d_left = 2 * math.pi * wheel_radius * left
    d_right = 2 * math.pi * wheel_radius * right
    d_center = (d_left + d_right) / 2.0

    # Change in heading
    d_theta = (d_right - d_left) / wheel_base

    # Update pose
    x += d_center * math.cos(theta + d_theta / 2)
    y += d_center * math.sin(theta + d_theta / 2)
    theta += d_theta

    positions.append((x, y))

# Plot path
xs, ys = zip(*positions)
plt.plot(xs, ys, marker='o')
plt.axis('equal')
plt.title("Path drawn from motor data")
plt.xlabel("X position (m)")
plt.ylabel("Y position (m)")
plt.show()
