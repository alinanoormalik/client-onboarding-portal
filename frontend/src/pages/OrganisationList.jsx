
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errorMessage } from "../api";
import { useAuth } from "../auth.jsx";

export default function OrganisationList() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const [orgs, setOrgs] = useState([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const timer = setTimeout(async () => {
      setLoading(true);
      setError("");

      try {
        const { data } = await api.get("/organisations", {
          params: {
            search: search || undefined,
            status: status || undefined,
          },
        });

        setOrgs(data);
      } catch (err) {
        setError(errorMessage(err));
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [search, status]);

  async function handleDelete(org) {
    if (
      !window.confirm(
        `Delete "${org.name}" and all its contacts?`
      )
    ) {
      return;
    }

    try {
      await api.delete(`/organisations/${org.id}`);

      setOrgs((current) =>
        current.filter((o) => o.id !== org.id)
      );
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <>
      <h1>Organisations</h1>

      <div className="filters">
        <input
          placeholder="Search by name, email or registration no."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {error && <div className="alert error">{error}</div>}

      {loading ? (
        <p>Loading…</p>
      ) : orgs.length === 0 ? (
        <p>No organisations found.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Reg. No.</th>
                <th>Industry</th>
                <th>Email</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {orgs.map((o) => (
                <tr key={o.id}>
                  <td>{o.name}</td>
                  <td>{o.registration_number || "—"}</td>
                  <td>{o.industry || "—"}</td>
                  <td>{o.email || "—"}</td>

                  <td>
                    <span className={`badge ${o.status}`}>
                      {o.status}
                    </span>
                  </td>

                  <td className="actions">
                    <Link
                      to={`/organisations/${o.id}/edit`}
                      className="btn small"
                    >
                      Edit
                    </Link>

                    {isAdmin && (
                      <button
                        className="btn small danger"
                        onClick={() => handleDelete(o)}
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
