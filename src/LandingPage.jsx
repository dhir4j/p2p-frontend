import { useState, useEffect } from 'react';
import { Navbar, NavbarDivider, NavbarItem, NavbarLabel, NavbarSection } from './components/navbar';
import { Sidebar, SidebarHeader, SidebarBody, SidebarSection, SidebarItem } from './components/sidebar';
import { StackedLayout } from './components/stacked-layout';
import AnymLogo from './assets/white_brand_name_logo.svg';
import BybitDashboard from './BYBITDashboard';
import BinanceDashboard from './BINANCEDashboard';
import OkxDashboard from './OKXDashboard';
import { Menu, X } from 'lucide-react';

const navItems = [
  { label: 'Home', url: 'https://anym.ai/' },
  { label: 'Binance', url: '/binance' },
  { label: 'Bybit', url: '/bybit' },
  { label: 'OKX', url: '/okx' },
];

function Example({ children }) {
  const [activeNav, setActiveNav] = useState('Binance');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleNavClick = (label, url, e) => {
    e.preventDefault();
    if (label === 'Home') {
      window.location.href = url;
    } else {
      setActiveNav(label);
      setIsSidebarOpen(false);
    }
  };

  const renderContent = () => {
    switch (activeNav) {
      case 'Binance':
        return <BinanceDashboard />;
      case 'Bybit':
        return <BybitDashboard />;
      case 'OKX':
        return <OkxDashboard />;
      default:
        return <BinanceDashboard />;
    }
  };

  return (
    <StackedLayout
      navbar={
        <Navbar>
          <div className="flex items-center justify-between w-full px-4">
            {/* Mobile menu button */}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 text-gray-700"
            >
              {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            <NavbarLabel>
              <img
                src={AnymLogo}
                alt="Anym Logo"
                className="w-auto h-8 md:h-10"
                style={{ borderRadius: '0', border: 'none', objectFit: 'contain' }}
              />
            </NavbarLabel>
            
            <NavbarDivider className="max-lg:hidden" />
            
            {/* Desktop navigation */}
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
                    <span className="absolute inset-x-2 -bottom-2.5 h-0.5 rounded-full bg-zinc-950 dark:bg-white"></span>
                  )}
                </div>
              ))}
            </NavbarSection>
          </div>

          {/* Mobile Sidebar */}
          {isSidebarOpen && (
            <Sidebar className="lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg">
              <SidebarHeader>
                <img
                  src={AnymLogo}
                  alt="Anym Logo"
                  className="h-8 w-auto mx-4 my-2"
                />
              </SidebarHeader>
              <SidebarBody>
                <SidebarSection>
                  {navItems.map(({ label, url }) => (
                    <SidebarItem
                      key={label}
                      href={url}
                      onClick={(e) => handleNavClick(label, url, e)}
                      className={`block px-4 py-2 ${
                        activeNav === label 
                          ? 'text-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                          : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {label}
                    </SidebarItem>
                  ))}
                </SidebarSection>
              </SidebarBody>
            </Sidebar>
          )}
        </Navbar>
      }
    >
      <div className="w-full px-4 py-4 md:px-6">
        {renderContent()}
      </div>
    </StackedLayout>
  );
}

export default Example;