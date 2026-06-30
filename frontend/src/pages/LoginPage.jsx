import { Database, LockKeyhole, UserRound } from "lucide-react";
import { useState } from "react";

import { loginUser, setupUser } from "../api/client.js";

export default function LoginPage({ setupRequired, onAuthenticated }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    if (setupRequired && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const user = setupRequired
        ? await setupUser(username, email, password)
        : await loginUser(username, password);
      onAuthenticated(user);
    } catch (exc) {
      setError(exc.message || "Unable to sign in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-brand-panel">
        <div className="login-brand">
          <img className="wellscout-logo" src="/assets/wellscout-logo-light.png" alt="WellScout Innovative Exploration" />
          <div className="tti-endorsement">
            <span>Technology by</span>
            <img className="tti-logo" src="/assets/tti-logo-transparent.png" alt="Terralog Technologies Inc." />
          </div>
        </div>
        <div>
          <Database size={28} />
          <h1>Well Production Management</h1>
          <p>Secure access to mapped well data, imports, and operational dashboards.</p>
        </div>
      </section>
      <section className="login-form-panel">
        <form className="login-form" onSubmit={submit}>
          <div>
            <p className="eyebrow">{setupRequired ? "Initial setup" : "Secure access"}</p>
            <h2>{setupRequired ? "Create administrator" : "Sign in"}</h2>
            <p>{setupRequired ? "Create the first account for this application." : "Enter your account credentials to continue."}</p>
          </div>
          {error && <div className="notice">{error}</div>}
          <label className="field">
            <span>Username</span>
            <div className="input-with-icon"><UserRound size={17} /><input autoFocus required value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></div>
          </label>
          {setupRequired && <label className="field"><span>Email</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" /></label>}
          <label className="field">
            <span>Password</span>
            <div className="input-with-icon"><LockKeyhole size={17} /><input required type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={setupRequired ? "new-password" : "current-password"} /></div>
          </label>
          {setupRequired && <label className="field"><span>Confirm password</span><input required type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" /></label>}
          <button className="primary-command login-submit" disabled={submitting}>{submitting ? "Please wait..." : setupRequired ? "Create account" : "Sign in"}</button>
        </form>
      </section>
    </main>
  );
}