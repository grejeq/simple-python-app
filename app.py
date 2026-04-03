from flask import Flask, jsonify
import os, socket

app = Flask(__name__)

@app.route('/')
def hello():
    student = os.environ.get('STUDENT_NAME', 'Student')
    return f"<h1>Hello from Jenkins CI/CD Pipeline!</h1><p>Student: {student}</p><p>Host: {socket.gethostname()}</p>"

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
