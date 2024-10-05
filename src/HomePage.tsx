import React, { useEffect, useState } from 'react';
import './App.css';
import Login from './Login'; // Import the new Login component
import { getServerURL } from './utils';
import io from 'socket.io-client';
import { str, stringify } from 'ajv';

const serverURL = getServerURL();
const socket = io(serverURL); // Adjust the URL if needed

interface ButtonData {
  name: string;
  postBody: { data: string };
}

const buttonDataListTV: ButtonData[] = [
  { name: 'TV Vol Up', postBody: { data: 'tv_volume_up' } },
  { name: 'TV Vol Down', postBody: { data: 'tv_volume_down' } },
  { name: 'TV Src ATV', postBody: { data: 'tv_source_appletv' } },
  { name: 'TV Src PC', postBody: { data: 'tv_source_pc' } },
  { name: 'TV Notify', postBody: { data: 'tv_notify' } },
  { name: 'TV Connect', postBody: { data: 'tv_reconnect' } },
  { name: 'TV On Off', postBody: { data: 'tv_on_off' } },
];

const buttonDataListLights: ButtonData[] = [
  { name: 'Lights On', postBody: { data: 'lights_on' } },
  { name: 'Lights Off', postBody: { data: 'lights_off' } },
  { name: 'Scene Bright', postBody: { data: 'scene_bright' } },
  { name: 'Scene Night', postBody: { data: 'scene_night' } },
  { name: 'Scene Focus', postBody: { data: 'scene_focus' } },
  { name: 'Scene Movie', postBody: { data: 'scene_movie' } },
];

const buttonDataListLightsBrightness: ButtonData[] = [
  { name: 'Brightness -', postBody: { data: 'lights_brightness_down' } },  
  { name: 'Brightness +', postBody: { data: 'lights_brightness_up' } },
];

const buttonCtrls: ButtonData[] = [
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
    handlePost(postBody);
  };

  return (
    <div className="container">
    {title && <h2>{title}</h2>}
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

const VolumeControl: React.FC = () => {
  const [volume, setVolume] = useState(50);
  const [isUserAdjustingVolume, setIsUserAdjustingVolume] = useState(false); // State to track user adjustment

  const handleVolumeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = event.target.value;
    setVolume(Number(newVolume));

    // Indicate that the user is adjusting the volume
    setIsUserAdjustingVolume(true);
    // Reset the state after 5 seconds to allow server updates again
    setTimeout(() => {
      setIsUserAdjustingVolume(false);
    }, 2000);
    
    // Send newVolume to the server if needed
    handlePost({ data: 'tv_set_volume', meta: Number(newVolume) });
    console.log('Volume:', newVolume);
  };

  useEffect(() => {
    handlePost({ data: "tv_get_volume" }).then(
      response => {
        console.log(response['data']);
        // setVolume(Number(response['data']));
      }
    );

    handlePost({ data: "tv_request_heartbeat" }).then(
      response => {
        console.log(response['data']);
        // setVolume(Number(response['data']));
      }
    );

    // Function to handle volume change from server
    const handleVolumeUpdate = (data: any) => {
      console.log('handleVolumeUpdate triggered');

      if (isUserAdjustingVolume) {
        // Prevent updates if the user is adjusting the slider
        console.log('not updating volume slider as user is adjusting volume');
        return;
      }

      const newVolume = Number(data.volume); // Adjust if the server sends a different structure
      setVolume(newVolume);
      console.log('Volume updated from server:', newVolume);
    };

    // Listen for 'volumeUpdate' event from the server
    socket.on('volume_update', handleVolumeUpdate);

    // Cleanup on component unmount
    return () => {
      socket.off('volume_update', handleVolumeUpdate);
    };
  }, []);

  return (
    <div className="volume-control">
      <input
        type="range"
        min="0"
        max="100"
        value={volume}
        className="slider vertical-slider"
        onChange={handleVolumeChange}
      />
    </div>
  );
};

const HomePage: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);
  const [buttonSequence, setButtonSequence] = useState<number[]>([]);
  const [showUnlockContent, setShowUnlockContent] = useState(false);
  const [isTVConnected, setIsTVConnected] = useState(false); // Step 1: TV connection state
  const [lastConnectedTime, setLastConnectedTime] = useState<string | null>(null); 

  const handleLogin = (newToken: string) => {
    console.log(newToken);
    setToken(newToken);
    localStorage.setItem('authToken', newToken); // Save token
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
  };

  const handleInvisibleButtonClick = (buttonId: number) => {
    setButtonSequence(prevSequence => {
      const newSequence = [...prevSequence, buttonId];
      if (JSON.stringify(newSequence.slice(-5)) === JSON.stringify([1, 1, 2, 2, 1])) {
        setShowUnlockContent(true);
      }
      return newSequence;
    });
  };

  // Step 2: Implement the handleTVConnectionConfirmUpdate function
  const handleTVConnectionConfirmUpdate = (data: any) => {
    const heartbeat_str = String(data.data);

    if (heartbeat_str === 'tv_connected'){
      setIsTVConnected(true); // Update state to show that TV is connected
    }
    else{
      setIsTVConnected(false); // Update state to show that TV is disconnected
    }

    // Get the current time when the connection is confirmed
    const currentTime = new Date().toLocaleString(); // Format the time as a readable string
    setLastConnectedTime(currentTime); // Update the last connected time    
  };

  useEffect(() => {
    const savedToken = localStorage.getItem('authToken');
    console.log(savedToken);
    if (savedToken) {
      setToken(savedToken);
    }

    // Listen for 'heartbeat' event from the server to confirm TV connection
    socket.on('tv_heartbeat', handleTVConnectionConfirmUpdate);

    // Cleanup on component unmount
    return () => {
      socket.off('tv_heartbeat', handleTVConnectionConfirmUpdate);
    };
  }, []);

  return (
    <div className="App">
      {token ? (
        <>
          <div className="container">
            {/* Step 3: Dynamically update the title based on isTVConnected */}
            <ButtonGroup
              // title={`TV Controls${isTVConnected ? ' (Connected)' : ''}`}
              title={`TV Controls${isTVConnected ? ` (${lastConnectedTime})` : ' (Not Connected)'}`}

              buttons={buttonDataListTV}
            />
            <br />
            <VolumeControl />
          </div>
          <div className="container">
            <ButtonGroup title="Lights Controls" buttons={buttonDataListLights} />
            <br/>
            <ButtonGroup title="" buttons={buttonDataListLightsBrightness} />
          </div>
          
          <div className="container">
            <div className="button-container">
              <button className='button' onClick={handleLogout}>Logout</button>
            </div>
          </div>
          {!showUnlockContent && (
            <div className='container-borderless'>
              <button
                className="invisible-button"
                onClick={() => handleInvisibleButtonClick(1)}
              >
                Invisible Button 1
              </button>
              <button
                className="invisible-button"
                onClick={() => handleInvisibleButtonClick(2)}
              >
                Invisible Button 2
              </button>
            </div>
          )}
          {showUnlockContent && (
            <div className="unlock-content">
              <div className="container">
                <ButtonGroup title="Controls" buttons={buttonCtrls} />
                <br/>
              </div>
            </div>
          )}
        </>
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
};

export default HomePage;
