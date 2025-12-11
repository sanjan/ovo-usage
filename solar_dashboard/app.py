#!/usr/bin/env python3
"""
Solar Energy Dashboard - Web Application

Interactive visualization of electricity usage during sunlight vs non-sunlight hours
for Australian households with solar panels.
"""

import argparse
import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request, session
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from astral import LocationInfo
from astral.sun import sun
import tempfile

from .postcodes import lookup_postcode, search_locations, MAJOR_CITIES, Location

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Global state for CLI-provided file
_cli_data_file: str | None = None
_cli_location: Location | None = None

# Cache for processed data
_data_cache: dict = {}


def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_location() -> Location:
    """Get the current location from session, CLI, or default."""
    # Check session first
    if 'location' in session:
        loc = session['location']
        return Location(
            postcode=loc['postcode'],
            locality=loc['locality'],
            state=loc['state'],
            latitude=loc['latitude'],
            longitude=loc['longitude']
        )
    
    # Then CLI
    if _cli_location:
        return _cli_location
    
    # Default to Melbourne
    return MAJOR_CITIES['melbourne']


def get_location_info(location: Location) -> LocationInfo:
    """Create astral LocationInfo from our Location."""
    # Determine timezone based on state
    timezones = {
        'NSW': 'Australia/Sydney',
        'VIC': 'Australia/Melbourne',
        'QLD': 'Australia/Brisbane',
        'SA': 'Australia/Adelaide',
        'WA': 'Australia/Perth',
        'TAS': 'Australia/Hobart',
        'NT': 'Australia/Darwin',
        'ACT': 'Australia/Sydney',
    }
    tz = timezones.get(location.state, 'Australia/Melbourne')
    
    return LocationInfo(
        location.locality,
        "Australia",
        tz,
        location.latitude,
        location.longitude
    )


def get_sun_times(date, location: Location):
    """Get sunrise and sunset times for a location on a given date."""
    loc_info = get_location_info(location)
    s = sun(loc_info.observer, date=date, tzinfo=loc_info.timezone)
    return s['sunrise'].replace(tzinfo=None), s['sunset'].replace(tzinfo=None)


def is_sunlight_hour(dt, location: Location) -> bool:
    """Check if a datetime falls within sunlight hours."""
    sunrise, sunset = get_sun_times(dt.date(), location)
    return sunrise.time() <= dt.time() <= sunset.time()


def get_data_file() -> str | None:
    """Get the current data file path."""
    # Check session first (uploaded file)
    if 'data_file' in session and os.path.exists(session['data_file']):
        return session['data_file']
    
    # Then CLI argument
    if _cli_data_file:
        return _cli_data_file
    
    return None


def load_and_process_data(filepath: str, location: Location):
    """Load and process energy data."""
    cache_key = f"{filepath}_{location.postcode}"
    
    if cache_key in _data_cache:
        return _data_cache[cache_key]
    
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    
    # Combine date and time into datetime
    df['datetime'] = pd.to_datetime(df['ReadDate'] + ' ' + df['ReadTime'])
    df['date'] = pd.to_datetime(df['ReadDate']).dt.date
    
    # Find first solar export date
    solar_exports = df[(df['Register'] == 2) & (df['SolarFlag'] == True)]
    non_zero_exports = solar_exports[solar_exports['ReadConsumption'] > 0]
    
    if len(non_zero_exports) == 0:
        raise ValueError("No solar exports found in data! Make sure the file contains Register=2 entries with SolarFlag=True.")
    
    solar_start = non_zero_exports['date'].min()
    print(f"Solar start date: {solar_start}")
    
    # Filter data from solar start date onwards
    df_filtered = df[df['date'] >= solar_start].copy()
    
    # Separate consumption and export
    consumption = df_filtered[df_filtered['Register'] == 1].copy()
    exports = df_filtered[(df_filtered['Register'] == 2) & (df_filtered['SolarFlag'] == True)].copy()
    
    # Calculate sunlight status
    print(f"Calculating sunlight hours for {location.display_name}...")
    consumption['is_sunlight'] = consumption['datetime'].apply(lambda dt: is_sunlight_hour(dt, location))
    exports['is_sunlight'] = exports['datetime'].apply(lambda dt: is_sunlight_hour(dt, location))
    
    result = {
        'consumption': consumption,
        'exports': exports,
        'solar_start': solar_start
    }
    
    _data_cache[cache_key] = result
    print("Data processing complete!")
    return result


