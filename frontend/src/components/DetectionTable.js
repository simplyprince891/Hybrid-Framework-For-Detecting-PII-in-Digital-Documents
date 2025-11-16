import React from "react";

function DetectionTable({ detections }) {
  const safeDetections = Array.isArray(detections) ? detections : [];

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text || '');
      // small feedback: use alert or better toast from parent; keep minimal here
      // eslint-disable-next-line no-alert
      alert('Copied to clipboard');
    } catch (err) {
      console.error('Copy failed', err);
    }
  };

  return (
    <div className="mt-6 overflow-x-auto">
      <div className="min-w-full bg-white rounded shadow">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {safeDetections.map((d, i) => (
              <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{d.type}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 break-words max-w-md">{d.value}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {d.score !== undefined && (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800">{d.score}</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => copyToClipboard(d.value)}
                      className="px-2 py-1 rounded bg-blue-600 text-white text-xs hover:bg-blue-700"
                    >
                      Copy
                    </button>
                    {/* placeholder for future actions (flag, ignore) */}
                  </div>
                </td>
              </tr>
            ))}
            {safeDetections.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">No detections yet</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DetectionTable;
