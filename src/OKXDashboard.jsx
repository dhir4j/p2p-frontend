import React, { useEffect, useState } from 'react'; 
import { Table, TableHead, TableBody, TableRow, TableHeader, TableCell } from './components/table';
import { Badge } from './components/badge';
import { Strong, Text } from './components/text';
import { MagnifyingGlassIcon } from '@heroicons/react/20/solid';
import { Input } from './components/input';
import { NavbarSection, NavbarSpacer, NavbarItem } from './components/navbar';
import OKXLogs from './App/OKXLogs';
import { Button } from './components/button';

function OKX_Dashboard() {
  const [dashboardData, setDashboardData] = useState([]);
  const [liquidityData, setLiquidityData] = useState({});
  const [metrics, setMetrics] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [showLogs, setShowLogs] = useState(false);
  const webapp = 'https://hard4j.pythonanywhere.com';

  useEffect(() => {
    fetch(`${webapp}/api/dashboard?exchange=okx`)
      .then(response => response.json())
      .then(data => {
        const updatedData = data.map(row => ({
          ...row,
          clickedPaymentMethods: row.available_payment_methods.map(payment => payment.method),
        }));
        setDashboardData(updatedData);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  
    fetch(`${webapp}/calculate?exchange=okx`)
      .then(response => response.json())
      .then(data => {
        setMetrics(data);
      })
      .catch(error => {
        console.error('Error fetching metrics:', error);
      });
  }, []);
  
  const handlePaymentMethodClick = (method, country, originalData) => {
    setDashboardData(prevData => {
      return prevData.map(row => {
        if (row.country === country) {
          let newClickedMethods;
          
          if (row.clickedPaymentMethods.length === row.available_payment_methods.length) {
            newClickedMethods = [method];
          } else {
            newClickedMethods = row.clickedPaymentMethods.includes(method)
              ? row.clickedPaymentMethods.filter(m => m !== method)
              : [...row.clickedPaymentMethods, method];
          }
          
          fetchLiquidityData(country, newClickedMethods);
          
          return {
            ...row,
            clickedPaymentMethods: newClickedMethods
          };
        }
        return row;
      });
    });
  };

  const fetchLiquidityData = (country, paymentMethods) => {
    fetch(`${webapp}/get_liquidity?exchange=okx`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        country: country,
        payment_methods: paymentMethods,
      }),
    })
      .then(response => response.json())
      .then(data => {
        setLiquidityData(prevData => ({
          ...prevData,
          [`${country}-${paymentMethods.join('-')}`]: data,
        }));
      })
      .catch(error => {
        console.error('Error fetching liquidity data:', error);
      });
  };

  const handleNavigateToLogs = () => {
    setShowLogs(true);
  };

  const formatNumberWithCommas = (number) => {
    if (typeof number === 'number') {
      return number.toLocaleString();
    }
    if (typeof number === 'string' && !isNaN(number)) {
      return parseFloat(number).toLocaleString();
    }
    return number;
  };

  const filteredData = dashboardData.filter(data => 
    data.country.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (showLogs) {
    return <OKXLogs exchangeName="OKX" />;
  }

  return (
    <div className="dark:bg-[#18181B] bg-[#D3D3D3] p-4 rounded-lg shadow-md dark:text-white text-black">

      <Strong>Overview</Strong>

      <div className="dark:bg-[#2a2a2e] bg-[#bebebe] p-3 rounded-lg flex justify-between mt-4">
        <div className="text-center p-2 rounded-lg w-1/4">
          <Strong>Total Liquidity (USDT)</Strong>
          <Text className="dark:text-white text-black">
            {metrics.total_liquidity ? formatNumberWithCommas(Math.round(metrics.total_liquidity)) : 'Loading...'}
          </Text>
        </div>
        <div className="text-center p-2 rounded-lg w-1/4">
          <Strong>Total Countries</Strong>
          <Text className="dark:text-white text-black">
            {metrics.total_countries ? metrics.total_countries : 'Loading...'}
          </Text>
        </div>
        <div className="text-center p-2 rounded-lg w-1/4">
          <Strong>Average Spread</Strong>
          <Text className="dark:text-white text-black">
            {metrics.average_spread ? metrics.average_spread.toFixed(2)+'%' : 'Loading...'}
          </Text>
        </div>
        <div className="text-center p-2 rounded-lg w-1/3">
          <Strong>Unique Payment Methods</Strong>
          <Text className="dark:text-white text-black">
            {metrics.unique_payment_methods_count ? metrics.unique_payment_methods_count : 'Loading...'}
          </Text>
        </div>
      </div>
      
      <div className="p-2"></div>
      <NavbarSection className="flex w-full">
        <NavbarItem className="flex items-center w-auto">
          <MagnifyingGlassIcon className="h-5 w-5 dark:text-white text-black" />
          <Input
            name="search"
            placeholder="Search Country…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            // className="dark:bg-[#2a2a2e] bg-white dark:text-white text-black"
          />
        </NavbarItem>
        <Button
          onClick={handleNavigateToLogs}
          // className="dark:text-gray-300 text-gray-700 hover:text-gray-900 dark:hover:text-gray-100 font-medium"
          lassName="dark:text-gray-300 text-gray-700 hover:text-gray-300 dark:hover:text-gray-100 font-medium"
        >
          Liquidity History
        </Button>
      </NavbarSection>

      <div className="p-2"></div>

      {filteredData.length > 0 ? (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeader className="dark:text-white text-black">Date & Time</TableHeader>
              <TableHeader className="dark:text-white text-black">Country</TableHeader>
              <TableHeader className="dark:text-white text-black">Fiat Currency</TableHeader>
              <TableHeader className="dark:text-white text-black">Total Liquidity (USDT)</TableHeader>
              <TableHeader className="dark:text-white text-black">VWAP Price</TableHeader>
              <TableHeader className="dark:text-white text-black">Exchange Rate</TableHeader>
              <TableHeader className="dark:text-white text-black">Spread</TableHeader>
              <TableHeader className="dark:text-white text-black">Available Payment Methods</TableHeader>
            </TableRow>
          </TableHead>

          <TableBody>
            {filteredData.map((data) => {
              const liquidityKey = `${data.country}-${(data.clickedPaymentMethods || []).join('-')}`;
              const specificLiquidity = liquidityData[liquidityKey]?.specific_liquidity;
              const specificVwap = liquidityData[liquidityKey]?.specific_vwap;

              return (
                <TableRow key={data.country} className="dark:hover:bg-[#2a2a2e] hover:bg-gray-50">
                  <TableCell className="dark:text-white text-black">{data.date_time}</TableCell>
                  <TableCell className="dark:text-white text-black">{data.country}</TableCell>
                  <TableCell className="dark:text-white text-black">{data.fiat_currency}</TableCell>
                  <TableCell className="dark:text-white text-black">
                    {specificLiquidity ? formatNumberWithCommas(specificLiquidity) : formatNumberWithCommas(Math.round(data.total_liquidity))}
                  </TableCell>
                  <TableCell className="dark:text-white text-black">
                    {specificVwap ? formatNumberWithCommas(specificVwap) : formatNumberWithCommas(data.volume_weighted_price.toFixed(2))}
                  </TableCell>
                  <TableCell className="dark:text-white text-black">
                    {formatNumberWithCommas(data.exchange_rate.toFixed(2))}
                  </TableCell>
                  <TableCell className="dark:text-white text-black">{data.spread}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-4">
                      {data.available_payment_methods.map(payment => {
                        const isClicked = (data.clickedPaymentMethods || []).includes(payment.method);
                        return (
                          <span
                            key={payment.method}
                            className={`cursor-pointer ${isClicked ? 'font-bold' : ''}`}
                            onClick={() => handlePaymentMethodClick(payment.method, data.country, data)}
                          >
                            {isClicked ? (
                              <Badge color="purple">{payment.method}</Badge>
                            ) : (
                              <span className="dark:text-white text-black">{payment.method}</span>
                            )}
                          </span>
                        );
                      })}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      ) : (
        <Text className="dark:text-white text-black">No data found.</Text>
      )}
    </div>
  );
}

export default OKX_Dashboard;