# agents.md - AI Agent Instructions

This file provides context and instructions for AI agents (like Claude, Cursor, GitHub Copilot, etc.) working on this codebase.

## Philosophy

**Be pragmatic. Follow the Zen of Python:**

- Simple is better than complex
- Flat is better than nested
- Readability counts
- Practicality beats purity
- If the implementation is hard to explain, it's a bad idea
- There should be one obvious way to do it

Don't over-engineer. Solve the problem at hand, not hypothetical future problems.

## Project Overview

**OVO Energy Solar Dashboard** is a Flask web application that analyzes electricity usage data exported from OVO Energy Australia. It calculates when energy is consumed during sunlight vs night hours and provides battery capacity recommendations with ROI analysis.

## Key Concepts

### Energy Data
- **Register 1 (001)**: Grid consumption (electricity drawn from grid)
- **Register 2 (002) + SolarFlag=True**: Solar export (electricity sent to grid)
- Data is in 5-minute intervals with ReadDate and ReadTime columns
- Analysis starts from the first day with actual solar exports (non-zero Register 2 readings)
- **Recommended: At least 12 months of data** for accurate battery recommendations (captures seasonal variations)

### Sunlight Calculation
- **Data-driven approach**: Uses actual solar generation data, not astronomical sunrise/sunset
- A timestamp is "sunlight" if solar export > 0.001 kWh at that time
- More accurate than astronomical calculation because it accounts for:
  - Panel orientation (east/west facing)
  - Shading and obstructions
  - Weather conditions
  - Actual inverter behavior

### Free Power Window
- OVO offers free power during certain hours (default: 11am-2pm)
- Grid usage during this window is excluded from "usage to offset" calculations
- Configurable via UI - users can enable/disable and set custom times

### Battery Sizing Logic
Coverage-based recommendations:
- **Minimum**: Battery that covers ≥70% of summer nights
- **Sweet Spot**: Battery that covers 100% of summer nights
- **Maximum**: Battery that covers ≥30% of winter nights

This approach:
- Accounts for seasonal usage patterns (higher winter consumption)
- Uses 90% round-trip battery efficiency
- Calculates seasonal coverage for each battery size

### ROI Analysis
- Users input their actual OVO rates (peak, off-peak, feed-in)
- Calculates savings per kWh shifted from export to self-consumption
- Estimates payback period and 10-year cumulative savings

## Architecture

```
solar_dashboard/
├── app.py          # Flask routes, data processing, battery calculations
├── postcodes.py    # Australian postcode lookup with coordinates
└── templates/
    └── index.html  # Single-page app with Plotly.js charts
```

### Key Functions in `app.py`

| Function | Purpose |
|----------|---------|
| `load_and_process_data()` | Load CSV, determine sunlight status from actual solar generation |
| `filter_data_by_date_range()` | Filter data to user-selected analysis period |
| `get_summary_stats()` | Aggregate consumption/export statistics |
| `calculate_battery_recommendation()` | Seasonal coverage-based battery sizing |
| `calculate_daylight_hours()` | Compare theoretical daylight vs actual generation |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve dashboard HTML |
| `/api/upload` | POST | Handle CSV file upload |
| `/api/location` | POST | Set location by postcode |
| `/api/search-locations` | GET | Search postcodes/suburbs |
| `/api/data` | GET | Get all chart data + battery recommendations |
| `/api/status` | GET | Check if data is loaded, current location |

## Common Tasks

### Adding a New Chart

1. Add data aggregation in `/api/data` route in `app.py`
2. Add HTML container in `index.html`
3. Add render function in JavaScript section
4. Call render function in `loadData()`

### Modifying Battery Recommendations

Key parameters in `calculate_battery_recommendation()`:
- `battery_efficiency = 0.90` - Round-trip efficiency
- `battery_sizes = [5, 7, 10, 13.5, 15, 20, 25, 30, 40]` - Available sizes
- Coverage targets: 70% summer (min), 100% summer (sweet spot), 30% winter (max)

### Adding New Location Features

The `postcodes.py` module provides:
- `lookup_postcode(postcode)` → `Location` object
- `search_locations(query)` → List of matching locations
- `MAJOR_CITIES` dict for quick access to capital cities

## Dependencies

Core:
- `flask` - Web framework
- `pandas` - Data processing
- `astral` - Sunrise/sunset calculations (for daylight hours chart)
- `numpy` - Numerical operations

The postcode database (`data/australian_postcodes.csv`) is downloaded from [Matthew Proctor's database](https://www.matthewproctor.com/australian_postcodes).

## Common Issues

1. **No solar exports found**: Data doesn't have Register=2 with SolarFlag=True entries
2. **Slow loading**: Large CSV files (300k+ rows) take time to process
3. **Postcode not found**: Some LVR (Large Volume Receiver) postcodes lack coordinates

## Style Guidelines

- Python: Follow existing patterns, use type hints, keep it simple
- JavaScript: Vanilla JS, no frameworks, Plotly.js for charts
- CSS: CSS variables for theming, dark theme default
- Comments: Explain business logic, not obvious code
- **Don't over-abstract**: If a function is only used once, it might not need to be a function

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `dev-key-change-in-production` | Flask session secret |

## Running Locally

```bash
# With uv
uv run solar-dashboard --file data.csv --postcode 3000 --debug

# With pip
python -m solar_dashboard.app --file data.csv --postcode 3000 --debug
```
