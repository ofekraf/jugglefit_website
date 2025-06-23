import subprocess
import sys

BACKEND_CMD = [sys.executable, '-m', 'uvicorn', 'server:app', '--reload', '--port', '5001']
FRONTEND_CMD = [sys.executable, '-m', 'http.server', '8000', '--directory', 'frontend']

backend_proc = None
frontend_proc = None

try:
    print('Starting FastAPI backend on http://localhost:5001 ...')
    backend_proc = subprocess.Popen(BACKEND_CMD)

    print('Starting frontend static server on http://localhost:8000 ...')
    frontend_proc = subprocess.Popen(FRONTEND_CMD)
    
    print('Both servers are running. Press Ctrl+C to stop.')
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print('Shutting down servers...')
    if backend_proc:
        backend_proc.terminate()
    if frontend_proc:
        frontend_proc.terminate()
    print('Servers stopped.') 