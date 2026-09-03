import React, {useEffect, useState} from 'react'
import api, { setToken } from '../services/api'
import { Link } from 'react-router-dom'

export default function Dashboard(){
  const [user, setUser] = useState<any>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState({ accounts: 0, balance: 0, transactions: 0, budgetSpent: 0 })

  useEffect(()=>{
    api.get('/api/auth/me').then(r=>{
      setUser(r.data)
      return Promise.all([api.get('/api/accounts'), api.get('/api/transactions'), api.get('/api/budgets')])
    }).then(([accounts, transactions, budgets])=>{
      const accountItems = accounts.data.data.accounts || []
      setSummary({
        accounts: accountItems.length,
        balance: accountItems.reduce((total: number, account: any) => total + Number(account.balance || 0), 0),
        transactions: transactions.data.data.total || 0,
        budgetSpent: Number(budgets.data.data.spent || 0),
      })
    }).catch(()=>setUser(null))
  },[])

  async function login(e: React.FormEvent){
    e.preventDefault(); setError(null)
    try{
      const res = await api.post('/api/auth/login', { email, password })
      setToken(res.data.token)
      setUser(res.data.user)
    }catch(err:any){ setError(err?.response?.data?.msg || 'login failed') }
  }

  async function register(e: React.FormEvent){
    e.preventDefault(); setError(null)
    try{
      const res = await api.post('/api/auth/register', { email, password, name })
      setToken(res.data.token)
      setUser(res.data.user)
    }catch(err:any){ setError(err?.response?.data?.msg || 'register failed') }
  }

  async function logout(){
    try{ await api.post('/api/auth/logout') }catch(_){}
    setToken(null); setUser(null)
  }

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-2">Ledgerly</h1>
      {user ? (
        <div>
          <div className="mb-6 text-slate-600">Welcome back, <strong>{user.name || user.email}</strong></div>
          <div className="grid gap-3 sm:grid-cols-4 mb-6">
            <div className="border rounded p-4"><div className="text-sm text-slate-500">Balance</div><strong>{summary.balance.toFixed(2)} NGN</strong></div>
            <div className="border rounded p-4"><div className="text-sm text-slate-500">Accounts</div><strong>{summary.accounts}</strong></div>
            <div className="border rounded p-4"><div className="text-sm text-slate-500">Transactions</div><strong>{summary.transactions}</strong></div>
            <div className="border rounded p-4"><div className="text-sm text-slate-500">Budget spent</div><strong>{summary.budgetSpent.toFixed(2)} NGN</strong></div>
          </div>
          <nav className="mb-6 flex gap-3 flex-wrap">
            <Link to="/accounts" className="px-4 py-2 rounded bg-blue-600 text-white">Accounts</Link>
            <Link to="/transactions" className="px-4 py-2 rounded bg-blue-600 text-white">Transactions</Link>
            <Link to="/budgets" className="px-4 py-2 rounded bg-blue-600 text-white">Budgets</Link>
          </nav>
          <button onClick={logout} className="px-3 py-2 bg-red-500 text-white rounded">Logout</button>
        </div>
      ) : (
        <div>
          <form onSubmit={login} className="mb-4">
            <div className="mb-2">
              <input className="border p-2 w-full" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
            </div>
            <div className="mb-2">
              <input type="password" className="border p-2 w-full" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
            </div>
            <button className="px-3 py-2 bg-blue-600 text-white rounded" type="submit">Login</button>
          </form>

          <div className="border-t pt-4">
            <h2 className="font-semibold mb-2">Register</h2>
            <form onSubmit={register}>
              <div className="mb-2"><input className="border p-2 w-full" placeholder="Name" value={name} onChange={e=>setName(e.target.value)} /></div>
              <div className="mb-2"><input className="border p-2 w-full" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} /></div>
              <div className="mb-2"><input type="password" className="border p-2 w-full" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} /></div>
              <button className="px-3 py-2 bg-green-600 text-white rounded" type="submit">Create account</button>
            </form>
          </div>

          {error && <div className="mt-4 text-red-600">{error}</div>}
        </div>
      )}
    </div>
  )
}
