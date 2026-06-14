/**
 * auth.js – Login, logout, token storage, role helpers.
 */

function getUser()   { try { return JSON.parse(localStorage.getItem('user') || 'null'); } catch { return null; } }
function getRole()   { return localStorage.getItem('role') || ''; }
function getAccess() { return localStorage.getItem('access') || ''; }
function isLoggedIn(){ return !!getAccess(); }
function isAdmin()   { return getRole() === 'admin'; }
function isStaff()   { return getRole() === 'staff' || getRole() === 'admin'; }

async function doLogin(username, password) {
  let res;
  try {
    res = await fetch(`${API_BASE}/api/users/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw new Error(getApiNetworkMessage());
  }

  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Login failed');

  localStorage.setItem('access',  data.access);
  localStorage.setItem('refresh', data.refresh);
  localStorage.setItem('role',    data.role);
  localStorage.setItem('user',    JSON.stringify({ name: data.name, id: data.user_id }));

  return data;
}

function doLogout() {
  localStorage.clear();
  window.location.href = 'login.html';
}
