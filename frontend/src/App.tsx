import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Accounts from './pages/Accounts'
import Budgets from './pages/Budgets'

export default function App(){
  return (
    <Routes>
      <Route path="/" element={<Dashboard/>} />
      <Route path="/transactions" element={<Transactions/>} />
      <Route path="/accounts" element={<Accounts/>} />
      <Route path="/budgets" element={<Budgets/>} />
    </Routes>
  )
}
