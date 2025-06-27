# app.py
from flask import Flask, session, render_template_string
import os
import redis # Import the redis library

app = Flask(__name__)

# A secret key is required to use Flask sessions.
# In a production environment, this should be a strong, randomly generated key
# and ideally loaded from environment variables or a configuration file.
app.secret_key = os.urandom(24) # Generates a random 24-byte secret key

# --- Redis Configuration ---
# Connect to Redis. When running in a Podman pod, 'redis' will be the hostname
# for the Redis container, as containers in the same pod share the same network namespace.
# Use environment variables for production deployments.
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost') # Default to localhost for local testing
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379)) # Default Redis port
REDIS_DB = int(os.getenv('REDIS_DB', 0)) # Default Redis DB

try:
    # Attempt to connect to Redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    r.ping() # Check if the connection is active
    print(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    # In a real application, you might want to handle this more gracefully,
    # perhaps by exiting or using a fallback mechanism.
    r = None # Set r to None if connection fails

# HTML template for the page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Visit Counter</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gradient-to-r from-blue-500 to-purple-600 min-h-screen flex items-center justify-center p-4">
    <div class="bg-white p-8 rounded-lg shadow-2xl text-center max-w-md w-full animate-fade-in-down">
        <h1 class="text-4xl font-extrabold text-gray-800 mb-6 tracking-tight">
            Welcome to the Page Counter!
        </h1>
        <p class="text-2xl text-gray-700 mb-8 font-semibold">
            You have visited this page <span class="text-purple-600 font-bold">{{ visits }}</span> time(s).
        </p>
        <div class="mt-8">
            <button onclick="location.reload()"
                    class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-full shadow-lg transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300">
                Visit Again!
            </button>
        </div>
        <p class="text-sm text-gray-500 mt-6">
            (This counter now uses Redis for persistence, so the count won't reset on browser closure.
            However, for this specific app, the count is tied to the unique user ID generated for each visit.)
        </p>
    </div>

    <style>
        @keyframes fade-in-down {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .animate-fade-in-down {
            animation: fade-in-down 0.8s ease-out forwards;
        }
    </style>
</body>
</html>
"""

@app.route('/')
def index():
    """
    Increments the visit count for the current session and displays it.
    The visit count is now stored in Redis, keyed by a session ID.
    """
    if r is None:
        # Fallback if Redis connection failed
        visits = session.get('visits', 0)
        visits += 1
        session['visits'] = visits
        message = "(Redis connection failed, using session-based counter)"
    else:
        # Use a unique session ID to track visits for each user in Redis
        # This makes the counter persistent even if the browser closes,
        # but a new session will get a new ID and start from 1.
        if 'user_id' not in session:
            session['user_id'] = str(os.urandom(16).hex()) # Generate a unique ID for the user

        user_id = session['user_id']
        
        try:
            # Increment the visit count for this user_id in Redis
            visits = r.incr(f"visits:{user_id}")
            message = "(Using Redis for visit count)"
        except Exception as e:
            print(f"Error interacting with Redis: {e}")
            # Fallback to in-memory session if Redis operation fails
            visits = session.get('visits', 0)
            visits += 1
            session['visits'] = visits
            message = "(Error with Redis, falling back to session-based counter)"

    # Render the HTML template with the current visit count
    # Note: The HTML_TEMPLATE doesn't directly display the message,
    # but the logic is here for completeness.
    return render_template_string(HTML_TEMPLATE, visits=visits)

if __name__ == '__main__':
    # Run the Flask application in debug mode (useful for development)
    # For production, debug should be False and a production-ready WSGI server should be used.
    app.run(debug=True, host='0.0.0.0', port=5000)
