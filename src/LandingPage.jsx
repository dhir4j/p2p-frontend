import { useState, useEffect } from 'react';
import { Navbar, NavbarDivider, NavbarItem, NavbarLabel, NavbarSection, NavbarSpacer } from './components/navbar';
import { StackedLayout } from './components/stacked-layout';
import AnymLogo from './assets/white_brand_name_logo.svg';
import BybitDashboard from './BYBITDashboard';
import BinanceDashboard from './BINANCEDashboard';
import OkxDashboard from './OKXDashboard';

const navItems = [
  { label: 'Home', url: 'https://anym.ai/' },
  { label: 'Binance', url: '/binance' },
  { label: 'Bybit', url: '/bybit' },
  { label: 'OKX', url: '/okx' },
];

function Example({ children }) {
  const [activeNav, setActiveNav] = useState('Binance'); // Set default to Binance
  const [query, setQuery] = useState('');

  const handleNavClick = (label, url, e) => {
    e.preventDefault();
    if (label === 'Home') {
      window.location.href = url;
    } else {
      setActiveNav(label);
    }
  };

  // Render the appropriate content based on active nav
  const renderContent = () => {
    switch (activeNav) {
      case 'Binance':
        return <BinanceDashboard />;
      case 'Bybit':
        return <BybitDashboard />;
      case 'OKX':
        return <OkxDashboard />;
      default:
        return <BinanceDashboard />; // Fallback to Binance dashboard
    }
  };

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
                  onClick={(e) => handleNavClick(label, url, e)}
                  className={activeNav === label ? 'text-blue-500' : 'text-gray-700'}
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
      {renderContent()}
    </StackedLayout>
  );
}

export default Example;