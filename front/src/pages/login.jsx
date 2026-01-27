import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../style/login.css';

export default function AuthPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); // Clear previous errors

    // Choose endpoint based on current mode
    const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';
    
    try {
      const response = await fetch(`http://localhost:3000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();
      
      if (response.ok) {
        if (isRegister) {
          alert("Registration successful! You can now log in.");
          setIsRegister(false); // Switch to login mode
          setUsername('');
          setPassword('');
        } else {
          // Store JWT token for future requests
          localStorage.setItem('token', data.token);
          alert("Login successful!");
          navigate('/'); // Send user to the home/dashboard page
        }
      } else {
        setError(data.error || "Something went wrong. Please try again.");
      }
    } catch (err) {
      setError("Cannot connect to server. Is the Docker backend running?");
      console.error("Auth Error:", err);
    }
  };

  return (
    <div className="login-container">
      <h2>{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
      
      {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input 
            type="text" 
            value={username}
            placeholder="Enter username" 
            required 
            onChange={(e) => setUsername(e.target.value)} 
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input 
            type="password" 
            value={password}
            placeholder="Enter password" 
            required 
            onChange={(e) => setPassword(e.target.value)} 
          />
        </div>

        <button type="submit" className="submit-btn">
          {isRegister ? 'Register' : 'Login'}
        </button>
      </form>
      
      <div className="toggle-auth">
        <span>{isRegister ? 'Already have an account?' : "Don't have an account?"}</span>
        <button 
          onClick={() => {
            setIsRegister(!isRegister);
            setError('');
          }} 
          className="link-btn"
        >
          {isRegister ? 'Login here' : 'Register here'}
        </button>
      </div>
    </div>
  );
}