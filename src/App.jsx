import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LandingPage from './LandingPage';
import OKXDashboard from './OKXDashboard'; // Import the OKX Dashboard component
import BINANCEDashboard from './BINANCEDashboard';
import BYBITDashboard from './BYBITDashboard';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        {/* <Route path="/okx" element={<OKXDashboard />} />  */}
        {/* <Route path="/bybit" element={<BYBITDashboard />} />
        <Route path="/binance" element={<BINANCEDashboard />} /> */}
      </Routes>
    </Router>
  );
};

export default App;
