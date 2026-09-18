import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      const data = await login(email, password);
      localStorage.setItem("token", data.access_token);

      const meResponse = await fetch("http://localhost:8000/me", {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      const me = await meResponse.json();
      localStorage.setItem("userId", me.id);
      localStorage.setItem("userName", me.name);
      
      navigate("/trips");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Log In</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default LoginPage;