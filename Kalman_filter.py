import numpy as np
from scipy.linalg import block_diag


# Define the Kalman Filter parameters
def initialize_kalman_filter():
    # State transition matrix F
    F = np.array([[1, 0, 1, 0],
                  [0, 1, 0, 1],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])

    # Measurement matrix H
    H = np.array([[1, 0, 0, 0],
                  [0, 1, 0, 0]])

    # Process noise covariance matrix Q
    Q = np.diag([0.01, 0.01, 0.01, 0.01])

    # Measurement noise covariance matrix R
    R = np.diag([0.1, 0.1])

    # Initial state estimate (x) and covariance (P)
    x = np.array([0, 0, 0, 0])  # Initial state guess
    P = np.diag([1, 1, 1, 1])  # Initial state covariance

    return F, H, Q, R, x, P


# Kalman Filter implementation
def kalman_filter(F, H, Q, R, x, P, measurements):
    estimated_positions = []

    for z in measurements:
        # Prediction step
        x_hat = np.dot(F, x)
        P_hat = np.dot(np.dot(F, P), F.T) + Q

        # Update step
        y = z - np.dot(H, x_hat)
        S = np.dot(np.dot(H, P_hat), H.T) + R
        K = np.dot(np.dot(P_hat, H.T), np.linalg.inv(S))
        x = x_hat + np.dot(K, y)
        P = np.dot((np.eye(4) - np.dot(K, H)), P_hat)

        # Extract estimated positions (Dx and Dy)
        estimated_positions.append((x[0], x[1]))

    return estimated_positions


# Load your dataset with columns: Dx, Dy, Sv, Sx, Sy, T
# Replace 'your_dataset.csv' with the actual path to your dataset file.
import pandas as pd

dataset = pd.read_csv('your_dataset.csv')

# Filter out measurements with zero Dx and Dy (noise)
dataset = dataset[(dataset['Dx'] != 0) & (dataset['Dy'] != 0)]

# Extract measurements (Dx and Dy) and timestamps (T)
measurements = dataset[['Dx', 'Dy']].values
timestamps = dataset['T'].values

# Initialize Kalman Filter
F, H, Q, R, x, P = initialize_kalman_filter()

# Apply Kalman Filter to estimate positions
estimated_positions = kalman_filter(F, H, Q, R, x, P, measurements)

# Print or use estimated positions for further analysis
for i, (estimated_dx, estimated_dy) in enumerate(estimated_positions):
    print(f"Timestamp {timestamps[i]}: Estimated Dx = {estimated_dx}, Estimated Dy = {estimated_dy}")
    