def get_summary_stats(consumption, exports):
    """Calculate summary statistics."""
    sunlight_consumption = consumption[consumption['is_sunlight']]['ReadConsumption'].sum()
    night_consumption = consumption[~consumption['is_sunlight']]['ReadConsumption'].sum()
    total_consumption = consumption['ReadConsumption'].sum()
    
    sunlight_exports = exports[exports['is_sunlight']]['ReadConsumption'].sum()
    total_exports = exports['ReadConsumption'].sum()
    
    num_days = len(consumption['date'].unique())
    
    return {
        'sunlight_consumption': round(sunlight_consumption, 2),
        'night_consumption': round(night_consumption, 2),
        'total_consumption': round(total_consumption, 2),
        'sunlight_exports': round(sunlight_exports, 2),
        'total_exports': round(total_exports, 2),
        'num_days': num_days,
        'avg_daily_consumption': round(total_consumption / num_days, 2),
        'avg_daily_export': round(total_exports / num_days, 2),
        'sunlight_pct': round(100 * sunlight_consumption / total_consumption, 1),
        'night_pct': round(100 * night_consumption / total_consumption, 1)
    }


def calculate_battery_recommendation(consumption, exports):
    """Calculate optimal battery capacity recommendation based on usage patterns."""
    import numpy as np
    
    # Daily aggregations
    daily_night = consumption[~consumption['is_sunlight']].groupby('date')['ReadConsumption'].sum()
    daily_export = exports.groupby('date')['ReadConsumption'].sum()
    
    # Align indices
    all_dates = daily_night.index
    daily_export = daily_export.reindex(all_dates, fill_value=0)
    
    # Core metrics
    avg_night_consumption = daily_night.mean()
    median_night_consumption = daily_night.median()
    p75_night_consumption = daily_night.quantile(0.75)
    p90_night_consumption = daily_night.quantile(0.90)
    max_night_consumption = daily_night.max()
    
    avg_daily_export = daily_export.mean()
    median_daily_export = daily_export.median()
    p75_daily_export = daily_export.quantile(0.75)
    
    # Potential storage
    potential_storage = daily_export.combine(daily_night, min)
    avg_potential_storage = potential_storage.mean()
    
    # Seasonal analysis
    consumption['month'] = consumption['datetime'].dt.month
    exports['month'] = exports['datetime'].dt.month
    
    winter_months = [5, 6, 7, 8]
    summer_months = [11, 12, 1, 2]
    
    winter_consumption = consumption[consumption['month'].isin(winter_months)]
    summer_consumption = consumption[consumption['month'].isin(summer_months)]
    winter_exports = exports[exports['month'].isin(winter_months)]
    summer_exports = exports[exports['month'].isin(summer_months)]
    
    winter_night_avg = (
        winter_consumption[~winter_consumption['is_sunlight']]
        .groupby('date')['ReadConsumption'].sum().mean()
        if len(winter_consumption) > 0 else avg_night_consumption
    )
    summer_night_avg = (
        summer_consumption[~summer_consumption['is_sunlight']]
        .groupby('date')['ReadConsumption'].sum().mean()
        if len(summer_consumption) > 0 else avg_night_consumption
    )
    winter_export_avg = (
        winter_exports.groupby('date')['ReadConsumption'].sum().mean()
        if len(winter_exports) > 0 else avg_daily_export
    )
    summer_export_avg = (
        summer_exports.groupby('date')['ReadConsumption'].sum().mean()
        if len(summer_exports) > 0 else avg_daily_export
    )
    
    # Battery efficiency
    battery_efficiency = 0.90
    
    # Sizing recommendations
    min_battery = avg_night_consumption / battery_efficiency
    usable_export = min(avg_daily_export, p75_night_consumption)
    recommended_battery = max(usable_export, median_night_consumption) / battery_efficiency
    optimal_battery = min(p90_night_consumption, p75_daily_export) / battery_efficiency
    large_battery = p90_night_consumption / battery_efficiency
    
    # Common battery sizes
    battery_sizes = [5, 7, 10, 13.5, 15, 20]
    
    def find_nearest_size(target):
        return min(battery_sizes, key=lambda x: abs(x - target))
    
    def calculate_savings(battery_kwh):
        usable_capacity = battery_kwh * battery_efficiency
        savings_per_day = []
        for date in all_dates:
            export_available = daily_export.get(date, 0)
            night_usage = daily_night.get(date, 0)
            stored = min(export_available, usable_capacity)
            offset = min(stored, night_usage)
            savings_per_day.append(offset)
        
        total_savings = sum(savings_per_day)
        coverage_pct = (total_savings / daily_night.sum()) * 100 if daily_night.sum() > 0 else 0
        
        return {
            'total_kwh_saved': round(total_savings, 1),
            'avg_daily_savings': round(np.mean(savings_per_day), 2),
            'night_coverage_pct': round(coverage_pct, 1)
        }
    
    battery_analysis = [{'size_kwh': size, **calculate_savings(size)} for size in battery_sizes]
    
    # Marginal benefits
    marginal_benefits = []
    for i in range(1, len(battery_analysis)):
        prev, curr = battery_analysis[i-1], battery_analysis[i]
        size_increase = curr['size_kwh'] - prev['size_kwh']
        savings_increase = curr['avg_daily_savings'] - prev['avg_daily_savings']
        marginal_benefits.append({
            'from_size': prev['size_kwh'],
            'to_size': curr['size_kwh'],
            'marginal_benefit': round(savings_increase / size_increase, 3) if size_increase > 0 else 0
        })
    
    # Find sweet spot
    sweet_spot_idx = 0
    for i, mb in enumerate(marginal_benefits):
        if i > 0 and mb['marginal_benefit'] < marginal_benefits[i-1]['marginal_benefit'] * 0.5:
            sweet_spot_idx = i
            break
        sweet_spot_idx = i
    sweet_spot_size = battery_sizes[min(sweet_spot_idx + 1, len(battery_sizes) - 1)]
    
    return {
        'metrics': {
            'avg_night_consumption': round(avg_night_consumption, 2),
            'median_night_consumption': round(median_night_consumption, 2),
            'p75_night_consumption': round(p75_night_consumption, 2),
            'p90_night_consumption': round(p90_night_consumption, 2),
            'max_night_consumption': round(max_night_consumption, 2),
            'avg_daily_export': round(avg_daily_export, 2),
            'median_daily_export': round(median_daily_export, 2),
            'avg_potential_storage': round(avg_potential_storage, 2),
            'winter_night_avg': round(winter_night_avg, 2),
            'summer_night_avg': round(summer_night_avg, 2),
            'winter_export_avg': round(winter_export_avg, 2),
            'summer_export_avg': round(summer_export_avg, 2),
        },
        'recommendations': {
            'minimum_kwh': round(min_battery, 1),
            'recommended_kwh': round(recommended_battery, 1),
            'optimal_kwh': round(optimal_battery, 1),
            'maximum_kwh': round(large_battery, 1),
            'sweet_spot_kwh': sweet_spot_size,
            'nearest_minimum': find_nearest_size(min_battery),
            'nearest_recommended': find_nearest_size(recommended_battery),
            'nearest_optimal': find_nearest_size(optimal_battery),
        },
        'battery_analysis': battery_analysis,
        'marginal_benefits': marginal_benefits,
        'efficiency_assumed': battery_efficiency
    }


