import { Link, Outlet, Route, Routes } from "react-router-dom";
import { ProtectedRoute, useAuth } from "./auth.jsx";
import Login from "./pages/Login.jsx";
import OrganisationList from "./pages/OrganisationList.jsx";
import OrganisationForm from "./pages/OrganisationForm.jsx";
import Users from "./pages/Users.jsx";

function Header() {
  const { user, logout } = useAuth();
  return (
    <header className="topbar">
      <Link to="/" className="brand">Client Onboarding Portal</Link>
      {user && (
        <div className="topbar-right">
          <span className="user-label">{user.full_name} ({user.role})</span>
          {user.role === "admin" && <Link to="/users" className="btn">Users</Link>}
          <Link to="/organisations/new" className="btn">+ New Client</Link>
          <button className="btn" onClick={logout}>Log out</button>
        </div>
      )}
    </header>
  );
}

export default function App() {
  return (
    <>
      <Header />
      <main className="container">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute><Outlet /></ProtectedRoute>}>
            <Route path="/" element={<OrganisationList />} />
            <Route path="/organisations/new" element={<OrganisationForm />} />
            <Route path="/organisations/:id/edit" element={<OrganisationForm />} />
            <Route path="/users" element={<Users />} />
          </Route>
          <Route path="*" element={<p>Page not found.</p>} />
        </Routes>
      </main>
    </>
  );
}