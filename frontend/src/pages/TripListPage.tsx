import { useState, useEffect } from "react";
import { getTrips, createTrip } from "../api";
import { Link } from "react-router-dom";

interface Trip {
  id: string;
  name: string;
  start_date: string | null;
  end_date: string | null;
}

function TripListPage() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [name, setName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    loadTrips();
  }, []);

  async function loadTrips() {
    try {
      const data = await getTrips();
      setTrips(data);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      await createTrip(name, startDate, endDate);
      setName("");
      setStartDate("");
      setEndDate("");
      loadTrips();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div>
      <h1>My Trips</h1>

      <ul>
        {trips.map((trip) => (
          <li key={trip.id}>
            <Link to={`/trips/${trip.id}`}>{trip.name}</Link>{" "}
            {trip.start_date && `(${trip.start_date} → ${trip.end_date})`}
          </li>
        ))}
      </ul>

      <h2>Create a Trip</h2>
      <form onSubmit={handleCreate}>
        <input
          type="text"
          placeholder="Trip name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />
        <button type="submit">Create Trip</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default TripListPage;