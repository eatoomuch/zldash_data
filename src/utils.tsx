import config from './config.json';


const isWindowsPlatform = (): boolean => {
    const platform = navigator.platform.toLowerCase();
    return platform.includes('win');
  };
  

// utils.ts
// const dashEnv = process.env.ZLDASH_ENV;

const dashEnv = config.env;


export const getServerURL = (): string => {
    if (dashEnv === 'prod') {
        return 'http://eatoomuch.com:5000/';        
    } else {
        return 'http://192.168.7.162:5000/'; // local testing
    }
  };
  