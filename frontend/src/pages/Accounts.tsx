import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { Link } from 'react-router-dom'

type Acct = {
  id: number
  name: string
  balance: number
  currency?: string
}

export default function Accounts(){
  const [accounts, setAccounts] = useState<Acct[]>([])
  const [error, setError] = useState('')
  const [name, setName] = useState('')
  const [balance, setBalance] = useState('0')

  async function addAccount(e: React.FormEvent) {
    e.preventDefault()
    try {
      const response = await api.post('/api/accounts', { name, balance: Number(balance), type: 'cash' })
      setAccounts(current => [...current, response.data.data])
      setName('')
      setBalance('0')
      setError('')
    } catch { setError('Could not add account') }
  }

  useEffect(()=>{
    api.get('/api/accounts').then(r=> setAccounts(r.data.data.accounts)).catch(() => setError('Could not load accounts'))
  },[])

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Accounts</h2>
        <Link to="/" className="text-sm text-blue-600">Back</Link>
      </div>
      {error && <p className="mb-3 text-red-600">{error}</p>}
      <form onSubmit={addAccount} className="mb-5 flex flex-wrap gap-2">
        <input className="border p-2 rounded" placeholder="Account name" value={name} onChange={e=>setName(e.target.value)} required />
        <input className="border p-2 rounded w-32" type="number" step="0.01" placeholder="Balance" value={balance} onChange={e=>setBalance(e.target.value)} />
        <button className="px-3 py-2 rounded bg-green-600 text-white">Add account</button>
      </form>
      {!error && accounts.length === 0 && <p className="text-slate-500">No accounts yet. Add your first account to start tracking your money.</p>}
      <ul>
        {accounts.map(a=> (
          <li key={a.id} className="py-2 border-b">
            <div className="flex justify-between">
              <div>{a.name}</div>
              <div>{a.balance} {a.currency}</div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
