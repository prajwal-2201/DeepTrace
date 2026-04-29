import os
from ui.app import app, socketio

if __name__ == '__main__':
    # Ensure necessary directories exist for uploads/reports
    os.makedirs('data/uploads', exist_ok=True)
    os.makedirs('data/reports', exist_ok=True)
    os.makedirs('data/recovered', exist_ok=True)
    
    # Run the Flask app with SocketIO
    socketio.run(app, debug=True, port=5000)
