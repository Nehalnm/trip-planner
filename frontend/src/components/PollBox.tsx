import { useState, useEffect, useRef } from "react";
import { createPoll, getPolls, getPollResults, voteOnPoll } from "../api";

interface Poll {
  id: string;
  question: string;
  options: string[];
}

interface PollResults {
  poll_id: string;
  question: string;
  options: string[];
  vote_counts: number[];
  total_votes: number;
}

function PollBox({ tripId }: { tripId: string }) {
  const [polls, setPolls] = useState<Poll[]>([]);
  const [results, setResults] = useState<Record<string, PollResults>>({});
  const [question, setQuestion] = useState("");
  const [optionsText, setOptionsText] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    loadPolls();

    const token = localStorage.getItem("token");
    const ws = new WebSocket(`ws://localhost:8000/ws/trips/${tripId}/polls?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data: PollResults = JSON.parse(event.data);
      setResults((prev) => ({ ...prev, [data.poll_id]: data }));
    };

    return () => {
      ws.close();
    };
  }, [tripId]);

  async function loadPolls() {
    const data = await getPolls(tripId);
    setPolls(data);
    for (const poll of data) {
      const res = await getPollResults(poll.id);
      setResults((prev) => ({ ...prev, [poll.id]: res }));
    }
  }

  async function handleCreatePoll(e: React.FormEvent) {
    e.preventDefault();
    const options = optionsText.split(",").map((o) => o.trim()).filter(Boolean);
    if (options.length < 2) return;

    await createPoll(tripId, question, options);
    setQuestion("");
    setOptionsText("");
    loadPolls();
  }

  async function handleVote(pollId: string, optionIndex: number) {
    await voteOnPoll(pollId, optionIndex);
  }

  return (
    <div>
      {polls.map((poll) => {
        const res = results[poll.id];
        return (
          <div key={poll.id} style={{ border: "1px solid #ccc", padding: "8px", marginBottom: "8px" }}>
            <p><strong>{poll.question}</strong></p>
            {poll.options.map((opt, idx) => (
              <div key={idx}>
                <button onClick={() => handleVote(poll.id, idx)}>{opt}</button>
                {res && <span> — {res.vote_counts[idx]} votes</span>}
              </div>
            ))}
            {res && <p>Total votes: {res.total_votes}</p>}
          </div>
        );
      })}

      <h3>Create a Poll</h3>
      <form onSubmit={handleCreatePoll}>
        <input
          type="text"
          placeholder="Question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <input
          type="text"
          placeholder="Options, comma-separated"
          value={optionsText}
          onChange={(e) => setOptionsText(e.target.value)}
        />
        <button type="submit">Create Poll</button>
      </form>
    </div>
  );
}

export default PollBox;