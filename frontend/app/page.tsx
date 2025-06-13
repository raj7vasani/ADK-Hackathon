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
    <div className={styles.container}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <h2>Chats</h2>
        </div>
        <nav className={styles.sidebarNav}>
          {staticChats.map((chat) => (
            <div key={chat.id} className={styles.sidebarChat}>
              {chat.title}
            </div>
          ))}
        </nav>
        <div className={styles.sidebarFooter}>
          <button className={styles.sidebarButton} disabled>
            + New Chat
          </button>
        </div>
      </aside>
      {/* Main Chat Area */}
      <main className={styles.main}>
        {/* Header */}
        <header className={styles.header}>
          <h1 className={styles.headerTitle}>Product Manager Chat</h1>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className={styles.roleSelect}
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
        <div className={styles.chatArea}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={
                msg.role === "user"
                  ? styles.userMessage
                  : styles.assistantMessage
              }
            >
              {msg.content}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        {/* Input Box */}
        <form onSubmit={handleSend} className={styles.inputBox}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            className={styles.input}
          />
          <button type="submit" className={styles.sendButton}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
