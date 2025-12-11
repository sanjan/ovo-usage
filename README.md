# ☀️ OVO Energy Solar Dashboard

A web dashboard for analyzing electricity usage data exported from [OVO Energy Australia](https://www.ovoenergy.com.au/). Visualize your consumption during sunlight vs night hours and get personalized home battery capacity recommendations with ROI analysis.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- 📊 **Interactive Charts** - Powered by Plotly.js with zoom, pan, and hover details
- ☀️ **Smart Sunlight Detection** - Uses actual solar generation data (not astronomical sunrise/sunset)
- 🔋 **Battery Recommendations** - Coverage-based sizing for summer and winter
- 💰 **ROI Analysis** - Calculate payback period with your actual OVO rates
- 🆓 **Free Power Window** - Configure your free electricity period (e.g., 11am-2pm)
- 📅 **Date Range Selection** - Analyze specific periods (auto-suggests 1-year range)
- 🌡️ **Seasonal Analysis** - Compare winter vs summer patterns
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

Data is recorded in **5-minute intervals**.

## Battery Recommendations

The dashboard uses **seasonal coverage-based** recommendations:

| Recommendation | Criteria |
|----------------|----------|
| **Minimum** | Covers ≥70% of summer nights |
| **Sweet Spot** ⭐ | Covers 100% of summer nights |
| **Maximum** | Covers ≥30% of winter nights |

This approach accounts for:
- Higher consumption in winter (heating)
- Lower solar generation in winter
- 90% round-trip battery efficiency

## ROI Analysis

Configure your actual OVO rates to calculate payback:

| Input | Description |
|-------|-------------|
| **Peak Rate** | What you pay during peak hours (c/kWh) |
| **Off-Peak Rate** | What you pay during off-peak (c/kWh) |
| **Feed-in Tariff** | What OVO pays you for exports (c/kWh) |
| **Battery Cost** | Installed cost per kWh ($/kWh) |

Optional: **Free Power Window** - If your plan includes free electricity during certain hours (e.g., 11am-2pm), configure it to exclude from calculations.

## Charts & Analysis

- **7-Day Rolling Average / Daily Values** - Toggle between smoothed trends and raw data
- **Hourly Usage Pattern** - See when you use power throughout the day
- **Monthly Breakdown** - Track seasonal patterns
- **Daylight vs Generation Hours** - Compare theoretical daylight to actual panel output
- **Battery Size vs Coverage** - Visualize diminishing returns
- **Cumulative Savings** - Project ROI over 10 years

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

## Project Structure

```
ovo-usage/
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── agents.md               # AI agent instructions
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
- **Sunrise/Sunset**: [Astral](https://github.com/sffjunkie/astral) (for daylight hours chart)
- **Postcodes**: [Matthew Proctor's Database](https://www.matthewproctor.com/australian_postcodes)

## License

MIT License

## Acknowledgments

- [OVO Energy Australia](https://www.ovoenergy.com.au/) - Energy provider
- [Matthew Proctor](https://www.matthewproctor.com/australian_postcodes) - Australian postcode database
- [Astral](https://github.com/sffjunkie/astral) - Sunrise/sunset calculations
- [Plotly.js](https://plotly.com/javascript/) - Interactive charts
