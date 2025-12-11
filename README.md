# ☀️ Solar Energy Dashboard

An interactive web dashboard for analyzing solar energy usage patterns for Australian households. Visualize your electricity consumption during sunlight vs night hours and get personalized home battery capacity recommendations.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- 📊 **Interactive Charts** - Powered by Plotly.js with zoom, pan, and hover details
- ☀️ **Sunlight Analysis** - Automatic sunrise/sunset calculation for your location
- 🔋 **Battery Recommendations** - Data-driven sizing based on your actual usage patterns
- 📍 **Australian Postcodes** - Full postcode database with coordinates
- 📁 **Easy Data Import** - Upload your OVO Energy CSV or use CLI

## Screenshots

*Dashboard showing energy usage patterns and battery recommendations*

## Quick Start

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/solar-energy-dashboard.git
cd solar-energy-dashboard

# Install with uv
uv sync

# Run with a CSV file
uv run solar-dashboard --file your_energy_data.csv --postcode 3000

# Or just start the server and upload via web interface
uv run solar-dashboard
```

### Using pip

```bash
# Clone and install
git clone https://github.com/yourusername/solar-energy-dashboard.git
cd solar-energy-dashboard
pip install -e .

# Run
solar-dashboard --file your_energy_data.csv --postcode 3000
```

Then open http://127.0.0.1:5000 in your browser.

## CLI Options

```
usage: solar-dashboard [-h] [-f FILE] [-p POSTCODE] [--port PORT] [--host HOST] [--debug]

Solar Energy Dashboard - Analyze your solar usage patterns

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to OVO Energy CSV file
  -p POSTCODE, --postcode POSTCODE
                        Australian postcode for location (e.g., 3000 for Melbourne)
  --port PORT           Port to run the server on (default: 5000)
  --host HOST           Host to bind to (default: 127.0.0.1)
  --debug               Run in debug mode

Examples:
  # Start with a CSV file
  solar-dashboard --file energy_data.csv

  # Start with file and location
  solar-dashboard --file energy_data.csv --postcode 3000

  # Just start the server (upload via web interface)
  solar-dashboard

  # Custom port
  solar-dashboard --port 8080
```

## Data Format

The dashboard expects CSV files from OVO Energy with the following columns:

| Column | Description |
|--------|-------------|
| `ReadDate` | Date of reading (YYYY-MM-DD) |
| `ReadTime` | Time of reading (HH:MM:SS) |
| `Register` | 1 = consumption, 2 = solar export |
| `SolarFlag` | true/false for solar readings |
| `ReadConsumption` | Energy in kWh |

The dashboard automatically:
- Detects when your solar system started exporting
- Filters data to only analyze post-solar-installation usage
- Calculates sunrise/sunset times for your location

## Battery Recommendations

The dashboard analyzes your usage patterns to recommend optimal battery sizes:

- **Minimum** - Covers your average nightly consumption
- **Sweet Spot** - Best value based on diminishing returns analysis
- **Maximum** - Covers 90th percentile nights for near-complete independence

Factors considered:
- Average and peak night consumption
- Daily solar export amounts
- Seasonal variation (Melbourne winters vs summers)
- 90% round-trip battery efficiency

## Location Data

Australian postcode coordinates are sourced from [Matthew Proctor's Australian Postcodes database](https://www.matthewproctor.com/australian_postcodes), which provides:

- 18,500+ postcode entries
- Latitude/longitude for each location
- State and locality information

## Project Structure

```
solar-energy-dashboard/
├── pyproject.toml          # Package configuration (uv/pip)
├── README.md               # This file
├── agents.md               # Instructions for AI agents
├── solar_dashboard/        # Main package
│   ├── __init__.py
│   ├── app.py              # Flask application
│   ├── postcodes.py        # Postcode lookup
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Matthew Proctor](https://www.matthewproctor.com/australian_postcodes) for the Australian postcode database
- [Astral](https://github.com/sffjunkie/astral) for sunrise/sunset calculations
- [Plotly.js](https://plotly.com/javascript/) for interactive charts

