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

  useEffect(()=>{
    api.get('/api/accounts/').then(r=> setAccounts(r.data)).catch(console.error)
  },[])

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Accounts</h2>
        <Link to="/" className="text-sm text-blue-600">Back</Link>
      </div>
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
