import React, { useState } from "react";
function FeedbackForm() {
  const [feedback, setFeedback] = useState("");
  const handleSubmit = async e => {
    e.preventDefault();
    await fetch("/api/v1/feedback/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback })
    });
    setFeedback("");
    alert("Feedback submitted");
  };
  return (
    <form onSubmit={handleSubmit}>
      <textarea value={feedback} onChange={e => setFeedback(e.target.value)} />
      <button type="submit">Submit Feedback</button>
    </form>
  );
}
export default FeedbackForm;
