import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import TripListPage from "./pages/TripListPage";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/trips" element={<TripListPage />} />
      <Route path="/" element={<Navigate to="/login" />} />
    </Routes>
  );
}

export default App;