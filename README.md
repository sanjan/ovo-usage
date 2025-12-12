# ☀️ OVO Energy Solar Dashboard

A web dashboard for analyzing electricity data exported from [OVO Energy Australia](https://www.ovoenergy.com.au/). Visualize your grid import during daytime vs night hours, simulate battery scenarios, and get personalized battery recommendations with ROI analysis.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- 📊 **Interactive Charts** - Powered by Plotly.js with synced zoom across time-series
- ☀️ **Smart Daytime Detection** - Uses actual solar generation data (not astronomical sunrise/sunset)
- 🔋 **Battery Simulation** - "What If?" chart with seasonal SOC breakdown (Summer vs Winter)
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

> ⚠️ **Recommended: At least 12 months of solar data** for accurate battery recommendations. This ensures seasonal variations (summer vs winter solar generation and consumption) are captured.

## Key Terms

| Term | Meaning |
|------|---------|
| **Daytime Grid Import** | Electricity bought from grid while solar is generating |
| **Night Grid Import** | Electricity bought from grid when solar isn't generating |
| **Solar Export** | Electricity sent back to the grid |

## Battery Recommendations

The dashboard uses **pragmatic percentile-based** recommendations with **8 kWh module increments** (Sigenergy standard):

| Recommendation | Criteria |
|----------------|----------|
| **Entry Level** | Covers 90th percentile of summer nights |
| **Best Value** ⭐ | Covers 99th percentile of summer nights |
| **Winter Ready** | Covers 90th percentile of winter nights |

Key assumptions:
- **97% usable capacity** (Sigenergy SigenStor actual)
- **$540/kWh** default battery cost (Sigenergy pricing)
- **Australian seasons**: Summer = Dec-Feb, Winter = Jun-Aug

## Battery Simulation

The "🔋 Battery Simulation - What If?" chart shows:
- Original vs simulated night grid import (with battery)
- Original vs simulated solar export (after charging battery)
- Battery state of charge over time (with daily carryover!)
- Stats: grid reduction %, self-consumed kWh
- **Seasonal SOC**: Average battery level for ☀️ Summer vs ❄️ Winter

Select different battery sizes (8-80 kWh) to see how they'd perform with your actual usage data.

**Pro tip**: Zoom on one chart and both time-series charts sync automatically!

## ROI Analysis

Configure your actual OVO rates to calculate payback:

| Input | Default | Description |
|-------|---------|-------------|
| **Peak Rate** | 33c | What you pay during peak hours (c/kWh) |
| **Off-Peak Rate** | 16c | What you pay during off-peak (c/kWh) |
| **Feed-in Tariff** | 5c | What OVO pays you for exports (c/kWh) |
| **Battery Cost** | $540 | Installed cost per kWh (Sigenergy pricing) |

Optional: **Free Power Window** - If your plan includes free electricity during certain hours (e.g., 11am-2pm), configure it to exclude from calculations.

## Charts & Analysis

- **7-Day Rolling Average / Daily Values** - Toggle between smoothed trends and raw data
- **Battery Simulation** - Interactive "What If?" analysis with battery size selector
- **Hourly Pattern** - See when you import power throughout the day
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
- **Sunrise/Sunset**: [Astral](https://github.com/sffjunkie/astral) (for daylight hours chart only)
- **Postcodes**: [Matthew Proctor's Database](https://www.matthewproctor.com/australian_postcodes)

## License

MIT License

## Acknowledgments

- [OVO Energy Australia](https://www.ovoenergy.com.au/) - Energy provider
- [Sigenergy](https://www.sigenergy.com/) - Battery pricing and efficiency data
- [Matthew Proctor](https://www.matthewproctor.com/australian_postcodes) - Australian postcode database
- [Astral](https://github.com/sffjunkie/astral) - Sunrise/sunset calculations
- [Plotly.js](https://plotly.com/javascript/) - Interactive charts