# ============== Routes ==============

@app.route('/')
def index():
    """Main dashboard page."""
    has_data = get_data_file() is not None
    location = get_location()
    return render_template('index.html', has_data=has_data, location=location.to_dict())


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"energy_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
    file.save(filepath)
    
    # Store in session
    session['data_file'] = filepath
    
    # Clear cache for fresh processing
    _data_cache.clear()
    
    return jsonify({'success': True, 'filename': filename})


@app.route('/api/location', methods=['POST'])
def set_location():
    """Set location by postcode."""
    data = request.get_json()
    postcode = data.get('postcode', '').strip()
    
    if not postcode:
        return jsonify({'error': 'No postcode provided'}), 400
    
    location = lookup_postcode(postcode)
    if not location:
        return jsonify({'error': f'Postcode {postcode} not found'}), 404
    
    session['location'] = location.to_dict()
    
    # Clear cache since location changed
    _data_cache.clear()
    
    return jsonify({'success': True, 'location': location.to_dict()})


@app.route('/api/search-locations')
def search_locations_api():
    """Search for locations by postcode or suburb name."""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    results = search_locations(query, limit=15)
    return jsonify(results)


@app.route('/api/status')
def get_status():
    """Get current status (has data, location)."""
    data_file = get_data_file()
    location = get_location()
    
    return jsonify({
        'has_data': data_file is not None,
        'data_file': os.path.basename(data_file) if data_file else None,
        'location': location.to_dict()
    })


