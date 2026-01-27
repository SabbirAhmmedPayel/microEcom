import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/login'
import './App.css'

function App() {
  // Check if user is logged in by looking for the token in localStorage
  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Redirect home to login if not authenticated */}
        <Route 
          path="/" 
          element={isAuthenticated ? <h1>Welcome to Dashboard</h1> : <Navigate to="/login" />} 
        />

        {/* Catch-all route */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </div>
  )
}

export default App