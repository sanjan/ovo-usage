# ☀️ OVO Energy Solar Dashboard

A web dashboard for analyzing electricity usage data exported from [OVO Energy Australia](https://www.ovoenergy.com.au/). Visualize your consumption during sunlight vs night hours and get personalized home battery capacity recommendations.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- 📊 **Interactive Charts** - Powered by Plotly.js with zoom, pan, and hover details
- ☀️ **Sunlight Analysis** - Automatic sunrise/sunset calculation for your location
- 🔋 **Battery Recommendations** - Data-driven sizing based on your actual usage patterns
- 📍 **Australian Postcodes** - Full postcode database with coordinates

## Quick Start

```bash
# Clone the repository
git clone https://github.com/sanjan/ovo-usage.git
cd ovo-usage

# Install with uv
uv sync

# Run with your OVO data file
uv run solar-dashboard --file your_ovo_export.csv --postcode 3000

# Or just start the server and upload via web interface
uv run solar-dashboard
```

Then open http://127.0.0.1:5000 in your browser.

## Getting Your Data from OVO Energy

1. Log in to your [OVO Energy account](https://my.ovoenergy.com.au/)
2. Navigate to **Usage** → **Download Usage Data**
3. Select your date range and download the CSV file
4. The file will be named like `OVOEnergy-Elec-XXXXXXXX-UsageData-DD-MM-YYYY-XXXXXXXX.csv`

> ⚠️ **Recommended: At least 12 months of solar data** for accurate battery recommendations. This ensures seasonal variations (summer vs winter solar generation and consumption) are captured for reliable sizing guidance.

## OVO Energy CSV Format

This dashboard **only works with OVO Energy Australia export files**. The expected format:

| Column | Description | Example |
|--------|-------------|---------|
| `AccountNumber` | Your OVO account number | `30128980` |
| `NMI` | National Metering Identifier | `63060932424` |
| `Register` | `001` = grid consumption, `002` = solar export | `001` |
| `ReadConsumption` | Energy in kWh | `0.123` |
| `SolarFlag` | `true` for solar export readings | `false` |
| `ReadUnit` | Unit of measurement | `kWh` |
| `ReadQuality` | Data quality indicator | `A` |
| `ReadDate` | Date (YYYY-MM-DD) | `2024-05-07` |
| `ReadTime` | Time (HH:MM:SS) | `00:05:00` |

**Sample data:**
```csv
AccountNumber,NMI,Register,ReadConsumption,SolarFlag,ReadUnit,ReadQuality,ReadDate,ReadTime
30128980,63060932424,"001",0.12300,false,kWh,A,2024-05-07,00:00:00
30128980,63060932424,"001",0.12100,false,kWh,A,2024-05-07,00:05:00
30128980,63060932424,"002",1.23400,true,kWh,A,2024-05-07,12:00:00
```

Data is recorded in **5-minute intervals**.

## CLI Options

```
usage: solar-dashboard [-h] [-f FILE] [-p POSTCODE] [--port PORT] [--host HOST] [--debug]

options:
  -f FILE, --file FILE  Path to OVO Energy CSV file
  -p POSTCODE, --postcode POSTCODE
                        Australian postcode for location (e.g., 3000 for Melbourne)
  --port PORT           Port to run the server on (default: 5000)
  --host HOST           Host to bind to (default: 127.0.0.1)
  --debug               Run in debug mode
```

**Examples:**
```bash
# Start with a CSV file
solar-dashboard --file OVOEnergy-Elec-30128980-UsageData.csv

# Start with file and location
solar-dashboard --file energy_data.csv --postcode 3000

# Custom port
solar-dashboard --port 8080
```

## Battery Recommendations

The dashboard analyzes your usage patterns to recommend optimal battery sizes:

- **Minimum** - Covers your average nightly consumption
- **Sweet Spot** - Best value based on diminishing returns analysis
- **Maximum** - Covers 90th percentile nights for near-complete grid independence

Factors considered:
- Average and peak night consumption
- Daily solar export amounts (what could be stored)
- Seasonal variation
- 90% round-trip battery efficiency

## Project Structure

```
ovo-usage/
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── solar_dashboard/        # Main package
│   ├── app.py              # Flask application
│   ├── postcodes.py        # Australian postcode lookup
│   └── templates/
│       └── index.html      # Dashboard UI
└── data/
    └── australian_postcodes.csv
```

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run in debug mode
uv run solar-dashboard --debug

# Run linting
uv run ruff check .
```

## Tech Stack

- **Backend**: Flask, Pandas, NumPy
- **Frontend**: Vanilla JS, Plotly.js
- **Sunrise/Sunset**: [Astral](https://github.com/sffjunkie/astral)
- **Postcodes**: [Matthew Proctor's Database](https://www.matthewproctor.com/australian_postcodes)

## License

MIT License

## Acknowledgments

- [OVO Energy Australia](https://www.ovoenergy.com.au/) - Energy provider
- [Matthew Proctor](https://www.matthewproctor.com/australian_postcodes) - Australian postcode database
- [Astral](https://github.com/sffjunkie/astral) - Sunrise/sunset calculations
- [Plotly.js](https://plotly.com/javascript/) - Interactive charts
