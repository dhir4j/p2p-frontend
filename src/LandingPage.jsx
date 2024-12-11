// import { useState } from 'react';
// import { Navbar, NavbarDivider, NavbarItem, NavbarLabel, NavbarSection } from './components/navbar';
// import { StackedLayout } from './components/stacked-layout';
// import AnymLogo from './assets/white_brand_name_logo.svg';
// import BybitDashboard from './BYBITDashboard';
// import BinanceDashboard from './BINANCEDashboard';
// import OkxDashboard from './OKXDashboard';
// import { Menu, X } from 'lucide-react';

// const navItems = [
//   { label: 'Home', url: 'https://anym.ai/' },
//   { label: 'Binance', url: '/binance' },
//   { label: 'Bybit', url: '/bybit' },
//   { label: 'OKX', url: '/okx' },
// ];

// function Example({ children }) {
//   const [activeNav, setActiveNav] = useState('Binance');
//   const [isMenuOpen, setIsMenuOpen] = useState(false);

//   const handleNavClick = (label, url, e) => {
//     e.preventDefault();
//     if (label === 'Home') {
//       window.location.href = url;
//     } else {
//       setActiveNav(label);
//       setIsMenuOpen(false);
//     }
//   };

//   const renderContent = () => {
//     switch (activeNav) {
//       case 'Binance':
//         return <BinanceDashboard />;
//       case 'Bybit':
//         return <BybitDashboard />;
//       case 'OKX':
//         return <OkxDashboard />;
//       default:
//         return <BinanceDashboard />;
//     }
//   };

//   return (
//     <StackedLayout
//       navbar={
//         <Navbar className="relative">
//           <div className="flex items-center justify-between w-full px-4">
//             <NavbarLabel>
//               <img
//                 src={AnymLogo}
//                 alt="Anym Logo"
//                 className="w-auto h-8 md:h-10"
//                 style={{ borderRadius: '0', border: 'none', objectFit: 'contain' }}
//               />
//             </NavbarLabel>

//             {/* Mobile menu button */}
//             <button
//               onClick={() => setIsMenuOpen(!isMenuOpen)}
//               className="lg:hidden p-2 text-gray-700"
//             >
//               {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
//             </button>

//             {/* Desktop navigation */}
//             <NavbarSection className="hidden lg:flex">
//               {navItems.map(({ label, url }) => (
//                 <div key={label} className="relative">
//                   <NavbarItem
//                     href={url}
//                     onClick={(e) => handleNavClick(label, url, e)}
//                     className={activeNav === label ? 'text-blue-500' : 'text-gray-700'}
//                   >
//                     {label}
//                   </NavbarItem>
//                   {activeNav === label && (
//                     <span className="absolute inset-x-2 -bottom-2.5 h-0.5 rounded-full bg-zinc-950 dark:bg-white"></span>
//                   )}
//                 </div>
//               ))}
//             </NavbarSection>
//           </div>

//           {/* Mobile navigation menu */}
//           {isMenuOpen && (
//             <div className="lg:hidden absolute top-full left-0 right-0 bg-white dark:bg-gray-800 shadow-lg z-50">
//               {navItems.map(({ label, url }) => (
//                 <NavbarItem
//                   key={label}
//                   href={url}
//                   onClick={(e) => handleNavClick(label, url, e)}
//                   className={`block w-full px-4 py-2 text-left ${
//                     activeNav === label ? 'text-blue-500 bg-gray-100 dark:bg-gray-700' : 'text-gray-700 dark:text-gray-300'
//                   }`}
//                 >
//                   {label}
//                 </NavbarItem>
//               ))}
//             </div>
//           )}
//         </Navbar>
//       }
//     >
//       <div className="w-full px-4 py-4 md:px-6">
//         {renderContent()}
//       </div>
//     </StackedLayout>
//   );
// }

// export default Example;

import { useState } from 'react';
import { Navbar, NavbarDivider, NavbarItem, NavbarLabel, NavbarSection } from './components/navbar';
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
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleNavClick = (label, url, e) => {
    e.preventDefault();
    if (label === 'Home') {
      window.location.href = url;
    } else {
      setActiveNav(label);
      setIsMenuOpen(false);
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
        <Navbar className="relative">
          <div className="flex items-center justify-between w-full px-4">
            <NavbarLabel>
              <img
                src={AnymLogo}
                alt="Anym Logo"
                className="w-auto h-8 md:h-10"
                style={{ borderRadius: '0', border: 'none', objectFit: 'contain' }}
              />
            </NavbarLabel>

            {/* Mobile menu toggle */}
            <div 
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="lg:hidden cursor-pointer p-2"
            >
              {isMenuOpen ? (
                <X className="text-gray-700 dark:text-gray-300" size={24} />
              ) : (
                <Menu className="text-gray-700 dark:text-gray-300" size={24} />
              )}
            </div>

            {/* Desktop navigation */}
            <NavbarSection className="hidden lg:flex">
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

          {/* Mobile navigation menu */}
          {isMenuOpen && (
            <div className="lg:hidden absolute top-full left-0 right-0 bg-white dark:bg-gray-800 shadow-lg z-50">
              {navItems.map(({ label, url }) => (
                <NavbarItem
                  key={label}
                  href={url}
                  onClick={(e) => handleNavClick(label, url, e)}
                  className={`block w-full px-4 py-2 text-left ${
                    activeNav === label ? 'text-blue-500 bg-gray-100 dark:bg-gray-700' : 'text-gray-700 dark:text-gray-300'
                  }`}
                >
                  {label}
                </NavbarItem>
              ))}
            </div>
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