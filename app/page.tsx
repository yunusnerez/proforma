'use client'

import { useState } from 'react'

interface InvoiceItem {
  item: string
  quantity: number
  rate: number
  note: string
}

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    title: 'Invoice',
    invoice_date: new Date().toISOString().split('T')[0],
    billed_by: 'You Clinic\nTurkey\nKazimdirik Mah. 296. Sok. No: 8 D:315\nIzmir, Turkey',
    billed_to: '',
    cash_note: 'Payment will be done in cash',
    currency: '£',
    show_quantity: true,
    show_rate: false,
    show_amount: true,
    deposit: 0,
    items: [
      {
        item: 'Autism Treatment Package',
        quantity: 1,
        rate: 0,
        note: ''
      }
    ] as InvoiceItem[]
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'deposit' || name === 'show_quantity' || name === 'show_rate' || name === 'show_amount'
        ? name.startsWith('show_') ? (e.target as HTMLInputElement).checked : parseFloat(value) || 0
        : value
    }))
  }

  const handleItemChange = (index: number, field: keyof InvoiceItem, value: string | number) => {
    const newItems = [...formData.items]
    newItems[index] = {
      ...newItems[index],
      [field]: field === 'quantity' || field === 'rate' ? parseFloat(value as string) || 0 : value
    }
    setFormData(prev => ({ ...prev, items: newItems }))
  }

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { item: '', quantity: 1, rate: 0, note: '' }]
    }))
  }

  const removeItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Failed to generate PDF' }))
        throw new Error(errorData.error || 'Failed to generate PDF')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `invoice_${new Date().getTime()}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      setSuccess('PDF generated successfully!')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Proforma Invoice Generator</h1>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="invoice_date">Invoice Date</label>
            <input
              type="date"
              id="invoice_date"
              name="invoice_date"
              value={formData.invoice_date}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="currency">Currency</label>
            <input
              type="text"
              id="currency"
              name="currency"
              value={formData.currency}
              onChange={handleInputChange}
              placeholder="£, $, €"
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="billed_by">Billed By</label>
          <textarea
            id="billed_by"
            name="billed_by"
            value={formData.billed_by}
            onChange={handleInputChange}
            required
            placeholder="Company Name&#10;Country"
          />
        </div>

        <div className="form-group">
          <label htmlFor="billed_to">Billed To</label>
          <textarea
            id="billed_to"
            name="billed_to"
            value={formData.billed_to}
            onChange={handleInputChange}
            required
            placeholder="Client Name&#10;Country"
          />
        </div>

        <div className="form-group">
          <label htmlFor="deposit">Deposit Amount</label>
          <input
            type="number"
            id="deposit"
            name="deposit"
            value={formData.deposit}
            onChange={handleInputChange}
            step="0.01"
            min="0"
          />
        </div>

        <div className="form-group">
          <label htmlFor="cash_note">Cash Note (Optional)</label>
          <input
            type="text"
            id="cash_note"
            name="cash_note"
            value={formData.cash_note}
            onChange={handleInputChange}
          />
        </div>

        <div className="checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="show_quantity"
              checked={formData.show_quantity}
              onChange={handleInputChange}
            />
            Show Quantity
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="show_rate"
              checked={formData.show_rate}
              onChange={handleInputChange}
            />
            Show Rate
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="show_amount"
              checked={formData.show_amount}
              onChange={handleInputChange}
            />
            Show Amount
          </label>
        </div>

        <div className="items-section">
          <h2>Items</h2>
          {formData.items.map((item, index) => (
            <div key={index} className="item-row">
              <div className="form-group">
                <label>Item Name</label>
                <input
                  type="text"
                  value={item.item}
                  onChange={(e) => handleItemChange(index, 'item', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input
                  type="number"
                  value={item.quantity}
                  onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                  step="1"
                  min="1"
                  required
                />
              </div>
              <div className="form-group">
                <label>Rate</label>
                <input
                  type="number"
                  value={item.rate}
                  onChange={(e) => handleItemChange(index, 'rate', e.target.value)}
                  step="0.01"
                  min="0"
                  required
                />
              </div>
              <div className="form-group">
                <label>Note (Optional)</label>
                <input
                  type="text"
                  value={item.note}
                  onChange={(e) => handleItemChange(index, 'note', e.target.value)}
                />
              </div>
              {formData.items.length > 1 && (
                <button
                  type="button"
                  className="remove-item-btn"
                  onClick={() => removeItem(index)}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button type="button" className="add-item-btn" onClick={addItem}>
            Add Item
          </button>
        </div>

        <button type="submit" className="generate-btn" disabled={loading}>
          {loading ? 'Generating PDF...' : 'Generate PDF'}
        </button>

        {loading && <div className="loading">Please wait while generating your invoice...</div>}
        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}
      </form>
    </div>
  )
}

