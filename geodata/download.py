from __future__ import annotations
from pathlib import Path
import getpass
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import rasterio.plot
from rasterio import features

from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    MosaickingOrder,
    SentinelHubRequest,
    bbox_to_dimensions,
)

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from config import config
from eval_scripts import (
    evalscript_all_bands,
    ndvi_eval,
    evalscript_5p,
    evalscript_mean_mosaic,
)


def plot_image(
    image: np.ndarray,
    factor: float = 1.0,
    clip_range: tuple[float, float] | None = None,
    **kwargs: Any,
) -> None:
    """Utility function for plotting RGB images."""
    _, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, **kwargs)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.savefig("test.png")


if __name__ == "__main__":
    s2 = False
    s5 = True

    if s2:
        # Sentinel 2
        coords = (5.0, 51.9, 5.2, 52.0)
        resolution = 10
        bbox = BBox(bbox=coords, crs=CRS.WGS84)
        extent = bbox_to_dimensions(bbox, resolution=resolution)

        request_all_bands = SentinelHubRequest(
            data_folder="test_dir",
            evalscript=evalscript_5p,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL5P.define_from(
                        "5p", service_url=config.sh_base_url
                    ),
                    time_interval=("2024-06-01", "2024-06-30"),
                    mosaicking_order=MosaickingOrder.LEAST_CC,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=extent,
            config=config,
        )

        all_bands_img = request_all_bands.get_data(save_data=True)

    if s5:

        bbox_europe = BBox([-12.30, 34.59, 32.52, 63.15], crs=CRS.WGS84).transform(
            CRS(3857)
        )
        # This is defining the data we will use.
        # You can list all available data collections with `DataCollection.get_available_collections()`.
        data_5p = DataCollection.SENTINEL5P.define_from(
            "5p", service_url=config.sh_base_url
        )

        request_monthly = SentinelHubRequest(
            evalscript=evalscript_mean_mosaic,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=data_5p,
                    time_interval=("2021-08-01", "2021-08-30"),
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox_europe,
            resolution=(5000, 3500),
            config=config,
            data_folder="./data",
        )

        mean_data = request_monthly.get_data(save_data=True)
