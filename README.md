# Sentinel Parallel Processor

## Overview

A parallel processing system for analyzing vegetation changes using Sentinel-2 satellite imagery, enabling efficient calculation of NDVI and NDMI indices with a user-friendly GUI interface.

## Project Structure

```
sentinel_parallel_processor/
├── src/                    # Source code directory
│   ├── core/              # Core processing modules
│   │   ├── data_loader/   # Data acquisition and preprocessing
│   │   ├── processing/    # Parallel processing implementation
│   │   └── analysis/      # Data analysis and calculations
│   ├── gui/               # GUI implementation
│   │   ├── views/         # GUI views and windows
│   │   ├── widgets/       # Custom GUI widgets
│   │   └── resources/     # GUI resources (icons, styles)
│   └── utils/             # Utility functions and helpers
├── tests/                 # Test directory
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── data/             # Test data
├── data/                  # Data storage
│   ├── raw/              # Raw Sentinel-2 data
│   ├── processed/        # Processed data
│   └── results/          # Analysis results
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   └── user_guide/       # User documentation
├── config/               # Configuration files
├── logs/                 # Application logs
└── scripts/              # Utility scripts
```

## Features

- Parallel processing of Sentinel-2 satellite imagery
- NDVI and NDMI index calculations
- Interactive visualization of vegetation changes
- User-friendly GUI interface
- Export capabilities for analysis results

## Tech Stack

- Python 3.8+
- Rasterio/GDAL for geospatial data processing
- NumPy for numerical computations
- PyQt6 for GUI implementation
- Matplotlib for data visualization
- multiprocessing for parallel processing

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `config/config.yaml`
4. Run the application: `python src/main.py`

## Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
