import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getTripMembers, inviteMember } from "../api";

interface Member {
  id: string;
  email: string;
  name: string;
}

function TripDetailPage() {
  const { tripId } = useParams<{ tripId: string }>();
  const [members, setMembers] = useState<Member[]>([]);
  const [inviteEmail, setInviteEmail] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    loadMembers();
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
    </div>
  );
}

export default TripDetailPage;