import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api, { errorMessage } from "../api";
import AddressLookup from "../components/AddressLookup.jsx";

const emptyOrg = {
  name: "", registration_number: "", industry: "", email: "", phone: "",
  website: "", address: "", address_line1: "", address_line2: "", city: "",
  county: "", postcode: "", country: "United Kingdom", status: "pending",
};
const emptyContact = {
  full_name: "", email: "", phone: "", job_title: "",
  contact_type: "general", is_primary: false,
};

// Convert blank strings to null so the API stores NULL, not ""
const clean = (obj) =>
  Object.fromEntries(
    Object.entries(obj).map(([k, v]) => {
      if (typeof v !== "string") return [k, v];
      const trimmed = v.trim();
      return [k, trimmed === "" ? null : trimmed];
    })
  );

const pick = (source, template) =>
  Object.fromEntries(Object.keys(template).map((k) => [k, source[k] ?? template[k]]));

export default function OrganisationForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [org, setOrg] = useState(emptyOrg);
  const [contacts, setContacts] = useState([{ ...emptyContact, is_primary: true }]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isEdit) return;
    api
      .get(`/organisations/${id}`)
      .then(({ data }) => {
        setOrg(pick(data, emptyOrg));
        setContacts(data.contacts.map((c) => pick(c, emptyContact)));
      })
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [id, isEdit]);

  const setOrgField = (e) => setOrg({ ...org, [e.target.name]: e.target.value });

  const applyAddress = (a) =>
    setOrg((o) => ({
      ...o,
      address: a.label,
      address_line1: a.address_line1 || "",
      address_line2: a.address_line2 || "",
      city: a.city || "",
      county: a.county || "",
      postcode: a.postcode || "",
      country: a.country || "United Kingdom",
    }));

  const setContactField = (index, field, value) =>
    setContacts(contacts.map((c, i) => (i === index ? { ...c, [field]: value } : c)));

  const makePrimary = (index) =>
    setContacts(contacts.map((c, i) => ({ ...c, is_primary: i === index })));

  const removeContact = (index) => {
    const remaining = contacts.filter((_, i) => i !== index);
    if (remaining.length && !remaining.some((c) => c.is_primary)) remaining[0].is_primary = true;
    setContacts(remaining);
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    const payload = { ...clean(org), contacts: contacts.map(clean) };
    try {
      if (isEdit) await api.put(`/organisations/${id}`, payload);
      else await api.post("/organisations", payload);
      navigate("/");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p>Loading…</p>;

  return (
    <form onSubmit={handleSubmit}>
      <h1>{isEdit ? "Edit Client" : "New Client Onboarding"}</h1>
      {error && <div className="alert error">{error}</div>}

      <fieldset>
        <legend>Organisation details</legend>
        <div className="grid">
          <label>Name *
            <input name="name" value={org.name} onChange={setOrgField} required maxLength={200} />
          </label>
          <label>Registration number
            <input name="registration_number" value={org.registration_number} onChange={setOrgField} maxLength={100} />
          </label>
          <label>Industry
            <input name="industry" value={org.industry} onChange={setOrgField} maxLength={150} />
          </label>
          <label>Email
            <input type="email" name="email" value={org.email} onChange={setOrgField} />
          </label>
          <label>Phone
            <input name="phone" value={org.phone} onChange={setOrgField} maxLength={30} />
          </label>
          <label>Website
            <input name="website" value={org.website} onChange={setOrgField} placeholder="https://" />
          </label>
          <label>Status
            <select name="status" value={org.status} onChange={setOrgField}>
              <option value="pending">Pending</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </label>
        </div>
      </fieldset>

      <fieldset>
        <legend>Postal address</legend>
        <div className="grid">
          <div className="full">
            <AddressLookup onSelect={applyAddress} />
          </div>
          <label>Address line 1
            <input name="address_line1" value={org.address_line1} onChange={setOrgField} maxLength={200} />
          </label>
          <label>Address line 2
            <input name="address_line2" value={org.address_line2} onChange={setOrgField} maxLength={200} />
          </label>
          <label>City
            <input name="city" value={org.city} onChange={setOrgField} maxLength={100} />
          </label>
          <label>County
            <input name="county" value={org.county} onChange={setOrgField} maxLength={100} />
          </label>
          <label>Postcode
            <input name="postcode" value={org.postcode} maxLength={10}
              onChange={(e) => setOrg({ ...org, postcode: e.target.value.toUpperCase() })} />
          </label>
          <label>Country
            <input name="country" value={org.country} onChange={setOrgField} maxLength={100} />
          </label>
        </div>
      </fieldset>

      <fieldset>
        <legend>Contacts</legend>
        {contacts.map((c, i) => (
          <div className="contact-card" key={i}>
            <div className="grid">
              <label>Full name *
                <input value={c.full_name} required maxLength={150}
                  onChange={(e) => setContactField(i, "full_name", e.target.value)} />
              </label>
              <label>Job title
                <input value={c.job_title}
                  onChange={(e) => setContactField(i, "job_title", e.target.value)} />
              </label>
              <label>Email
                <input type="email" value={c.email}
                  onChange={(e) => setContactField(i, "email", e.target.value)} />
              </label>
              <label>Phone
                <input value={c.phone} maxLength={30}
                  onChange={(e) => setContactField(i, "phone", e.target.value)} />
              </label>
              <label>Contact type
                <select value={c.contact_type}
                  onChange={(e) => setContactField(i, "contact_type", e.target.value)}>
                  <option value="general">General</option>
                  <option value="billing">Billing</option>
                  <option value="technical">Technical</option>
                  <option value="legal">Legal</option>
                  <option value="other">Other</option>
                </select>
              </label>
            </div>
            <div className="contact-actions">
              <label className="inline">
                <input type="radio" name="primary" checked={c.is_primary} onChange={() => makePrimary(i)} />
                Primary contact
              </label>
              <button type="button" className="btn small danger" onClick={() => removeContact(i)}>
                Remove
              </button>
            </div>
          </div>
        ))}
        <button type="button" className="btn"
          onClick={() => setContacts([...contacts, { ...emptyContact, is_primary: contacts.length === 0 }])}>
          + Add contact
        </button>
      </fieldset>

      <div className="form-actions">
        <button className="btn primary" disabled={saving}>
          {saving ? "Saving…" : isEdit ? "Save changes" : "Submit"}
        </button>
        <Link to="/" className="btn">Cancel</Link>
      </div>
    </form>
  );
}