import { useState, useEffect } from 'react';
import { Navbar, NavbarDivider, NavbarItem, NavbarLabel, NavbarSection } from './components/navbar';
import { Sidebar, SidebarHeader, SidebarBody, SidebarSection, SidebarItem } from './components/sidebar';
import { StackedLayout } from './components/stacked-layout';
import DarkLogo from './assets/black_brand_name_logo.svg';
import WhiteLogo from './assets/white_brand_name_logo.svg';
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

    checkMobileView();
    window.addEventListener('resize', checkMobileView);

    return () => {
      window.removeEventListener('resize', checkMobileView);
    };
  }, []);

  return (
    <div className="bg-[#FFFFFF] dark:!bg-[#09090B] [&>*]:dark:!bg-[#09090B] text-black dark:text-white min-h-screen">
      <StackedLayout
        navbar={
          <Navbar className="bg-[#FFFFFF] dark:bg-[#09090B]">
            <NavbarLabel>
              <img
                src={`${useMediaQuery('(prefers-color-scheme: dark)') ? WhiteLogo : DarkLogo}`}
                alt="Anym Logo"
                className="w-auto h-auto"
                style={{ borderRadius: '0', border: 'none', objectFit: 'contain' }}
              />
            </NavbarLabel>
            <NavbarDivider className="max-lg:hidden dark:border-gray-700" />
            <NavbarSection className="max-lg:hidden">
              {navItems.map(({ label, url }) => (
                <div key={label} className="relative">
                  <NavbarItem
                    href={url}
                    onClick={(e) => handleNavClick(label, url, e)}
                    className={`
                      ${activeNav === label 
                        ? 'text-blue-700 dark:text-blue-400' 
                        : 'text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-300'}
                    `}
                  >
                    {label}
                  </NavbarItem>
                  {activeNav === label && (
                    <span 
                      className="absolute inset-x-2 -bottom-2.5 h-0.5 rounded-full bg-zinc-950 dark:bg-white"
                      style={{ opacity: 1 }}
                    ></span>
                  )}
                </div>
              ))}
            </NavbarSection>
          </Navbar>
        }
        sidebar={
          <Sidebar className="lg:hidden bg-[#FFFFFF] dark:bg-[#18181B]">
            {/* <SidebarHeader className="border-b border-gray-200 dark:border-gray-800"> */}
            <SidebarHeader>
              <img
                src={`${useMediaQuery('(prefers-color-scheme: dark)') ? WhiteLogo : DarkLogo}`}
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
                        ? 'text-blue-700 dark:text-blue-400 bg-gray-100 dark:bg-gray-800' 
                        : 'text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800'}
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
        <div className="bg-[#D3D3D3] dark:bg-[#18181B] rounded-lg">
          {renderContent()}
        </div>
      </StackedLayout>
    </div>
  );
}

// Custom hook for media queries
function useMediaQuery(query) {
  const [matches, setMatches] = useState(
    window.matchMedia(query).matches
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const handler = (e) => setMatches(e.matches);
    
    mediaQuery.addListener(handler);
    return () => mediaQuery.removeListener(handler);
  }, [query]);

  return matches;
}

export default Example;