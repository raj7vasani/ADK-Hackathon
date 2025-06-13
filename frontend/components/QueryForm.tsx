import { useState } from "react";

export default function QueryForm() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const res = await fetch("/api/table-retriever", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    setResult(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Ask your data question..."
      />
      <button type="submit">Submit</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </form>
  );
}