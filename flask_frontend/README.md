# Solar Panel Cleaning System - Flask Frontend

A modern, responsive web interface for managing an automated solar panel cleaning system. Built with Flask, Bootstrap 5, and integrated with FastAPI backend.

## 🌟 Features

### Dashboard
- **Real-time System Health** - Monitor water levels, temperature, and system status
- **Panel Overview** - View all panels with their current status and dust levels
- **Latest Decisions** - See the most recent AI-powered cleaning decisions
- **Quick Actions** - Analyze all panels or perform emergency cleaning

### Panel Management
- **Detailed Panel View** - Individual panel information and controls
- **Bulk Operations** - Analyze or clean multiple panels at once
- **Status Tracking** - Real-time status updates (clean, moderate dust, needs cleaning)
- **Action Buttons** - Direct analyze and clean controls for each panel

### System Settings
- **Connection Management** - Backend API connection testing and configuration
- **Cleaning Parameters** - Adjust dust thresholds and spray settings
- **Maintenance Schedule** - Set up automated cleaning schedules
- **Notifications** - Configure email alerts and system notifications

### Modern UI/UX
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Bootstrap 5** - Modern, clean interface with smooth animations
- **Real-time Updates** - Auto-refresh system status every 30 seconds
- **Interactive Elements** - Hover effects, progress bars, and status indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI backend running on port 8000
- Required Python packages (see requirements.txt)

### Installation

1. **Install Dependencies**
   ```bash
   pip install flask requests
   ```

2. **Start the Backend** (if not already running)
   ```bash
   python main.py
   ```

3. **Start the Flask Frontend**
   ```bash
   python flask_frontend/app.py
   ```

4. **Access the Application**
   - Frontend: http://localhost:5000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Alternative: Start Everything at Once
```bash
python run_system.py
```

## 📋 API Integration

The Flask frontend communicates with the FastAPI backend through these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System status and version |
| `/health` | GET | System health metrics |
| `/analyze` | POST | Analyze panel dust levels |
| `/spray` | POST | Trigger panel cleaning |
| `/panels` | GET | List all panels and status |
| `/latest-decision` | GET | Get latest AI decision |

## 🎨 UI Components

### Status Indicators
- 🟢 **Green**: Clean panels, healthy system
- 🟡 **Yellow**: Moderate dust, scheduled cleaning
- 🔴 **Red**: Needs immediate cleaning, system issues

### Action Buttons
- **Analyze**: Run dust detection on specific panel
- **Clean**: Trigger water spray cleaning
- **Quick Analyze All**: Analyze all panels at once
- **Emergency Clean**: Immediate cleaning for all panels

### Real-time Features
- Auto-refresh system status every 30 seconds
- Live connection status indicator
- Instant feedback on all actions
- Progress indicators for long operations

## 🔧 Configuration

### Backend Connection
Edit the `BACKEND_URL` in `flask_frontend/app.py`:
```python
BACKEND_URL = "http://localhost:8000"  # Change if backend is on different host/port
```

### Frontend Settings
- **Port**: Default 5000 (change in app.py)
- **Debug Mode**: Enabled by default for development
- **Auto-refresh**: 30-second intervals (configurable in settings)

## 📱 Responsive Design

The interface is fully responsive and works on:
- **Desktop**: Full feature set with sidebar navigation
- **Tablet**: Optimized layout with touch-friendly controls
- **Mobile**: Compact view with essential features

## 🛠️ Development

### Project Structure
```
flask_frontend/
├── app.py                 # Main Flask application
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── dashboard.html    # Main dashboard page
│   ├── panels.html       # Panel management page
│   └── settings.html     # System settings page
```

### Adding New Features
1. **New Route**: Add route function in `app.py`
2. **New Template**: Create HTML template in `templates/`
3. **API Integration**: Use `make_api_request()` helper function
4. **Styling**: Extend Bootstrap classes or add custom CSS

### Custom Styling
The interface uses Bootstrap 5 with custom CSS:
- **Solar Theme**: Blue/purple gradient backgrounds
- **Card Design**: Rounded corners with subtle shadows
- **Animations**: Smooth hover effects and transitions
- **Status Colors**: Semantic color coding for all states

## 🔒 Security Features

- **Input Validation**: All user inputs are validated
- **CSRF Protection**: Flask secret key for session security
- **API Timeout**: 10-second timeout for backend requests
- **Error Handling**: Graceful degradation when backend is unavailable

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📊 System Requirements

- **RAM**: 256MB minimum for Flask frontend
- **Storage**: 10MB for templates and static files
- **Network**: HTTP connection to FastAPI backend
- **Browser**: JavaScript enabled for real-time features

## 🆘 Troubleshooting

### Backend Connection Issues
1. Verify FastAPI is running on port 8000
2. Check `BACKEND_URL` configuration
3. Test connection using Settings > Test Connection

### Frontend Not Loading
1. Check Python Flask installation
2. Verify port 5000 is available
3. Check console for JavaScript errors

### UI Issues
1. Clear browser cache
2. Ensure JavaScript is enabled
3. Try different browser

## 🔄 Future Enhancements

- **User Authentication**: Login system with role-based access
- **Data Visualization**: Charts and graphs for historical data
- **Mobile App**: Native mobile application
- **Advanced Scheduling**: More complex cleaning schedules
- **Weather Integration**: Weather-based cleaning decisions
- **Export Features**: Data export in various formats

## 📝 License

This project is part of the Solar Panel Cleaning System and follows the same licensing terms.

## 👥 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes to Flask frontend
4. Test with FastAPI backend
5. Submit pull request

## 📞 Support

For issues with the Flask frontend:
- Check backend connectivity first
- Review browser console for errors
- Verify all dependencies are installed
- Contact system administrator if issues persist
