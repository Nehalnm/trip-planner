import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { getTripMembers, inviteMember, getItinerary, createItineraryItem, createExpense, getSettlement } from "../api";
import LiveMap from "../components/LiveMap";
import ChatBox from "../components/ChatBox";
import PollBox from "../components/PollBox";
import AnalyticsDashboard from "../components/AnalyticsDashboard";
import PhotoGallery from "../components/PhotoGallery";
import { scanReceipt } from "../api";

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
interface SettlementTransaction {
  from_user_id: string;
  from_name: string;
  to_user_id: string;
  to_name: string;
  amount: number;
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
  const [expenseAmount, setExpenseAmount] = useState("");
  const [expenseDescription, setExpenseDescription] = useState("");
  const [selectedParticipants, setSelectedParticipants] = useState<string[]>([]);
  const [settlement, setSettlement] = useState<SettlementTransaction[]>([]);
  const [expenseCategory, setExpenseCategory] = useState("Other");
  const receiptInputRef = useRef<HTMLInputElement>(null);

  async function handleScanReceipt(e: React.ChangeEvent<HTMLInputElement>) {
  const file = e.target.files?.[0];
  if (!file || !tripId) return;

  const result = await scanReceipt(tripId, file);

  if (result.guessed_amount) {
    setExpenseAmount(result.guessed_amount.toString());
  }

  if (receiptInputRef.current) receiptInputRef.current.value = "";
}
  useEffect(() => {
    loadMembers();
    loadItinerary();
    loadSettlement();
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

  async function loadSettlement() {
    if (!tripId) return;
    try {
      const data = await getSettlement(tripId);
      setSettlement(data);
    } catch (err) {
      setError((err as Error).message);
    }
  }
  function toggleParticipant(userId: string) {
    setSelectedParticipants((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    );
  }

  async function handleCreateExpense(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!tripId) return;

    try {
      await createExpense(tripId, parseFloat(expenseAmount), expenseDescription, expenseCategory, selectedParticipants);
      setExpenseAmount("");
      setExpenseDescription("");
      setExpenseCategory("Other");
      setSelectedParticipants([]);
      loadSettlement();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div>
      <h1>Trip Members</h1>
      {tripId && <LiveMap tripId={tripId} />}

      <h2>Trip Chat</h2>
      {tripId && <ChatBox tripId={tripId} />}

      <h2>Polls</h2>
      {tripId && <PollBox tripId={tripId} />}

      <h2>Trip Photos</h2>
      {tripId && <PhotoGallery tripId={tripId} />}

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

<h2>Add Expense</h2>
        <form onSubmit={handleCreateExpense}>
          <div style={{ marginBottom: "8px" }}>
            <label>Scan a receipt (optional): </label>
            <input type="file" accept="image/*" ref={receiptInputRef} onChange={handleScanReceipt} />
          </div>
          <input
            type="number"
            placeholder="Amount"
            value={expenseAmount}
            onChange={(e) => setExpenseAmount(e.target.value)}
          />
        <input
          type="text"
          placeholder="Description"
          value={expenseDescription}
          onChange={(e) => setExpenseDescription(e.target.value)}
        />
        <select value={expenseCategory} onChange={(e) => setExpenseCategory(e.target.value)}>
          <option value="Food">Food</option>
          <option value="Transport">Transport</option>
          <option value="Accommodation">Accommodation</option>
          <option value="Activities">Activities</option>
          <option value="Other">Other</option>
        </select>
        <div>
          <p>Select Participants:</p>
          {members.map((member) => (
            <label key={member.id}>
              <input
                type="checkbox"
                checked={selectedParticipants.includes(member.id)}
                onChange={() => toggleParticipant(member.id)}
              />
              {member.name}
            </label>
          ))}
        </div>
        <button type="submit">Add Expense</button>
      </form>
      
      <h2>Settlement</h2>
      {settlement.length === 0 ? (
        <p>All settled up!</p>
      ) : (
        <ul>
          {settlement.map((tx, idx) => (
            <li key={idx}>
              {tx.from_name} owes {tx.to_name}: ${tx.amount.toFixed(2)}
            </li>
          ))}
        </ul>
      )}
      <h2>Budget Analytics</h2>
      {tripId && <AnalyticsDashboard tripId={tripId} />}
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