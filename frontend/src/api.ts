import axios from 'axios'

const API_URL = (import.meta && import.meta.env && import.meta.env.VITE_API_URL) ? import.meta.env.VITE_API_URL : 'http://127.0.0.1:5001'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('ft_access_token')
  if (token) cfg.headers = { ...cfg.headers, Authorization: `Bearer ${token}` }
  return cfg
})

export function setToken(token: string | null){
  if (token) localStorage.setItem('ft_access_token', token)
  else localStorage.removeItem('ft_access_token')
}

export default api
