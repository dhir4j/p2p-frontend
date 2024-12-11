import React, { useEffect, useState } from 'react';
import { Table, TableHead, TableBody, TableRow, TableHeader, TableCell } from '../components/table';
import { Text, Strong } from '../components/text';
import BINANCE_Dashboad from '../BINANCEDashboard';
import { Button } from '../components/button';

function LogsTable({ exchangeName }) {
  const [logsData, setLogsData] = useState([]);
  const [timestamps, setTimestamps] = useState([]);
  const [countriesData, setCountriesData] = useState({});
  const [showDashboard, setShowDashboard] = useState(false);
  const webapp = 'https://hard4j.pythonanywhere.com';

  useEffect(() => {
    fetch(`${webapp}/logs?exchange=binance`)
      .then((response) => response.json())
      .then((data) => {
        if (data.length > 0) {
          // Extract timestamps and organize country data
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
    return <BINANCE_Dashboad exchangeName="BINANCE" />;
  }

  return (
    <div className="bg-[#18181B] p-4 rounded-lg shadow-md">
      <div className="flex justify-between items-center w-full">
        <Strong>{exchangeName} Liquidity Snapshots</Strong>

        <Button onClick={handleNavigateToDashboard} className="text-500 hover:text-700 font-medium">
          Return to Dashboard
        </Button>
      </div>
      <div className="p-2"></div>

      <Table>
        <TableHead>
          <TableRow>
            <TableHeader>Timestamp</TableHeader>
            {Object.keys(countriesData).map((country, index) => (
              <TableHeader key={index}>{country}</TableHeader>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {timestamps.map((timestamp, rowIndex) => (
            <TableRow key={rowIndex}>
              <TableCell>{timestamp}</TableCell>
              {Object.keys(countriesData).map((country, colIndex) => (
                <TableCell key={colIndex}>
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
