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

  useEffect(()=>{
    api.get('/api/transactions/').then(r=> setTxs(r.data)).catch(console.error)
  },[])

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Transactions</h2>
        <Link to="/" className="text-sm text-blue-600">Back</Link>
      </div>
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
