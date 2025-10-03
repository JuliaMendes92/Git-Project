import React, { useEffect, useState, useMemo } from 'react'
import { fetchMetrics, getMe } from '../api'
import { Box, Typography, Button, TextField, Paper, Table, TableHead, TableRow, TableCell, TableBody, TableContainer, TableSortLabel, Stack, Alert, CircularProgress } from '@mui/material'
import dayjs from 'dayjs'
import { useNavigate } from 'react-router-dom'

export default function Dashboard({ user }){
  const [metrics, setMetrics] = useState([])
  const [token] = useState(localStorage.getItem('token'))
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [sortBy, setSortBy] = useState(null)
  const [sortDir, setSortDir] = useState('asc')
  const [loading, setLoading] = useState(false)
  const [me, setMe] = useState(user)

  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(100)
  const [total, setTotal] = useState(0)
  const navigate = useNavigate()

  useEffect(()=>{
    if(!me && token){
      getMe(token).then(setMe).catch(()=>{})
    }
    load(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const load = async (p = 1) =>{
    setLoading(true)
    try{
      const params = {}
      if(start) params.start_date = start
      if(end) params.end_date = end
      if(sortBy) params.sort_by = sortBy
      if(sortDir) params.sort_dir = sortDir
      params.page = p
      params.page_size = pageSize
      const res = await fetchMetrics(token, params)
      setMetrics(res.data || [])
      setPage(res.page || p)
      setPageSize(res.page_size || pageSize)
      setTotal(res.total || 0)
    }catch(err){
      console.error(err)
      // show error
    
    }finally{setLoading(false)}
  }

  const columns = useMemo(()=>{
    const base = [
      {key:'account_id', label:'Account'},
      {key:'date', label:'Date'},
      {key:'impressions', label:'Impressions'},
      {key:'clicks', label:'Clicks'},
      {key:'conversions', label:'Conversions'},
    ]
    if(me?.role === 'admin') base.push({key:'cost_micros', label:'Cost (micros)'})
    return base
  }, [me])

  const handleSort = (col) =>{
    if(sortBy === col){
      setSortDir(prev => prev === 'asc' ? 'desc' : 'asc')
    }else{
      setSortBy(col)
      setSortDir('asc')
    }
    load(1)
  }

  // reload when filters or page change
  useEffect(()=>{
    load(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [start, end, sortBy, sortDir, pageSize])

  const handleLogout = () =>{
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <Box sx={{mt:4}}>
      <Typography variant="h4" gutterBottom>Metrics Dashboard</Typography>
      <Paper sx={{p:2, mb:2}}>
        <Stack direction="row" spacing={2} alignItems="center">
          <div>
            <Typography variant="subtitle2">Logged in as: {me?.full_name || me?.email} ({me?.role})</Typography>
          </div>
          <TextField label="Start date (YYYY-MM-DD)" value={start} onChange={e=>setStart(e.target.value)} sx={{mr:2}} />
          <TextField label="End date (YYYY-MM-DD)" value={end} onChange={e=>setEnd(e.target.value)} sx={{mr:2}} />
          <Button variant="contained" onClick={()=>load(1)}>Filter</Button>
          <Box sx={{flex:1}} />
          <Button variant="outlined" color="secondary" onClick={handleLogout}>Logout</Button>
        </Stack>
      </Paper>

      <TableContainer component={Paper}>
        {loading ? (
          <Box sx={{p:4, display:'flex', justifyContent:'center'}}><CircularProgress /></Box>
        ) : (
        <Table>
          <TableHead>
            <TableRow>
              {columns.map(c=> (
                <TableCell key={c.key}>
                  <TableSortLabel active={sortBy===c.key} direction={sortDir} onClick={()=>handleSort(c.key)}>
                    {c.label}
                  </TableSortLabel>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {metrics.map((r, idx)=> (
              <TableRow key={idx}>
                {columns.map(c=> (
                  <TableCell key={c.key}>{c.key === 'date' ? dayjs(r[c.key]).format('YYYY-MM-DD') : r[c.key]}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
        )}
      </TableContainer>

      <Box sx={{display:'flex', justifyContent:'space-between', alignItems:'center', mt:2}}>
        <Typography variant="body2">Page {page} — {total} rows</Typography>
        <div>
          <Button disabled={loading || page<=1} onClick={()=>{const p=page-1; setPage(p); load(p);}}>Previous</Button>
          <Button disabled={loading || page*pageSize>=total} onClick={()=>{const p=page+1; setPage(p); load(p);}}>Next</Button>
        </div>
      </Box>
    </Box>
  )
}
