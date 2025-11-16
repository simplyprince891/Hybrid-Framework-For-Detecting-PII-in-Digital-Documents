import React, { useState } from "react";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import FileUpload from "./components/FileUpload";
import DetectionTable from "./components/DetectionTable";
import FeedbackForm from "./components/FeedbackForm";

function App() {
  const [detections, setDetections] = useState([]);
  return (
    <div style={{padding: 20, fontFamily: 'Segoe UI, Arial, sans-serif'}}>
      <h1>PII Detection Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
        <div>
          <FileUpload onUpload={setDetections} />
          <DetectionTable detections={detections} />
        </div>
      </div>
      <div className="mt-6">
        <FeedbackForm />
      </div>
      <ToastContainer position="top-right" autoClose={4000} />
    </div>
  );
}
export default App;
