import { Database, LayoutDashboard, LogOut, TableProperties } from "lucide-react";
import { useEffect, useState } from "react";

import { fetchAuthStatus, logoutUser } from "./api/client.js";
import DataBrowser from "./pages/DataBrowser.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import Production from "./pages/Production.jsx";
import RawDataImport from "./pages/RawDataImport.jsx";
import WellDashboard from "./pages/WellDashboard.jsx";

const MODULES = {
  dashboard: "dashboard",
  production: "production",
  "data-import": "data-import",
  "data-browser": "data-browser",
};

function moduleFromHash() {
  const value = window.location.hash.replace("#", "");
  return MODULES[value] || "dashboard";
}

export default function App() {
  const [module, setModule] = useState(moduleFromHash);
  const [user, setUser] = useState(null);
  const [setupRequired, setSetupRequired] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [authError, setAuthError] = useState("");

  useEffect(() => {
    fetchAuthStatus()
      .then((status) => {
        setUser(status.authenticated ? status.user : null);
        setSetupRequired(Boolean(status.setup_required));
        setAuthError("");
      })
      .catch((error) => setAuthError(error.message || "Unable to connect to the authentication service."))
      .finally(() => setAuthLoading(false));
  }, []);

  useEffect(() => {
    const handleHashChange = () => setModule(moduleFromHash());
    window.addEventListener("hashchange", handleHashChange);
    if (!window.location.hash) window.history.replaceState(null, "", "#dashboard");
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  function openModule(nextModule) {
    window.location.hash = nextModule;
  }

  async function signOut() {
    await logoutUser();
    setUser(null);
    setSetupRequired(false);
  }

  if (authLoading) {
    return <main className="auth-loading"><span className="spinner" /><span>Checking secure session</span></main>;
  }

  if (!user) {
    return (
      <>
        {authError && <div className="auth-service-error notice">{authError}</div>}
        <LoginPage setupRequired={setupRequired} onAuthenticated={setUser} />
      </>
    );
  }

  return (
    <div className="platform-shell">
      <header className="platform-header">
        <div className="platform-brand">
          <span className="brand-mark">SP</span>
          <div>
            <strong>Saguaro Petroleum</strong>
            <small>Well Production Management</small>
          </div>
        </div>
        <nav className="module-navigation" aria-label="Platform sections">
          <button className={module === "dashboard" ? "selected" : ""} onClick={() => openModule("dashboard")}>
            <LayoutDashboard size={17} />
            <span><strong>Well Dashboard</strong><small>Map and well search</small></span>
          </button>
          <button className={module === "production" ? "selected" : ""} onClick={() => openModule("production")}>
            <LayoutDashboard size={17} />
            <span><strong>Production Modules</strong><small>Production metrics and reports</small></span>
          </button>
          <button className={module === "data-import" ? "selected" : ""} onClick={() => openModule("data-import")}>
            <Database size={17} />
            <span><strong>Raw Data Import</strong><small>Upload, map, and split</small></span>
          </button>
          <button className={module === "data-browser" ? "selected" : ""} onClick={() => openModule("data-browser")}>
            <TableProperties size={17} />
            <span><strong>Data Browser</strong><small>Tables and columns</small></span>
          </button>
        </nav>
        <div className="account-menu">
          <span><strong>{user.username}</strong><small>Signed in</small></span>
          <button type="button" className="icon-button" title="Sign out" aria-label="Sign out" onClick={signOut}><LogOut size={17} /></button>
        </div>
      </header>

      <section className="platform-module" aria-live="polite">
        {module === "dashboard" ? (
          <WellDashboard />
        ) : module === "production" ? (
          <Production />
        ) : module === "data-import" ? (
          <RawDataImport onDone={() => openModule("dashboard")} />
        ) : (
          <DataBrowser />
        )}
      </section>
    </div>
  );
}