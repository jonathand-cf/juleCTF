import type { Metadata } from 'next'


export const metadata: Metadata = {
  title: 'santas packet database',
  description: 'this is where santa keeps the database of all packets. its only for authenticated users. hopefully, noone is able to bypass our authentication without the (C)orrect (V)ital (E)vidence in the middle.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <main style={{ maxWidth: '1000px', margin: '0 auto', padding: '20px' }}>      
            <header>
                <title>🎅 Santa's Packet Database 🎄</title> 
            </header>
          {children}
        </main>
      </body>
    </html>
  )
} 
