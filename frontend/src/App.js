// App.js 

import React from 'react';
import { Routes, Route } from 'react-router-dom';
import StockList from './components/StockList';
import StockDetails from './components/StockDetails';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Stock Lookup Application</h1>
        <Routes>
          <Route path="/" element={<StockList />} />
          {/* Ensure the path here is /stock/ not /stocks/ */}
          <Route path="/stock/:ticker" element={<StockDetails />} />
        </Routes>
      </header>
    </div>
  );
}

export default App;