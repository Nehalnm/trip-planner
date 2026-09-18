import { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";

interface LocationUpdate {
  user_id: string;
  name: string;
  lat: number;
  lng: number;
}

function LiveMap({ tripId }: { tripId: string }) {
  const [locations, setLocations] = useState<Record<string, LocationUpdate>>({});
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/trips/${tripId}/location`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data: LocationUpdate = JSON.parse(event.data);
      setLocations((prev) => ({ ...prev, [data.user_id]: data }));
    };

    return () => {
      ws.close();
    };
  }, [tripId]);

  function shareMyLocation() {
    navigator.geolocation.getCurrentPosition((position) => {
      const update = {
        user_id: localStorage.getItem("userId") || "unknown",
        name: localStorage.getItem("userName") || "unknown",
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      };
      wsRef.current?.send(JSON.stringify(update));
      setLocations((prev) => ({ ...prev, [update.user_id]: update }));
    });
  }

  return (
    <div>
      <button onClick={shareMyLocation}>Share My Location</button>
      <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: "400px" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {Object.values(locations).map((loc) => (
          <Marker key={loc.user_id} position={[loc.lat, loc.lng]}>
            <Popup>{loc.name}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default LiveMap;