import { useState } from 'react';
import { Navbar, NavbarDivider, NavbarItem, NavbarLabel, NavbarSection, NavbarSpacer } from './components/navbar';
import { StackedLayout } from './components/stacked-layout';
import AnymLogo from './assets/white_brand_name_logo.svg'; // Update the path according to your folder structure
import BybitDashboard from './BYBITDashboard'; // Import the Bybit dashboard
import BinanceDashboard from './BINANCEDashboard';
import OkxDashboard from './OKXDashboard';


const navItems = [
  { label: 'Home', url: '/' },
  { label: 'Binance', url: '/binance' },
  { label: 'Bybit', url: '/bybit' },
  { label: 'OKX', url: '/okx' },
];

function Example({ children }) {
  const [activeNav, setActiveNav] = useState('Home'); // Default active item is Home
  const [query, setQuery] = useState(''); // State to hold the input value


  return (
    <StackedLayout
      navbar={
        <Navbar>
          <NavbarLabel>
            <img
              src={AnymLogo}
              alt="Anym Logo"
              className="w-auto h-auto"
              style={{ borderRadius: '0', border: 'none', objectFit: 'contain' }}
            />
          </NavbarLabel>
          <NavbarDivider className="max-lg:hidden" />
          <NavbarSection className="max-lg:hidden">
            {navItems.map(({ label, url }) => (
              <div key={label} className="relative">
                <NavbarItem
                  href={url}
                  onClick={(e) => {
                    e.preventDefault(); // Prevent navigation
                    setActiveNav(label); // Update active nav item
                  }}
                  className={activeNav === label ? 'text-blue-500' : 'text-gray-700'} // Active item styling
                >
                  {label}
                </NavbarItem>
                {activeNav === label && (
                  <span className="absolute inset-x-2 -bottom-2.5 h-0.5 rounded-full bg-zinc-950 dark:bg-white" style={{ opacity: 1 }}></span>
                )}
              </div>
            ))}
          </NavbarSection>

        </Navbar>
      }
    >
      {activeNav === 'Binance' ? <BinanceDashboard /> : children} 
      {activeNav === 'Bybit' ? <BybitDashboard /> : children} 
      {activeNav === 'OKX' ? <OkxDashboard /> : children} 
    
    </StackedLayout>
  );
}

export default Example;

