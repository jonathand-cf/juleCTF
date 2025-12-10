import * as fs from 'fs';

let flag: string = "JUL{FAKEFLAG}";
export default function ProtectedPage() {
    const filePath: string = 'flag.txt';
    try {
        flag = fs.readFileSync(filePath, 'utf-8');
    } catch (error) {
        console.error('Error reading file:', error);
    }

    return (
        <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', background: '#fffafa', borderRadius: '16px', boxShadow: '0 0 20px rgba(0,0,0,0.1)' }}>
            <h1
                style={{ fontSize: '2.8rem', marginBottom: '1.5rem', color: '#b30000', textAlign: 'center' }}>🎅 Santa's Packet Database 🎄</h1>

            <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
                <h2 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#006400' }}>🎁 Secure Packet Area 🎁</h2>
                <p style={{ fontSize: '1.2rem', lineHeight: 1.6 }}>
                    🎅 HoHoHo! Santa's secret list 🎄
                    <code
                        style={{
                            background: '#fff0f0',
                            border: '2px solid #b30000',
                            color: '#006400',
                            padding: '0.4rem 0.6rem',
                            borderRadius: '8px',
                            fontSize: '0.7rem',
                            fontFamily: 'monospace',
                            boxShadow: '0 0 10px rgba(0,0,0,0.15)',
                            display: 'inline-block'
                        }}
                    >
                        Candy Cane Care Packet (Peppermint candy canes, Hot cocoa sachet and Mini marshmallows)<br/>
                        Cozy Winter Warmth Packet (Fuzzy Christmas socks, Hot cider mix and Cinnamon-scented candle)<br/>
                        Santa’s Secret Packet (Small wooden toy, {flag} and Elf-approved-glue)<br/>
                        Reindeer Snack Packet (Carrot gummies, A tiny sleigh bell and Feeding instructions signed by Rudolph)<br/>
                    </code>

                </p>
            </div>

            <div style={{ textAlign: 'center', fontSize: '2rem' }}>
                ❄️⛄🎄🎅✨
            </div>
        </div>
    );

}

