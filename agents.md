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

**OVO Energy Solar Dashboard** is a Flask web application that analyzes electricity grid import data exported from OVO Energy Australia. It calculates when energy is drawn from the grid during daytime vs night hours and provides battery capacity recommendations with ROI analysis.

## Key Concepts

### Terminology
- **Daytime Grid Import**: Electricity bought from grid during solar generation hours
- **Night Grid Import**: Electricity bought from grid when solar isn't generating
- **Solar Export**: Electricity sent back to the grid

### Energy Data
- **Register 1 (001)**: Grid import (electricity drawn from grid)
- **Register 2 (002) + SolarFlag=True**: Solar export (electricity sent to grid)
- Data is in 5-minute intervals with ReadDate and ReadTime columns
- Analysis starts from the first day with actual solar exports (non-zero Register 2 readings)
- **Recommended: At least 12 months of data** for accurate battery recommendations

### Sunlight Detection
- **Data-driven approach**: Uses actual solar generation data, not astronomical sunrise/sunset
- A timestamp is "daytime" if solar export > 0.001 kWh at that time
- More accurate because it accounts for panel orientation, shading, weather, inverter behavior

### Free Power Window
- OVO offers free power during certain hours (default: 11am-2pm)
- Grid import during this window is excluded from calculations
- Configurable via UI - users can enable/disable and set custom times

### Battery Sizing Logic
Pragmatic percentile-based recommendations using **8 kWh module increments** (Sigenergy standard):
- **Entry Level**: Smallest battery whose usable capacity covers 90th percentile summer nights
- **Best Value**: Smallest battery whose usable capacity covers 99th percentile summer nights
- **Winter Ready**: Smallest battery whose usable capacity covers 90th percentile winter nights

Key settings:
- `battery_efficiency = 0.97` (Sigenergy SigenStor actual usable capacity)
- `battery_sizes = [8, 16, 24, 32, 40, 48, 56, 64, 72, 80]` (8 kWh module increments)
- Australian seasons: Summer = Dec-Feb, Winter = Jun-Aug

### Battery Simulation
The "What If?" simulation chart shows:
- Original vs simulated night grid import
- Original vs simulated solar export
- Battery state of charge (SOC) with daily carryover
- Stats: grid reduction %, export reduction %, self-consumed kWh

### ROI Analysis
- Default battery cost: $540/kWh (Sigenergy pricing)
- Users input their actual OVO rates (peak, off-peak, feed-in)
- Calculates payback period and 10-year cumulative savings

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
| `load_and_process_data()` | Load CSV, determine daytime status from actual solar generation |
| `filter_data_by_date_range()` | Filter data to user-selected analysis period |
| `get_summary_stats()` | Aggregate grid import/export statistics |
| `calculate_battery_recommendation()` | Percentile-based battery sizing |
| `calculate_daylight_hours()` | Compare theoretical daylight vs actual generation |

### Key Functions in `index.html` (JavaScript)

| Function | Purpose |
|----------|---------|
| `simulateBattery()` | Simulate battery charging/discharging with daily carryover |
| `renderBatterySimulation()` | Render "What If?" chart with battery size selector |
| `renderTrendsChart()` | 7-day rolling average or daily values chart |

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
- `battery_efficiency = 0.97` - Sigenergy usable capacity ratio
- `battery_sizes = [8, 16, 24, 32, ...]` - 8 kWh module increments
- Find smallest battery whose `size * efficiency >= target_usage`

## Dependencies

Core:
- `flask` - Web framework
- `pandas` - Data processing
- `astral` - Sunrise/sunset calculations (for daylight hours chart only)
- `numpy` - Numerical operations

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
- **Be pragmatic**: Don't over-buy batteries, recommend module-based sizes

## Running Locally

```bash
# With uv
uv run solar-dashboard --file data.csv --postcode 3000 --debug

# With pip
python -m solar_dashboard.app --file data.csv --postcode 3000 --debug
```
