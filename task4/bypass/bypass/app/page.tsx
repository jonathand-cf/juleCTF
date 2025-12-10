export default function Home() {
    return (
        <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', background: '#fffafa',borderRadius: '16px', boxShadow: '0 0 20px rgba(0,0,0,0.1)'}}>
            <h1
                style={{fontSize: '2.8rem',marginBottom: '1.5rem',color: '#b30000',textAlign: 'center'}}>🎅 Santa's Packet Database 🎄</h1>

            <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
                <h2 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#006400' }}>🎁 Secure Packet Area 🎁</h2>
                <p style={{ fontSize: '1.2rem', lineHeight: 1.6 }}>
                    The secret santa list is only of authenticated users 🔒

                    <a href="/protected" style={{ color: '#0070f3', textDecoration: 'none', marginLeft: '0.3rem' }}>/protected</a> 🔒

                </p>
            </div>

            <div style={{ textAlign: 'center', fontSize: '2rem' }}>
                ❄️⛄🎄🎅✨
            </div>
        </div>
    );
}