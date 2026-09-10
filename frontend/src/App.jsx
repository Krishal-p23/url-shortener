import { useState } from "react";

import { getAnalytics, shortenUrl } from "./api";

function App() {
  const [url, setUrl] = useState("");
  const [createdUrl, setCreatedUrl] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setAnalytics(null);
    try {
      const result = await shortenUrl(url.trim());
      setCreatedUrl(result);
      setUrl("");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalytics() {
    if (!createdUrl) return;
    setAnalyticsLoading(true);
    setMessage("");
    try {
      setAnalytics(await getAnalytics(createdUrl.short_code));
    } catch (error) {
      setMessage(error.message);
    } finally {
      setAnalyticsLoading(false);
    }
  }

  async function copyShortUrl() {
    if (!createdUrl) return;
    await navigator.clipboard.writeText(createdUrl.short_url);
    setMessage("Short URL copied.");
  }

  return (
    <main className="page-shell">
      <section className="panel">
        <p className="eyebrow">Hardware Distributed URL Shortener</p>
        <h1>Make a long link easier to share.</h1>
        <form onSubmit={handleSubmit} className="shorten-form">
          <label htmlFor="url">Long URL</label>
          <div className="input-row">
            <input
              id="url"
              type="url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://example.com/article"
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? "Shortening..." : "Shorten URL"}
            </button>
          </div>
        </form>

        {message && <p className="message" role="alert">{message}</p>}

        {createdUrl && (
          <section className="result" aria-live="polite">
            <span className="result-label">Your short URL</span>
            <a href={createdUrl.short_url} target="_blank" rel="noreferrer">
              {createdUrl.short_url}
            </a>
            <div className="actions">
              <button type="button" onClick={copyShortUrl}>Copy</button>
              <button type="button" onClick={handleAnalytics} disabled={analyticsLoading}>
                {analyticsLoading ? "Loading..." : "View analytics"}
              </button>
            </div>
          </section>
        )}

        {analytics && (
          <section className="analytics">
            <h2>Analytics</h2>
            <p className="click-total">{analytics.total_clicks} total clicks</p>
            {analytics.recent_clicks.length > 0 ? (
              <ul>
                {analytics.recent_clicks.map((click, index) => (
                  <li key={`${click.clicked_at}-${index}`}>
                    <span>{new Date(click.clicked_at).toLocaleString()}</span>
                    <small>{click.user_agent || "Unknown browser"}</small>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No clicks recorded yet.</p>
            )}
          </section>
        )}
      </section>
    </main>
  );
}

export default App;