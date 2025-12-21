'use client';
import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setResult('');
    if (!file) return setError('🎁 Santa needs a PKCS#12 file first!');

    setLoading(true);
    try {
      const form = new FormData();
      form.append('file', file);

      const res = await fetch('/api/upload', { method: 'POST', body: form });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || '❄️ Santa’s workshop rejected the gift');
      } else {
        setResult(data.encrypted);
      }
    } catch {
      setError('🔥 The elves broke something');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        minHeight: '100vh',
        padding: 32,
        background: 'linear-gradient(#0b1d3a, #123)',
        color: '#fff',
        fontFamily: 'system-ui, sans-serif',
      }}
    >
      <h1 style={{ fontSize: 36, marginBottom: 8 }}>
        🎅 Santa’s Secure Gift Exchange
      </h1>

      <p style={{ maxWidth: 800, opacity: 0.9 }}>
        Upload your <strong>PKCS#12 file</strong> and Santa will send you an <strong>encrypted Christmas present</strong>.
      </p>

        <div
            style={{
            marginTop: 24,
            padding: 16,
            borderRadius: 8,
            background: '#011f1aff',
            border: '1px solid #ff6b6b',
            maxWidth: 800,
            }}
        >
            🎅 <strong>Message from santa</strong>
            <br />
            The elves haven’t finished my password delivery system yet — it seems they might have borked it. Good thing the system doesn’t actually depend on the password to work.
        </div>      

      
      <form
        onSubmit={handleSubmit}
        style={{
          marginTop: 32,
          padding: 24,
          borderRadius: 12,
          background: 'rgba(255,255,255,0.08)',
          maxWidth: 800,
        }}
      >
        <label style={{ display: 'block', marginBottom: 8 }}>
          🎄 Choose your PKCS#12 file
        </label>

        <input
          type="file"
          accept=".p12,.pfx"
          onChange={e => setFile(e.target.files?.[0] || null)}
        />

        <br />
        <br />

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '10px 16px',
            fontSize: 16,
            borderRadius: 8,
            border: 'none',
            background: loading ? '#555' : '#c1121f',
            color: '#fff',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? '🎅 Santa is checking the list…' : '🎁 Send to Santa to receive your present!'}
        </button>
      </form>

      {error && (
        <div
            style={{
            marginTop: 24,
            padding: 16,
            borderRadius: 8,
            background: '#2b0000',
            border: '1px solid #ff6b6b',
            maxWidth: 800,
            }}
        >
            ⚠️ <strong>Santa encountered a problem with your file</strong>
            <br />
            {error}
        </div>
        )}

      {result && (
        <div
          style={{
            marginTop: 32,
            padding: 24,
            borderRadius: 12,
            background: '#0f5132',
            border: '1px solid #75b798',
            maxWidth: 800,
          }}
        >
          <h3 style={{ marginTop: 0 }}>
            🎁 Encrypted Message from Santa
          </h3>
          <p style={{ opacity: 0.9 }}>
            Only the rightful private key holder may open this present:
          </p>
          <pre
            style={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
              background: '#062c1f',
              padding: 16,
              borderRadius: 8,
              marginTop: 12,
            }}
          >
            {result}
          </pre>
        </div>
      )}

      <footer style={{ marginTop: 48, opacity: 0.6 }}>
        🎄 Built in Santa’s workshop · Cryptography may be hazardous to elves
      </footer>
    </main>
  );
}
