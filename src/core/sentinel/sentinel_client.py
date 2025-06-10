import requests
from typing import List
import json 

class SentinelHubClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self._get_token()

    def _get_token(self) -> str:
        response = requests.post(
            "https://services.sentinel-hub.com/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def download_ndvi_image(self, bbox: List[float], time_interval: str, width=512, height=512) -> bytes:
        headers = {"Authorization": f"Bearer {self.token}"}

        evalscript = (
            "//VERSION=3\n"
            "function setup() {\n"
            "  return {\n"
            "    input: [\"B04\", \"B08\"],\n"
            "    output: { bands: 1, sampleType: \"FLOAT32\" }\n"
            "  };\n"
            "}\n"
            "function evaluatePixel(sample) {\n"
            "  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);\n"
            "  return [ndvi];\n"
            "}"
        )

        payload = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {
                        "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                    }
                },
                "data": [
                    {
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": f"{time_interval.split('/')[0]}T00:00:00Z",
                                "to": f"{time_interval.split('/')[1]}T23:59:59Z"
                            }
                        }
                    }
                ]
            },
            "output": {
                "width": width,
                "height": height,
                "responses": [
                    {
                        "identifier": "default",
                        "format": {"type": "image/png"}
                    }
                ]
            },
            "evalscript": evalscript
        }

        print("\n=== SENT PAYLOAD TO API ===")
        print(json.dumps(payload, indent=2))
        print("===========================\n")

        response = requests.post(
            "https://services.sentinel-hub.com/api/v1/process",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.content