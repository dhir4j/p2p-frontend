import React, { useEffect, useState } from 'react'; 
import { Table, TableHead, TableBody, TableRow, TableHeader, TableCell } from './components/table';
import { Badge } from './components/badge';
import { Strong, Text } from './components/text';
import { MagnifyingGlassIcon } from '@heroicons/react/20/solid';
import { Input } from './components/input';
import { NavbarSection, NavbarSpacer, NavbarItem } from './components/navbar';
import BYBITLogs from './App/BYBITLogs';
import { Button } from './components/button';

function BYBIT_Dashboard() {
  const [dashboardData, setDashboardData] = useState([]);
  const [liquidityData, setLiquidityData] = useState({});
  const [metrics, setMetrics] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [showLogs, setShowLogs] = useState(false);
  const webapp = 'https://dvds-occasions-impossible-bet.trycloudflare.com';

  useEffect(() => {
    fetch(`${webapp}/api/dashboard?exchange=bybit`)
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
  
    fetch(`${webapp}/calculate?exchange=bybit`)
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
    fetch(`${webapp}/get_liquidity?exchange=bybit`, {
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
    return <BYBITLogs exchangeName="BYBIT" />;
  }

  return (
    <div className="bg-[#18181B] p-4 rounded-lg shadow-md">
      <Strong>Overview</Strong>

      <div className="bg-[#2a2a2e] p-3 rounded-lg flex justify-between mt-4">
        <div className="bg-[#2a2a2e] text-center p-2 rounded-lg w-1/4">
          <Strong>Total Liquidity (USDT)</Strong>
          <Text>{metrics.total_liquidity ? formatNumberWithCommas(metrics.total_liquidity) : 'Loading...'}</Text>
        </div>
        <div className="bg-[#2a2a2e] text-center p-2 rounded-lg w-1/4">
          <Strong>Total Countries</Strong>
          <Text>{metrics.total_countries ? metrics.total_countries : 'Loading...'}</Text>
        </div>
        <div className="bg-[#2a2a2e] text-center p-2 rounded-lg w-1/4">
          <Strong>Average Spread</Strong>
          <Text>{metrics.average_spread ? metrics.average_spread.toFixed(2)+'%' : 'Loading...'}</Text>
        </div>
        <div className="bg-[#2a2a2e] text-center p-2 rounded-lg w-1/3">
          <Strong>Unique Payment Methods</Strong>
          <Text>{metrics.unique_payment_methods_count ? metrics.unique_payment_methods_count : 'Loading...'}</Text>
        </div>
      </div>
      
      <div className="p-2"></div>
          <NavbarSection className="flex w-full">


          <NavbarItem className="flex items-center w-auto">
            <MagnifyingGlassIcon className="h-5 w-5" />
            <Input
              name="search"
              placeholder="Search Country…"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </NavbarItem>
          <Button
            onClick={handleNavigateToLogs}
            className="text-500 hover:text-700 font-medium"
          >
            Liquidity History
          </Button>

        </NavbarSection>

      <div className="p-2"></div>

      {filteredData.length > 0 ? (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeader>Date & Time</TableHeader>
              <TableHeader>Country</TableHeader>
              <TableHeader>Fiat Currency</TableHeader>
              <TableHeader>Total Liquidity (USDT)</TableHeader>
              <TableHeader>VWAP Price</TableHeader>
              <TableHeader>Exchange Rate</TableHeader>
              <TableHeader>Spread</TableHeader>
              <TableHeader>Available Payment Methods</TableHeader>
            </TableRow>
          </TableHead>

          <TableBody>
            {filteredData.map((data) => {
              const liquidityKey = `${data.country}-${(data.clickedPaymentMethods || []).join('-')}`;
              const specificLiquidity = liquidityData[liquidityKey]?.specific_liquidity;
              const specificVwap = liquidityData[liquidityKey]?.specific_vwap;

              return (
                <TableRow key={data.country}>
                  <TableCell>{data.date_time}</TableCell>
                  <TableCell>{data.country}</TableCell>
                  <TableCell>{data.fiat_currency}</TableCell>
                  <TableCell>{specificLiquidity ? formatNumberWithCommas(specificLiquidity) : formatNumberWithCommas(data.total_liquidity)}</TableCell>
                  <TableCell>{specificVwap ? formatNumberWithCommas(specificVwap) : formatNumberWithCommas(data.volume_weighted_price.toFixed(2))}</TableCell>
                  <TableCell>{formatNumberWithCommas(data.exchange_rate.toFixed(2))}</TableCell>
                  <TableCell>{data.spread}</TableCell>
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
                              payment.method
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
        <Text>No data found.</Text>
      )}
    </div>
  );
}

export default BYBIT_Dashboard;