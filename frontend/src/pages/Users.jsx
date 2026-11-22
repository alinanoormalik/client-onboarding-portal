import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import api, { errorMessage } from "../api";
import { useAuth } from "../auth.jsx";

const emptyForm = { full_name: "", email: "", password: "", role: "staff" };

export default function Users() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);

  async function load() {
    try {
      const { data } = await api.get("/auth/users");
      setUsers(data);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  useEffect(() => {
    if (user?.role === "admin") load();
  }, [user]);

  if (user?.role !== "admin") return <Navigate to="/" replace />;

  const setField = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await api.post("/auth/users", { ...form, email: form.email.trim() });
      setMessage(`User ${form.email.trim()} created.`);
      setForm(emptyForm);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <h1>Staff users</h1>
      {error && <div className="alert error">{error}</div>}
      {message && <div className="alert success">{message}</div>}

      <form onSubmit={handleSubmit}>
        <fieldset>
          <legend>Add a user</legend>
          <div className="grid">
            <label>Full name *
              <input name="full_name" value={form.full_name} onChange={setField} required maxLength={150} />
            </label>
            <label>Email *
              <input type="email" name="email" value={form.email} onChange={setField} required />
            </label>
            <label>Password * (8 to 72 characters)
              <input type="password" name="password" value={form.password} onChange={setField}
                required minLength={8} maxLength={72} />
            </label>
            <label>Role
              <select name="role" value={form.role} onChange={setField}>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
            </label>
          </div>
          <div className="form-actions" style={{ marginTop: 16 }}>
            <button className="btn primary" disabled={saving}>
              {saving ? "Creating…" : "Create user"}
            </button>
          </div>
        </fieldset>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th></tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.full_name}</td>
                <td>{u.email}</td>
                <td style={{ textTransform: "capitalize" }}>{u.role}</td>
                <td>{u.is_active ? "Active" : "Disabled"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}