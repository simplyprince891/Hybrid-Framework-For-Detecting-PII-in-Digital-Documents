import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

function ChartPanel({ data }) {
  const sample = data && data.length ? data : [
    { name: 'Aadhaar', count: 3 },
    { name: 'PAN', count: 1 },
    { name: 'EMAIL', count: 2 }
  ];

  return (
    <div className="bg-white rounded shadow p-4">
      <h3 className="text-lg font-medium mb-2">Detections by Type</h3>
      <div style={{ width: '100%', height: 180 }}>
        <ResponsiveContainer>
          <BarChart data={sample}>
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default ChartPanel;
