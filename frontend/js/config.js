/**
 * config.js – Shared frontend configuration.
 */

const DEFAULT_API_BASE = 'http://127.0.0.1:8000';

// Allow the frontend to derive the API base when served from a dev server.
let API_BASE = DEFAULT_API_BASE;
try {
  const { protocol, hostname, port } = window.location;
  // If the frontend is served from localhost, assume backend is on port 8000.
  if (hostname === '127.0.0.1' || hostname === 'localhost') {
    API_BASE = `${protocol}//127.0.0.1:8000`;
  }
} catch (e) {
  // ignore (e.g. when evaluated in non-browser environments)
}

const DEV_FRONTEND_PORTS = ['5500', '3000'];

function getApiNetworkMessage() {
  const origin = window.location.origin;

  if (origin === 'null' || origin.startsWith('file:')) {
    return 'Cannot reach the API. Run the frontend server (e.g. Live Server) instead of opening files directly, then ensure Django is running.';
  }

  if (!DEV_FRONTEND_PORTS.includes(window.location.port)) {
    return `Cannot reach the API from ${origin}. Open http://127.0.0.1:5500/login.html and ensure Django is running at ${API_BASE}.`;
  }

  return `Cannot reach the server at ${API_BASE}. Make sure Django is running (run \`python manage.py runserver 127.0.0.1:8000\`).`;
}
