import React, { useEffect, useState } from 'react';
import { Table, TableHead, TableBody, TableRow, TableHeader, TableCell } from '../components/table';
import { Text, Strong } from '../components/text';
import OKX_Dashboad from '../OKXDashboard';
import { Button } from '../components/button';

function LogsTable({ exchangeName }) {
  const [logsData, setLogsData] = useState([]);
  const [timestamps, setTimestamps] = useState([]);
  const [countriesData, setCountriesData] = useState({});
  const [showDashboard, setShowDashboard] = useState(false);
  const webapp = 'https://hard4j.pythonanywhere.com';

  useEffect(() => {
    fetch(`${webapp}/logs?exchange=okx`)
      .then((response) => response.json())
      .then((data) => {
        if (data.length > 0) {
          const extractedTimestamps = data.map((log) => log.timestamp);
          const organizedCountriesData = {};

          data.forEach((log) => {
            Object.keys(log).forEach((key) => {
              if (key !== 'timestamp') {
                if (!organizedCountriesData[key]) {
                  organizedCountriesData[key] = [];
                }
                organizedCountriesData[key].push(log[key]);
              }
            });
          });

          setTimestamps(extractedTimestamps);
          setCountriesData(organizedCountriesData);
        }
      })
      .catch((error) => {
        console.error('Error fetching logs data:', error);
      });
  }, [exchangeName]);

  const handleNavigateToDashboard = () => {
    setShowDashboard(true);
  };

  if (showDashboard) {
    return <OKX_Dashboad exchangeName="OKX" />;
  }

  return (
    <div className="dark:bg-[#18181B] bg-[#D3D3D3] p-4 rounded-lg shadow-md">
      <div className="flex justify-between items-center w-full">
        <Strong className="dark:text-white text-black">{exchangeName} Liquidity Snapshots</Strong>

        <Button 
          onClick={handleNavigateToDashboard} 
          className="dark:text-gray-300 text-gray-700 hover:text-gray-300 dark:hover:text-gray-100 font-medium"
        >
          Return to Dashboard
        </Button>
      </div>
      <div className="p-2"></div>

      <Table>
        <TableHead>
          <TableRow>
            <TableHeader className="dark:text-white text-black">Timestamp</TableHeader>
            {Object.keys(countriesData).map((country, index) => (
              <TableHeader key={index} className="dark:text-white text-black">{country}</TableHeader>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {timestamps.map((timestamp, rowIndex) => (
            <TableRow key={rowIndex}>
              <TableCell className="dark:text-white text-black">{timestamp}</TableCell>
              {Object.keys(countriesData).map((country, colIndex) => (
                <TableCell key={colIndex} className="dark:text-white text-black">
                  {countriesData[country][rowIndex] !== null && !isNaN(countriesData[country][rowIndex])
                    ? parseFloat(countriesData[country][rowIndex])
                        .toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                    : 'N/A'}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export default LogsTable;