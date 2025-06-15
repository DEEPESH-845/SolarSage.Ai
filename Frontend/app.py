#!/usr/bin/env python3
"""
Solar Panel Cleaning System - Flask Frontend
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'solar_panel_cleaning_system_2025'

# Configuration
BACKEND_URL = "http://localhost:8000"
API_TIMEOUT = 10

def make_api_request(endpoint, method='GET', data=None):
    """Make request to FastAPI backend with error handling"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=API_TIMEOUT)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=API_TIMEOUT)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        flash(f"API Error: {str(e)}", "error")
        return None

@app.route('/')
def dashboard():
    """Main dashboard"""
    # Get system health
    health_data = make_api_request('/health')
    
    # Get panels status
    panels_data = make_api_request('/panels')
    
    # Get latest decision
    latest_decision = make_api_request('/latest-decision')
    
    return render_template('dashboard.html', 
                         health=health_data,
                         panels=panels_data,
                         latest_decision=latest_decision)

@app.route('/analyze/<panel_id>')
def analyze_panel(panel_id):
    """Analyze specific panel"""
    data = {"panel_id": panel_id}
    result = make_api_request('/analyze', method='POST', data=data)
    
    if result:
        flash(f"Analysis completed for {panel_id}: {result.get('action', 'No action needed')}", "success")
    
    return redirect(url_for('dashboard'))

@app.route('/spray/<panel_id>')
def spray_panel(panel_id):
    """Trigger spray for specific panel"""
    data = {"panel_id": panel_id}
    result = make_api_request('/spray', method='POST', data=data)
    
    if result:
        flash(f"Cleaning initiated for {panel_id}: {result.get('action', 'Spray completed')}", "success")
    
    return redirect(url_for('dashboard'))

@app.route('/panels')
def panels_page():
    """Detailed panels management page"""
    panels_data = make_api_request('/panels')
    return render_template('panels.html', panels=panels_data)

@app.route('/settings')
def settings_page():
    """System settings page"""
    health_data = make_api_request('/health')
    return render_template('settings.html', health=health_data)

@app.route('/api/status')
def api_status():
    """API endpoint for frontend to check backend status"""
    try:
        health_data = make_api_request('/health')
        if health_data:
            return jsonify({"status": "connected", "data": health_data})
        else:
            return jsonify({"status": "disconnected", "error": "No response from backend"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/api/quick-analyze')
def quick_analyze():
    """Quick analyze all panels"""
    panels_data = make_api_request('/panels')
    if not panels_data:
        return jsonify({"error": "Could not get panels data"})
    
    results = []
    for panel in panels_data.get('panels', []):
        panel_id = panel['id']
        result = make_api_request('/analyze', method='POST', data={"panel_id": panel_id})
        if result:
            results.append(result)
    
    return jsonify({"results": results, "total": len(results)})

@app.route('/api/emergency-clean-all')
def emergency_clean_all():
    """Emergency clean all panels immediately"""
    panels_data = make_api_request('/panels')
    if not panels_data:
        return jsonify({"error": "Could not get panels data"})
    
    results = []
    total_water_used = 0
    successful_cleanings = 0
    
    for panel in panels_data.get('panels', []):
        panel_id = panel['id']
        result = make_api_request('/spray', method='POST', data={"panel_id": panel_id})
        if result:
            results.append(result)
            total_water_used += result.get('water_used_ml', 100)
            successful_cleanings += 1
    
    return jsonify({
        "results": results, 
        "total_panels": len(panels_data.get('panels', [])),
        "successful_cleanings": successful_cleanings,
        "total_water_used": total_water_used,
        "message": f"Emergency cleaning completed for {successful_cleanings} panels. Total water used: {total_water_used}ml"
    })

@app.route('/system-reports')
def system_reports():
    """System reports and analytics page"""
    # Get system statistics
    stats_data = make_api_request('/system/stats')
    
    # Get recent logs
    logs_data = make_api_request('/system/logs')
    
    # Get panels data for analysis
    panels_data = make_api_request('/panels')
    
    return render_template('reports.html', 
                         stats=stats_data,
                         logs=logs_data,
                         panels=panels_data)

@app.route('/api/system-reports')
def api_system_reports():
    """API endpoint for system reports data"""
    # Get system statistics
    stats_data = make_api_request('/system/stats')
    
    # Get recent logs
    logs_data = make_api_request('/system/logs')
    
    # Get panels data
    panels_data = make_api_request('/panels')
    
    # Calculate additional metrics
    if panels_data and panels_data.get('panels'):
        clean_panels = len([p for p in panels_data['panels'] if p['status'] == 'clean'])
        dirty_panels = len([p for p in panels_data['panels'] if 'need' in p['status']])
        moderate_panels = len([p for p in panels_data['panels'] if 'moderate' in p['status']])
        
        panel_health = {
            "clean": clean_panels,
            "moderate_dust": moderate_panels,
            "needs_cleaning": dirty_panels,
            "health_percentage": round((clean_panels / len(panels_data['panels'])) * 100, 1)
        }
    else:
        panel_health = {"clean": 0, "moderate_dust": 0, "needs_cleaning": 0, "health_percentage": 0}
    
    return jsonify({
        "stats": stats_data,
        "logs": logs_data[:10] if logs_data else [],  # Last 10 logs
        "panel_health": panel_health,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/clean-dirty-panels')
def clean_dirty_panels():
    """Clean only panels that need attention (moderate dust or needs cleaning)"""
    panels_data = make_api_request('/panels')
    if not panels_data:
        return jsonify({"error": "Could not get panels data"})
    
    # Filter panels that need cleaning
    dirty_panels = [p for p in panels_data.get('panels', []) 
                   if p['status'] != 'clean']
    
    if not dirty_panels:
        return jsonify({
            "message": "No panels need cleaning at this time",
            "total_panels": len(panels_data.get('panels', [])),
            "panels_cleaned": 0,
            "total_water_used": 0
        })
    
    results = []
    total_water_used = 0
    successful_cleanings = 0
    
    for panel in dirty_panels:
        panel_id = panel['id']
        result = make_api_request('/spray', method='POST', data={"panel_id": panel_id})
        if result:
            results.append(result)
            total_water_used += result.get('water_used_ml', 100)
            successful_cleanings += 1
    
    return jsonify({
        "results": results,
        "total_panels": len(panels_data.get('panels', [])),
        "dirty_panels_found": len(dirty_panels),
        "panels_cleaned": successful_cleanings,
        "total_water_used": total_water_used,
        "message": f"Cleaned {successful_cleanings} dirty panels. Water used: {total_water_used}ml"
    })

if __name__ == '__main__':
    print("🌞 Starting Solar Panel Flask Frontend...")
    print("🌐 Frontend Server: http://localhost:5000")
    print("🔗 Backend API: http://localhost:8000")
    print("Make sure the FastAPI backend is running on port 8000!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
