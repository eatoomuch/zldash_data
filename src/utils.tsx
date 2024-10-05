import config from './config.json';


const isWindowsPlatform = (): boolean => {
    const platform = navigator.platform.toLowerCase();
    return platform.includes('win');
  };
  

// utils.ts
// const dashEnv = process.env.ZLDASH_ENV;

const dashEnv = config.env;


export const getServerURL = (): string => {

    return "http://" + config.server_url + ":" + config.websocket_port

    // if (dashEnv === 'prod') {
    //     return 'http://eatoomuch.com:5000/';        
    // } else {
    //     return 'http://localhost:5000/'; // local testing
    // }
  };
  