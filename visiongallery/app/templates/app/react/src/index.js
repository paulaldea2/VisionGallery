// import React from 'react';
// import ReactDOM from 'react-dom';
// import './index.css';
// import App from './App';
// import reportWebVitals from './reportWebVitals';

// ReactDOM.render(
//   <React.StrictMode>
//     <App />
//   </React.StrictMode>,
//   document.getElementById('root')
// );

import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import './assets/css/custom.scss'
import App from './App';
// import * as serviceWorker from './serviceWorker';
// 路由使用 history模式
import { BrowserRouter as Router } from 'react-router-dom';
// 路由采用 hash模式
// import { HashRouter } from 'react-router-dom'

ReactDOM.render(
  <Router>
    <App />
  </Router>
, document.getElementById('root'));

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// reportWebVitals();
