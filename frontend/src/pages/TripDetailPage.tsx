import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getTripMembers, inviteMember } from "../api";
import { getItinerary, createItineraryItem } from "../api";

interface Member {
  id: string;
  email: string;
  name: string;
}
interface ItineraryItem {
  id: string;
  title: string;
  scheduled_at: string | null;
  notes: string | null;
}

function TripDetailPage() {
  const { tripId } = useParams<{ tripId: string }>();
  const [members, setMembers] = useState<Member[]>([]);
  const [inviteEmail, setInviteEmail] = useState("");
  const [error, setError] = useState("");
  const [itinerary, setItinerary] = useState<ItineraryItem[]>([]);
  const [itemTitle, setItemTitle] = useState("");
  const [itemDate, setItemDate] = useState("");
  const [itemNotes, setItemNotes] = useState("");

  useEffect(() => {
    loadMembers();
    loadItinerary();
  }, [tripId]);

  async function loadMembers() {
    if (!tripId) return;
    try {
      const data = await getTripMembers(tripId);
      setMembers(data);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function loadItinerary() {
    if (!tripId) return;
    try {
      const data = await getItinerary(tripId);
      setItinerary(data);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleCreateItem(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!tripId) return;

    try {
      await createItineraryItem(tripId, itemTitle, itemDate, itemNotes);
      setItemTitle("");
      setItemDate("");
      setItemNotes("");
      loadItinerary();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!tripId) return;

    try {
      await inviteMember(tripId, inviteEmail);
      setInviteEmail("");
      loadMembers();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div>
      <h1>Trip Members</h1>

      <ul>
        {members.map((member) => (
          <li key={member.id}>
            {member.name} ({member.email})
          </li>
        ))}
      </ul>

      <h2>Invite Someone</h2>
      <form onSubmit={handleInvite}>
        <input
          type="email"
          placeholder="Email to invite"
          value={inviteEmail}
          onChange={(e) => setInviteEmail(e.target.value)}
        />
        <button type="submit">Invite</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <h2>Itinerary</h2>
      <ul>
        {itinerary.map((item) => (
          <li key={item.id}>
            <strong>{item.title}</strong>
            {item.scheduled_at && <p>Scheduled: {item.scheduled_at}</p>}
            {item.notes && <p>Notes: {item.notes}</p>}
          </li>
        ))}
      </ul>

      <h3>Add Itinerary Item</h3>
      <form onSubmit={handleCreateItem}>
        <input
          type="text"
          placeholder="Title"
          value={itemTitle}
          onChange={(e) => setItemTitle(e.target.value)}
        />
        <input
          type="datetime-local"
          value={itemDate}
          onChange={(e) => setItemDate(e.target.value)}
        />
        <input
          type="text"
          placeholder="Notes"
          value={itemNotes}
          onChange={(e) => setItemNotes(e.target.value)}
        />
        <button type="submit">Add Item</button>
      </form>
    </div>
  );
}

export default TripDetailPage;