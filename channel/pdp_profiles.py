import numpy as np

# Typical Urban
TU = {
    "name": "Typical Urban",
    "delays": np.array([0, 0.2e-6, 0.5e-6, 1.6e-6, 2.3e-6, 5e-6]),
    "powers_db": np.array([0, -2, -4, -6, -8, -10])
}

# Rural Area
RA = {
    "name": "Rural Area",
    "delays": np.array([0, 0.2e-6, 0.4e-6, 0.6e-6]),
    "powers_db": np.array([0, -2, -4, -7])
}

# Hilly Terrain
HT = {
    "name": "Hilly Terrain",
    "delays": np.array([0, 0.2e-6, 0.4e-6, 0.6e-6, 15e-6, 17e-6]),
    "powers_db": np.array([0, -2, -4, -7, -6, -12])
}

CHANNEL_PROFILES = {
    "TU": TU,
    "RA": RA,
    "HT": HT
}