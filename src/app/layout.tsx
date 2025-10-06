import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Header } from '@/components/layout/Header'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NBA Fantasy Insights Bot',
  description: 'Real-time insights for your ESPN Fantasy Basketball team',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="relative min-h-screen bg-background">
          <Header />
          {children}
        </div>
      </body>
    </html>
  )
}