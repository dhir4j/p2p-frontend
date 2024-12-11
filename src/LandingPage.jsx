import { useState, useEffect } from 'react';
import { Navbar, NavbarDivider, NavbarItem, NavbarLabel, NavbarSection } from './components/navbar';
import { Sidebar, SidebarHeader, SidebarBody, SidebarSection, SidebarItem } from './components/sidebar';
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
  const [activeNav, setActiveNav] = useState('Binance');
  const [isMobile, setIsMobile] = useState(false);

  const handleNavClick = (label, url, e) => {
    e.preventDefault();
    if (label === 'Home') {
      window.location.href = url;
    } else {
      setActiveNav(label);
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

  useEffect(() => {
    const checkMobileView = () => {
      setIsMobile(window.innerWidth <= 1024);
    };

    // Initial check
    checkMobileView();

    // Add event listener
    window.addEventListener('resize', checkMobileView);

    // Cleanup
    return () => {
      window.removeEventListener('resize', checkMobileView);
    };
  }, []);

  return (
    <div className={`
      ${isMobile 
        ? 'bg-white text-black dark:bg-black dark:text-white' 
        : ''}
    `}>
      <StackedLayout
        navbar={
          <Navbar className={`
            ${isMobile 
              ? 'bg-white text-black dark:bg-black dark:text-white' 
              : ''}
          `}>
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
                    className={`
                      ${activeNav === label 
                        ? (isMobile 
                            ? 'text-blue-700 dark:text-blue-400' 
                            : 'text-blue-500')
                        : (isMobile 
                            ? 'text-gray-900 dark:text-gray-100' 
                            : 'text-gray-700')}
                    `}
                  >
                    {label}
                  </NavbarItem>
                  {activeNav === label && (
                    <span 
                      className={`
                        absolute inset-x-2 -bottom-2.5 h-0.5 rounded-full
                        ${isMobile 
                          ? 'bg-black dark:bg-white' 
                          : 'bg-zinc-950'}
                      `} 
                      style={{ opacity: 1 }}
                    ></span>
                  )}
                </div>
              ))}
            </NavbarSection>
          </Navbar>
        }
        sidebar={
          <Sidebar className={`
            lg:hidden 
            ${isMobile 
              ? 'bg-white text-black dark:bg-black dark:text-white' 
              : ''}
          `}>
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
                    className={`
                      ${activeNav === label 
                        ? (isMobile 
                            ? 'text-blue-700 dark:text-blue-400' 
                            : 'text-blue-500')
                        : (isMobile 
                            ? 'text-gray-900 dark:text-gray-100' 
                            : 'text-gray-700')}
                    `}
                  >
                    {label}
                  </SidebarItem>
                ))}
              </SidebarSection>
            </SidebarBody>
          </Sidebar>
        }
      >
        <div className={`
          w-full px-4 py-4 md:px-6
          ${isMobile 
            ? 'bg-white text-black dark:bg-black dark:text-white' 
            : ''}
        `}>
          {renderContent()}
        </div>
      </StackedLayout>
    </div>
  );
}

export default Example;