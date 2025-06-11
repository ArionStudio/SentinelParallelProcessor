import numpy as np
from typing import Dict, Tuple, Optional

from sentinelhub import (
    SentinelHubRequest,
    DataCollection,
    MimeType,
    CRS,
    BBox,
    SHConfig,
)


class SentinelDataLoader:
    """
    Handles fetching satellite imagery bands (B04, B08, B11) and the data mask
    from the Sentinel Hub Process API using a pre-configured SHConfig object.
    """

    EVALSCRIPT_B4_B8_B11 = """
        //VERSION=3
        function setup() {
            return {
                input: ["B04", "B08", "B11", "dataMask"],
                output: { bands: 4, sampleType: "UINT16" }
            };
        }
        function evaluatePixel(sample) {
            return [sample.B04, sample.B08, sample.B11, sample.dataMask];
        }
    """

    def __init__(self, config: SHConfig):
        """
        Initializes the data loader with a validated Sentinel Hub config object.

        Args:
            config: A validated SHConfig object containing the necessary
                    authentication credentials (client_id and client_secret).
        """
        if not isinstance(config, SHConfig):
            raise TypeError("SentinelDataLoader must be initialized with a SHConfig object.")
        self.config = config

    def fetch_bands(
        self,
        bbox: Tuple[float, float, float, float],
        image_size: Tuple[int, int],
        time_interval: Tuple[str, str] = ("2025-05-01", "2025-06-30"),
    ) -> Optional[Dict[str, np.ndarray]]:
        """
        Fetches B04, B08, B11 bands and the data mask for a given area and time.

        Args:
            bbox: A tuple representing the bounding box in WGS84 CRS
                  (min_lon, min_lat, max_lon, max_lat).
            image_size: A tuple representing the output image size (width, height).
            time_interval: A tuple of strings for the start and end date.

        Returns:
            A dictionary mapping band names to their NumPy arrays, or None if
            the request fails.
        """
        try:
            sentinel_bbox = BBox(bbox=bbox, crs=CRS.WGS84)

            request = SentinelHubRequest(
                evalscript=self.EVALSCRIPT_B4_B8_B11,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=time_interval,
                        mosaicking_order="leastCC",
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=sentinel_bbox,
                size=image_size,
                config=self.config,  # Use the provided config object
            )

            print(f"Requesting data for bbox {bbox} at {image_size} resolution...")
            bands_data = request.get_data()[0]
            print("Data received successfully.")

            return {
                "B04": bands_data[:, :, 0],
                "B08": bands_data[:, :, 1],
                "B11": bands_data[:, :, 2],
                "dataMask": bands_data[:, :, 3],
            }
        except Exception as e:
            print(f"An error occurred while fetching Sentinel Hub data: {e}")
            return None