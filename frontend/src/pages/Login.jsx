import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, getMe } from '../api'
import { Box, TextField, Button, Typography, Paper, Alert, CircularProgress } from '@mui/material'

export default function Login({ onLogin }){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const submit = async (e) =>{
    e.preventDefault()
    setError(null)
    setLoading(true)
    try{
      const data = await login(email, password)
      localStorage.setItem('token', data.access_token)
      const me = await getMe(data.access_token)
      onLogin(me)
      navigate('/dashboard')
    }catch(err){
      setError(err?.response?.data?.detail || 'Login failed')
    }
    setLoading(false)
  }

  return (
    <Paper style={{padding:20, marginTop:40}}>
      <Typography variant="h5" gutterBottom>Login</Typography>
      <Box component="form" onSubmit={submit}>
        <TextField label="Email" value={email} onChange={e=>setEmail(e.target.value)} fullWidth margin="normal" />
        <TextField label="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} fullWidth margin="normal" />
        {error && <Alert severity="error" sx={{my:1}}>{error}</Alert>}
        <Button type="submit" variant="contained" sx={{mt:2}} disabled={loading}>
          {loading ? <CircularProgress size={20} color="inherit" /> : 'Login'}
        </Button>
      </Box>
    </Paper>
  )
}
