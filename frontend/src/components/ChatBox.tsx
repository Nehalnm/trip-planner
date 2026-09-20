import { useState, useEffect, useRef } from "react";
import { getChatHistory } from "../api";

interface ChatMessage {
  id: string;
  user_id: string;
  sender_name: string;
  content: string;
  created_at: string;
}

function ChatBox({ tripId }: { tripId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    getChatHistory(tripId).then(setMessages);

    const token = localStorage.getItem("token");
    const ws = new WebSocket(`ws://localhost:8000/ws/trips/${tripId}/chat?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data: ChatMessage = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    return () => {
      ws.close();
    };
  }, [tripId]);

  function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    wsRef.current?.send(JSON.stringify({ content: input }));
    setInput("");
  }

  return (
    <div>
      <div style={{ height: "200px", overflowY: "auto", border: "1px solid #ccc", padding: "8px" }}>
        {messages.map((msg) => (
          <p key={msg.id}>
            <strong>{msg.sender_name}:</strong> {msg.content}
          </p>
        ))}
      </div>
      <form onSubmit={sendMessage}>
        <input
          type="text"
          placeholder="Type a message"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default ChatBox;