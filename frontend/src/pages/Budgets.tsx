import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { Link } from 'react-router-dom'

type Budget = { id: number; month: string; category_id: number; category_name?: string; amount: number; spent?: number; remaining?: number; percent_used?: number }

function SimpleBarChart({data}:{data:Budget[]}){
  const max = Math.max(1, ...data.map(d=>d.amount))
  return (
    <svg width="100%" height={data.length*28}>
      {data.map((d,i)=> (
        <g key={d.id} transform={`translate(0, ${i*28})`}>
          <rect x={120} y={4} width={`${(d.amount/max)*60}%`} height={20} fill="#60a5fa" />
          <text x={8} y={18} fontSize={12}>{d.category_name || d.month}</text>
          <text x={200} y={18} fontSize={12}>{d.spent || 0} / {d.amount}</text>
        </g>
      ))}
    </svg>
  )
}

export default function Budgets(){
  const [items, setItems] = useState<Budget[]>([])
  const [error, setError] = useState('')
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7))
  const [limit, setLimit] = useState('')
  const [categories, setCategories] = useState<{id:number; name:string}[]>([])
  const [categoryId, setCategoryId] = useState('')

  async function load() {
    try {
      const [budgetResponse, categoryResponse] = await Promise.all([api.get(`/api/budgets?month=${month}`), api.get('/api/categories')])
      setItems(budgetResponse.data.data.categories)
      setCategories(categoryResponse.data.data.filter((category: any) => category.kind === 'expense'))
    } catch { setError('Could not load budgets') }
  }

  async function saveBudget(e: React.FormEvent) {
    e.preventDefault()
    try {
      await api.post('/api/budgets', { month, overall_limit: Number(limit), categories: categoryId ? [{ category_id: Number(categoryId), amount: Number(limit) }] : [] })
      await load()
      setError('')
    } catch (err: any) { setError(err?.response?.data?.error || 'Could not save budget') }
  }

  useEffect(()=>{
    load()
  },[])

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Budgets</h2>
        <Link to="/" className="text-sm text-blue-600">Back</Link>
      </div>
      {error && <p className="mb-3 text-red-600">{error}</p>}
      <form onSubmit={saveBudget} className="mb-5 flex flex-wrap gap-2">
        <input className="border p-2 rounded" type="month" value={month} onChange={e=>setMonth(e.target.value)} />
        <input className="border p-2 rounded" type="number" step="0.01" min="0.01" placeholder="Limit" value={limit} onChange={e=>setLimit(e.target.value)} required />
        <select className="border p-2 rounded" value={categoryId} onChange={e=>setCategoryId(e.target.value)}><option value="">Overall budget</option>{categories.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select>
        <button className="px-3 py-2 rounded bg-green-600 text-white">Save budget</button>
      </form>
      {!error && items.length === 0 && <p className="text-slate-500">No budgets yet. Create a budget to see category limits here.</p>}
      <SimpleBarChart data={items} />
      <ul className="mt-4">
        {items.map(b=> (
          <li key={b.id} className="py-2 border-b flex justify-between">
            <div>{b.category_name || `Category ${b.category_id}`}</div>
            <div>{b.spent || 0} / {b.amount} NGN</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
