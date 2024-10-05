import React, { useState } from 'react';
import './App.css';
import { getServerURL } from './utils';

interface LoginProps {
  onLogin: (token: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const serverURL = getServerURL();
 

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    

    try {
      const response = await fetch(serverURL, { // Replace with your API URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: 'login', meta: {username, password} }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      console.log(data)
      onLogin(data['data']['token']); // Save token in your app state
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('An unknown error occurred.');
      }
    }
  };

  return (
    <div className="login-form">
      {/* <h2>Login</h2> */}
      <form onSubmit={handleLogin}>
        {/* <label> */}
          {/* Username: */}
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        {/* </label> */}
        {/* <label> */}
          {/* Password: */}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        {/* </label> */}
        <button type="submit">__</button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default Login;
