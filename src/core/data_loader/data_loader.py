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
    Handles fetching analytical bands (B04, B08, B11) and the data mask.
    """

    EVALSCRIPT_BANDS = """
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
        if not isinstance(config, SHConfig):
            raise TypeError(
                "SentinelDataLoader must be initialized with a SHConfig object."
            )
        self.config = config

    def fetch_data(
        self,
        bbox: Tuple[float, float, float, float],
        image_size: Tuple[int, int],
        time_interval: Tuple[str, str],
    ) -> Optional[Dict[str, np.ndarray]]:
        """
        Fetches analytical bands for a given area and time.
        """
        try:
            sentinel_bbox = BBox(bbox=bbox, crs=CRS.WGS84)

            request_bands = SentinelHubRequest(
                evalscript=self.EVALSCRIPT_BANDS,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=time_interval,
                        mosaicking_order="leastCC",
                    )
                ],
                responses=[
                    SentinelHubRequest.output_response("default", MimeType.TIFF)
                ],
                bbox=sentinel_bbox,
                size=image_size,
                config=self.config,
            )
            
            print(f"Requesting analytical bands for bbox {bbox}...")
            bands_data = request_bands.get_data()[0]
            print("Analytical bands received successfully.")

            return {
                "B04": bands_data[:, :, 0],
                "B08": bands_data[:, :, 1],
                "B11": bands_data[:, :, 2],
                "dataMask": bands_data[:, :, 3],
            }
        except Exception as e:
            print(f"An error occurred while fetching Sentinel Hub data: {e}")
            raise e