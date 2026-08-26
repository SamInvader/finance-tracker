import React, {useEffect, useState} from 'react'
import api, { setToken } from '../api'

export default function Dashboard(){
  const [user, setUser] = useState<any>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(()=>{
    api.get('/api/auth/me').then(r=>setUser(r.data)).catch(()=>setUser(null))
  },[])

  async function login(e: React.FormEvent){
    e.preventDefault(); setError(null)
    try{
      const res = await api.post('/api/auth/login', { email, password })
      setToken(res.data.access_token)
      setUser(res.data.user)
    }catch(err:any){ setError(err?.response?.data?.msg || 'login failed') }
  }

  async function register(e: React.FormEvent){
    e.preventDefault(); setError(null)
    try{
      const res = await api.post('/api/auth/register', { email, password, name })
      setToken(res.data.access_token)
      setUser(res.data.user)
    }catch(err:any){ setError(err?.response?.data?.msg || 'register failed') }
  }

  async function logout(){
    try{ await api.post('/api/auth/logout') }catch(_){}
    setToken(null); setUser(null)
  }

  return (
    <div className="p-6 max-w-xl">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      {user ? (
        <div>
          <div className="mb-4">Welcome, <strong>{user.name || user.email}</strong></div>
          <nav className="mb-4 space-x-3">
            <a href="/accounts" className="text-blue-600">Accounts</a>
            <a href="/transactions" className="text-blue-600">Transactions</a>
            <a href="/budgets" className="text-blue-600">Budgets</a>
          </nav>
          <pre className="mb-4">{JSON.stringify(user,null,2)}</pre>
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
