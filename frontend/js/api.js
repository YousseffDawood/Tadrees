/**
 * api.js – Centralized fetch wrapper with JWT auth, auto-refresh, and safe responses.
 * All API calls go through api.get/post/put/patch/delete().
 */

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('access');
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  try {
    function buildUrl(p) {
      if (!p) return API_BASE;
      if (p.startsWith('/')) return API_BASE + p;
      return API_BASE + '/' + p;
    }

    let res = await fetch(buildUrl(path), { ...options, headers });

    if (res.status === 401) {
      const refreshed = await tryRefresh();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${localStorage.getItem('access')}`;
        res = await fetch(buildUrl(path), { ...options, headers });
      } else {
        logout();
        return null;
      }
    }

    return res;
  } catch (err) {
    console.error('API network error:', path, err);
    return null;
  }
}

async function tryRefresh() {
  const refresh = localStorage.getItem('refresh');
  if (!refresh) return false;
  try {
    const res = await fetch(buildUrl('/api/users/token/refresh/'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem('access', data.access);
    return true;
  } catch {
    return false;
  }
}

function logout() {
  localStorage.clear();
  window.location.href = 'login.html';
}

function formatApiError(data) {
  if (!data) return 'Request failed';
  if (typeof data === 'string') return data;
  if (data.error) return data.error;
  if (data.detail) {
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) return data.detail[0];
    return JSON.stringify(data.detail);
  }
  return JSON.stringify(data);
}

async function parseApiResponse(res) {
  if (!res) {
    return {
      ok: false,
      status: 0,
      data: null,
      networkError: true,
      message: getApiNetworkMessage(),
    };
  }

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }

  return {
    ok: res.ok,
    status: res.status,
    data,
    networkError: false,
    message: res.ok ? '' : formatApiError(data),
  };
}

async function apiRequest(method, path, body) {
  const options = { method };
  if (body !== undefined) {
    options.body = body instanceof FormData ? body : JSON.stringify(body);
  }

  const res = await apiFetch(path, options);
  return parseApiResponse(res);
}

const api = {
  get:    (path)            => apiRequest('GET', path),
  post:   (path, body)      => apiRequest('POST', path, body),
  put:    (path, body)      => apiRequest('PUT', path, body),
  patch:  (path, body)      => apiRequest('PATCH', path, body),
  delete: (path)            => apiRequest('DELETE', path),
};
