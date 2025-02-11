import numpy as np
#colors representing the closest ressembling rgb combination to all of the given planets (21 of them)
COLORS = (
    np.array(
        [
            [130, 216, 255],
            [130, 216, 255],
            [130, 216, 255],
            [255, 179, 0],
            [255, 179, 0],
            [255, 94, 0],
            [255, 94, 0],
            [102, 40, 0],
            [107, 212, 32],
            [107, 212, 32],
            [0, 0, 255],
            [107, 212, 32],
            [255, 179, 0],
            [255, 94, 0],
            [107, 212, 32],
            [61, 58, 54],
            [107, 212, 32],
            [107, 212, 32],
            [36, 36, 34],
            [235, 140, 40],
            [89, 121, 150],
        ],
        dtype=np.float32,
    )
    / 255
)
