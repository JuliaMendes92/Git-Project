import React, { useEffect, useState } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import { getMe } from './api'
import { CssBaseline, Container } from '@mui/material'

export default function App(){
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(()=>{
    const token = localStorage.getItem('token')
    if(token){
      getMe(token).then(u=>{
        setUser(u)
        navigate('/dashboard')
      }).catch(()=>{
        localStorage.removeItem('token')
      })
    } else {
      navigate('/login')
    }
  }, [])

  return (
    <>
      <CssBaseline />
      <Container maxWidth="lg">
        <Routes>
          <Route path="/login" element={<Login onLogin={(u)=>{setUser(u)}} />} />
          <Route path="/dashboard" element={<Dashboard user={user} />} />
          <Route path="/" element={<Login onLogin={(u)=>{setUser(u)}} />} />
        </Routes>
      </Container>
    </>
  )
}
