"use client";
import React, { useState, useRef, useEffect } from "react";
import styles from "./page.module.css";

const SIDEBAR_WIDTH = 260;

const staticChats = [
  { id: 1, title: "Q1 Analysis" },
  { id: 2, title: "Feature Usage" },
  { id: 3, title: "Churn Prediction" },
];

const roles = ["Product Manager"];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "system", content: "You are a helpful Product Manager assistant." },
  ]);
  const [input, setInput] = useState("");
  const [role, setRole] = useState(roles[0]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const userMessage = { role: "user", content: input.trim() };
    setMessages((msgs) => [...msgs, userMessage]);
    setInput("");
    try {
      const res = await fetch("/api/table-retriever", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input.trim() }),
      });
      if (!res.ok) throw new Error("Failed to fetch response");
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: data.enhanced_query || JSON.stringify(data) },
      ]);
    } catch (err: any) {
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: `Error: ${err.message}` },
      ]);
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh", background: "#f7f7f8" }}>
      {/* Sidebar */}
      <aside
        style={{
          width: SIDEBAR_WIDTH,
          background: "#fff",
          borderRight: "1px solid #ececec",
          display: "flex",
          flexDirection: "column",
          padding: "16px 0",
        }}
      >
        <div style={{ padding: "0 24px", marginBottom: 24 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Chats</h2>
        </div>
        <nav style={{ flex: 1 }}>
          {staticChats.map((chat) => (
            <div
              key={chat.id}
              style={{
                padding: "12px 24px",
                cursor: "pointer",
                borderRadius: 6,
                margin: "0 8px 8px 8px",
                background: "#f3f3f6",
                fontWeight: 500,
                color: "#222",
              }}
            >
              {chat.title}
            </div>
          ))}
        </nav>
        <div style={{ padding: "0 24px" }}>
          <button
            style={{
              width: "100%",
              padding: "10px 0",
              borderRadius: 6,
              border: "none",
              background: "#ececf1",
              color: "#444",
              fontWeight: 600,
              fontSize: 16,
              cursor: "pointer",
              marginTop: 8,
            }}
            disabled
          >
            + New Chat
          </button>
        </div>
      </aside>
      {/* Main Chat Area */}
      <main
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          height: "100vh",
          maxWidth: "100vw",
        }}
      >
        {/* Header */}
        <header
          style={{
            padding: "24px 32px 12px 32px",
            borderBottom: "1px solid #ececec",
            background: "#fff",
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, flex: 1 }}>
            Product Manager Chat
          </h1>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: 6,
              border: "1px solid #ececec",
              fontSize: 16,
              background: "#f7f7f8",
              color: "#222",
            }}
            disabled
          >
            {roles.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </header>
        {/* Chat Messages */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "32px 0 24px 0",
            background: "#f7f7f8",
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                background: msg.role === "user" ? "#e0eaff" : "#fff",
                color: "#222",
                padding: "14px 20px",
                borderRadius: 12,
                maxWidth: "70%",
                boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
                fontSize: 16,
                marginRight: msg.role === "user" ? 32 : 0,
                marginLeft: msg.role === "assistant" ? 32 : 0,
              }}
            >
              {msg.content}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        {/* Input Box */}
        <form
          onSubmit={handleSend}
          style={{
            display: "flex",
            alignItems: "center",
            padding: "20px 32px",
            background: "#fff",
            borderTop: "1px solid #ececec",
            gap: 12,
          }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            style={{
              flex: 1,
              padding: "14px 18px",
              borderRadius: 8,
              border: "1px solid #ececec",
              fontSize: 16,
              background: "#f7f7f8",
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) handleSend();
            }}
          />
          <button
            type="submit"
            style={{
              padding: "12px 24px",
              borderRadius: 8,
              border: "none",
              background: "#007aff",
              color: "#fff",
              fontWeight: 600,
              fontSize: 16,
              cursor: "pointer",
            }}
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
