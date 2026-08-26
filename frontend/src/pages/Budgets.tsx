import React, { useEffect, useState } from 'react'
import api from '../api'
import { Link } from 'react-router-dom'

type Budget = { id: number; month: string; category_id: number; amount: number }

function SimpleBarChart({data}:{data:Budget[]}){
  const max = Math.max(1, ...data.map(d=>d.amount))
  return (
    <svg width="100%" height={data.length*28}>
      {data.map((d,i)=> (
        <g key={d.id} transform={`translate(0, ${i*28})`}>
          <rect x={120} y={4} width={`${(d.amount/max)*60}%`} height={20} fill="#60a5fa" />
          <text x={8} y={18} fontSize={12}>{d.month}</text>
          <text x={200} y={18} fontSize={12}>{d.amount}</text>
        </g>
      ))}
    </svg>
  )
}

export default function Budgets(){
  const [items, setItems] = useState<Budget[]>([])

  useEffect(()=>{
    api.get('/api/budgets/').then(r=> setItems(r.data)).catch(console.error)
  },[])

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Budgets</h2>
        <Link to="/" className="text-sm text-blue-600">Back</Link>
      </div>
      <SimpleBarChart data={items} />
      <ul className="mt-4">
        {items.map(b=> (
          <li key={b.id} className="py-2 border-b flex justify-between">
            <div>{b.month} (cat {b.category_id})</div>
            <div>{b.amount}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
