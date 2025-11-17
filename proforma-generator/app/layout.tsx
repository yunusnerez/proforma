import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Proforma Invoice Generator',
  description: 'Generate professional proforma invoices with deposit',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