@app.route('/api/data')
def get_data():
    """API endpoint to get all chart data."""
    data_file = get_data_file()
    if not data_file:
        return jsonify({'error': 'No data file loaded. Please upload a CSV file.'}), 400
    
    location = get_location()
    
    try:
        data = load_and_process_data(data_file, location)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    consumption = data['consumption']
    exports = data['exports']
    
    # Summary stats
    stats = get_summary_stats(consumption, exports)
    stats['solar_start'] = str(data['solar_start'])
    stats['location'] = location.to_dict()
    
    # Daily data
    daily_sunlight = consumption[consumption['is_sunlight']].groupby('date')['ReadConsumption'].sum()
    daily_night = consumption[~consumption['is_sunlight']].groupby('date')['ReadConsumption'].sum()
    daily_export = exports.groupby('date')['ReadConsumption'].sum()
    
    daily_data = {
        'dates': [str(d) for d in daily_sunlight.index],
        'sunlight': daily_sunlight.round(2).tolist(),
        'night': daily_night.reindex(daily_sunlight.index, fill_value=0).round(2).tolist(),
        'export': daily_export.reindex(daily_sunlight.index, fill_value=0).round(2).tolist()
    }
    
    # Hourly patterns
    consumption['hour'] = consumption['datetime'].dt.hour
    exports['hour'] = exports['datetime'].dt.hour
    
    hourly_consumption = consumption.groupby('hour')['ReadConsumption'].mean()
    hourly_export = exports.groupby('hour')['ReadConsumption'].mean()
    
    hourly_data = {
        'hours': list(range(24)),
        'consumption': [round(hourly_consumption.get(h, 0), 4) for h in range(24)],
        'export': [round(hourly_export.get(h, 0), 4) for h in range(24)]
    }
    
    # Monthly data
    consumption['month'] = consumption['datetime'].dt.to_period('M').astype(str)
    exports['month'] = exports['datetime'].dt.to_period('M').astype(str)
    
    monthly_sunlight = consumption[consumption['is_sunlight']].groupby('month')['ReadConsumption'].sum()
    monthly_night = consumption[~consumption['is_sunlight']].groupby('month')['ReadConsumption'].sum()
    monthly_export = exports.groupby('month')['ReadConsumption'].sum()
    
    all_months = sorted(set(monthly_sunlight.index) | set(monthly_night.index) | set(monthly_export.index))
    
    monthly_data = {
        'months': all_months,
        'sunlight': [round(monthly_sunlight.get(m, 0), 2) for m in all_months],
        'night': [round(monthly_night.get(m, 0), 2) for m in all_months],
        'export': [round(monthly_export.get(m, 0), 2) for m in all_months]
    }
    
    # Rolling averages
    rolling_sunlight = daily_sunlight.rolling(7).mean().dropna()
    rolling_night = daily_night.reindex(daily_sunlight.index, fill_value=0).rolling(7).mean().dropna()
    rolling_export = daily_export.reindex(daily_sunlight.index, fill_value=0).rolling(7).mean().dropna()
    
    trend_data = {
        'dates': [str(d) for d in rolling_sunlight.index],
        'sunlight': rolling_sunlight.round(2).tolist(),
        'night': rolling_night.round(2).tolist(),
        'export': rolling_export.round(2).tolist()
    }
    
    # Battery recommendations
    battery_rec = calculate_battery_recommendation(consumption, exports)
    
    return jsonify({
        'stats': stats,
        'daily': daily_data,
        'hourly': hourly_data,
        'monthly': monthly_data,
        'trends': trend_data,
        'battery': battery_rec
    })


def main():
    """Main entry point with CLI argument parsing."""
    global _cli_data_file, _cli_location
    
    parser = argparse.ArgumentParser(
        description='Solar Energy Dashboard - Analyze your solar usage patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with a CSV file
  solar-dashboard --file energy_data.csv

  # Start with file and location
  solar-dashboard --file energy_data.csv --postcode 3000

  # Just start the server (upload via web interface)
  solar-dashboard

  # Custom port
  solar-dashboard --port 8080
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Path to OVO Energy CSV file'
    )
    
    parser.add_argument(
        '-p', '--postcode',
        type=str,
        help='Australian postcode for location (e.g., 3000 for Melbourne)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the server on (default: 5000)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )
    
    args = parser.parse_args()
    
    # Handle file argument
    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        _cli_data_file = str(filepath.absolute())
        print(f"📁 Using data file: {_cli_data_file}")
    
    # Handle postcode argument
    if args.postcode:
        location = lookup_postcode(args.postcode)
        if not location:
            print(f"Error: Postcode {args.postcode} not found", file=sys.stderr)
            sys.exit(1)
        _cli_location = location
        print(f"📍 Location: {location.display_name} ({location.latitude}, {location.longitude})")
    else:
        _cli_location = MAJOR_CITIES['melbourne']
        print(f"📍 Default location: Melbourne, VIC")
    
    print(f"\n🌞 Starting Solar Energy Dashboard...")
    print(f"   Open http://{args.host}:{args.port} in your browser\n")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()

