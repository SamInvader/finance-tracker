import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { Link } from 'react-router-dom'

type Tx = {
  id: number
  amount: number
  type: string
  date: string
  description?: string
  account_id?: number
}

export default function Transactions(){
  const [txs, setTxs] = useState<Tx[]>([])
  const [error, setError] = useState('')
  const [accounts, setAccounts] = useState<{id:number; name:string}[]>([])
  const [categories, setCategories] = useState<{id:number; name:string; kind:string}[]>([])
  const [form, setForm] = useState({ type: 'expense', amount: '', description: '', account_id: '' , category_id: ''})

  async function load() {
    try {
      const [txResponse, accountResponse, categoryResponse] = await Promise.all([api.get('/api/transactions'), api.get('/api/accounts'), api.get('/api/categories')])
      setTxs(txResponse.data.data.items)
      setAccounts(accountResponse.data.data.accounts)
      setCategories(categoryResponse.data.data)
    } catch { setError('Could not load transactions') }
  }

  async function addTransaction(e: React.FormEvent) {
    e.preventDefault()
    try {
      await api.post('/api/transactions', { ...form, amount: Number(form.amount), account_id: Number(form.account_id), category_id: form.category_id ? Number(form.category_id) : undefined, date: new Date().toISOString().slice(0, 10) })
      setForm(current => ({ ...current, amount: '', description: '' }))
      await load()
      setError('')
    } catch (err: any) { setError(err?.response?.data?.error || 'Could not add transaction') }
  }

  useEffect(()=>{
    load()
  },[])

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Transactions</h2>
        <Link to="/" className="text-sm text-blue-600">Back</Link>
      </div>
      {error && <p className="mb-3 text-red-600">{error}</p>}
      <form onSubmit={addTransaction} className="mb-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
        <select className="border p-2 rounded" value={form.type} onChange={e=>setForm({...form, type:e.target.value, category_id:''})}><option value="expense">Expense</option><option value="income">Income</option></select>
        <input className="border p-2 rounded" type="number" step="0.01" min="0.01" placeholder="Amount" value={form.amount} onChange={e=>setForm({...form, amount:e.target.value})} required />
        <input className="border p-2 rounded" placeholder="Description" value={form.description} onChange={e=>setForm({...form, description:e.target.value})} />
        <select className="border p-2 rounded" value={form.account_id} onChange={e=>setForm({...form, account_id:e.target.value})} required><option value="">Account</option>{accounts.map(a=><option key={a.id} value={a.id}>{a.name}</option>)}</select>
        <select className="border p-2 rounded" value={form.category_id} onChange={e=>setForm({...form, category_id:e.target.value})}><option value="">Category</option>{categories.filter(c=>c.kind===form.type).map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select>
        <button className="px-3 py-2 rounded bg-green-600 text-white">Add transaction</button>
      </form>
      {!error && txs.length === 0 && <p className="text-slate-500">No transactions yet. Add an account before recording your first transaction.</p>}
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th className="px-4 py-2">Date</th>
            <th className="px-4 py-2">Desc</th>
            <th className="px-4 py-2">Amount</th>
            <th className="px-4 py-2">Type</th>
          </tr>
        </thead>
        <tbody>
          {txs.map(t=> (
            <tr key={t.id} className="border-t">
              <td className="px-4 py-2">{new Date(t.date).toLocaleString()}</td>
              <td className="px-4 py-2">{t.description}</td>
              <td className="px-4 py-2">{t.amount}</td>
              <td className="px-4 py-2">{t.type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
