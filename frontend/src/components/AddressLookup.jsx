import { useEffect, useRef, useState } from "react";
import api, { errorMessage } from "../api";

export default function AddressLookup({ onSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const skipNext = useRef(false);

  useEffect(() => {
    if (skipNext.current) {
      skipNext.current = false;
      return;
    }
    if (query.trim().length < 3) {
      setResults([]);
      setOpen(false);
      setError("");
      return;
    }
    let cancelled = false;
    const timer = setTimeout(async () => {
      setLoading(true);
      setError("");
      try {
        const { data } = await api.get("/addresses/search", {
          params: { q: query.trim() },
        });
        if (!cancelled) {
          setResults(data);
          setOpen(true);
        }
      } catch (err) {
        if (!cancelled) {
          setResults([]);
          setError(errorMessage(err));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 500);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query]);

  function choose(item) {
    skipNext.current = true;
    setQuery(item.label);
    setOpen(false);
    onSelect(item);
  }

  return (
    <div className="address-lookup">
      <label>
        Find UK address
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Start typing an address or postcode, e.g. 10 Downing Street London"
          autoComplete="off"
        />
      </label>
      {loading && <span className="hint">Searching…</span>}
      {error && <div className="alert error">{error}</div>}
      {open && !loading &&
        (results.length ? (
          <ul className="suggestions">
            {results.map((r, i) => (
              <li key={i}>
                <button type="button" onClick={() => choose(r)}>
                  {r.label}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <span className="hint">
            No addresses found. You can still enter the address manually below.
          </span>
        ))}
    </div>
  );
}