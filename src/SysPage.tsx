import React, { useEffect, useState } from 'react';
import './App.css';
import Login from './Login'; // Import the new Login component
import { getServerURL } from './utils';
import io from 'socket.io-client';



const serverURL = getServerURL();
const socket = io(serverURL); // Adjust the URL if needed

interface ButtonData {
  name: string;
  postBody: { data: string };
}

const buttonDataListTV: ButtonData[] = [
  { name: 'Snap Email', postBody: { data: 'snap_email' } },
  { name: 'Lock WS', postBody: { data: 'lock_work_station' } },
];



const handlePost = async (postBody: { data: string; meta?: any }): Promise<any> => {
  try {
    const response = await fetch(serverURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postBody),
    });

    const data = await response.json();
    console.log('Success:', data);
    return data;
  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error('Error:', error.message);
      alert('Error: ' + error.message);
    } else {
      console.error('Unknown error:', error);
      alert('An unknown error occurred.');
    }
    throw error; // Re-throw the error to handle it in the calling function if needed
  }
};


const ButtonGroup: React.FC<{ title: string; buttons: ButtonData[] }> = ({ title, buttons }) => {
  const handleClick = async (postBody: { data: string }) => {
    handlePost(postBody)
  };

  return (
    <div className="container">
      <h2>{title}</h2>
      <div className="button-container">
        {buttons.map((buttonData, index) => (
          <button
            key={index}
            className="button"
            onClick={() => handleClick(buttonData.postBody)}
          >
            {buttonData.name}
          </button>
        ))}
      </div>
    </div>
  );
};


const SysPage: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);

  const handleLogin = (newToken: string) => {
    console.log(newToken)
    setToken(newToken);
    localStorage.setItem('authToken', newToken); // Save token

  };  

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
  };
  
  // In useEffect, check for existing token:
  useEffect(() => {
    const savedToken = localStorage.getItem('authToken');
    console.log(savedToken)
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);  

  return (
    <div className="App">
      {token ? (
        <>
          <div className="container">
            <ButtonGroup title="Controls" buttons={buttonDataListTV} />
            <br/>
          </div>


          <div className="container">

          <div className="button-container">
            <button className='button' onClick={handleLogout}>Logout</button>
          </div>

            
          </div>
          
        </>
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
};

export default SysPage;
