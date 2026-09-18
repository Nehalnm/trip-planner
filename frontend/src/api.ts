const API_BASE_URL = "http://localhost:8000";

export async function signup(email: string, name: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, name, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Signup failed");
  }

  return response.json();
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Login failed");
  }

  return response.json();
}

function authHeaders() {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function getTrips() {
  const response = await fetch(`${API_BASE_URL}/trips`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch trips");
  }

  return response.json();
}

export async function createTrip(name: string, startDate: string, endDate: string) {
  const response = await fetch(`${API_BASE_URL}/trips`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ name, start_date: startDate || null, end_date: endDate || null }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create trip");
  }

  return response.json();
}