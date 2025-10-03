import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
axios.defaults.timeout = 10000

export async function login(email, password){
  const params = new URLSearchParams()
  params.append('username', email)
  params.append('password', password)
  const res = await axios.post(`${API}/token`, params)
  return res.data
}

export async function getMe(token){
  const res = await axios.get(`${API}/me`, { headers: { Authorization: `Bearer ${token}` } })
  return res.data
}

export async function fetchMetrics(token, params){
  const res = await axios.get(`${API}/metrics`, { params, headers: { Authorization: `Bearer ${token}` } })
  return res.data
}
