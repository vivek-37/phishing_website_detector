import { useState } from "react";
import "./App.css";
import logo from "./assets/Web-Watchdogs.png"; // Import the logo
import CircularProgressBar from "./CircularProgressBar"; // Import Circular Display Component

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [confidenceScore, setConfidenceScore] = useState(null); // Confidence Score

  const handleScan = async (e) => {
    e.preventDefault();
    if (!url) return alert("Please enter a URL");

    setLoading(true);
    setProgress(0);
    setConfidenceScore(null); // Reset confidence score

    // Simulating loading bar progress
    let progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10; // Increases progress gradually
      });
    }, 300);

    try {
      // Send URL to backend
      const response = await fetch("http://127.0.0.1:8000/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error("Failed to send URL to backend");
      }

      const data = await response.json();
      console.log("Backend Response:", data);

      // Show result in frontend
      setResult({
        status: "received",
        message: `URL Received: ${data.url}`,
      });

      setConfidenceScore(100); // Placeholder confidence score
    } catch (error) {
      console.error("Error:", error);
      alert("Error sending the URL to the backend");
    }

    clearInterval(progressInterval);
    setProgress(100); // Set to 100% when done
    setLoading(false);
  };

  return (
    <div className="container">
      {/* Logo with Glow Animation */}
      <img src={logo} alt="Web Watchdogs Logo" className="logo ultra-glow" />
      
      <h1>Phishing Website Detector</h1>

      <form method="post" onSubmit={handleScan}>
        <div className="input-container">
          {/* Neon Glowing Input Box */}
          <input
            type="text"
            placeholder="Enter website URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="input-box"
          />
          
          {/* Animated Glowing Button */}
          <button disabled={loading} className="glow-button">
            {loading ? "Scanning..." : "Scan Website"}
          </button>
        </div>
      </form>

      {/* Loading Bar (Keeps Showing During Scan) */}
      {loading && (
        <div className="loading-bar-container">
          <div className="loading-bar" style={{ width: `${progress}%` }}>
            {progress}%
          </div>
        </div>
      )}

      {/* Display Result Section */}
      {result && (
        <div className={`result ${result.status}`}>
          <h2>Result: {result.status}</h2>
          <p>{result.message}</p>
        </div>
      )}

      {/* Circular Percentage Display (Appears after scan) */}
      {confidenceScore !== null && (
        <div className="circle-wrapper">
          <CircularProgressBar percentage={confidenceScore} />
          <p className="confidence-text">Confidence Score</p>
        </div>
      )}
    </div>
  );
}

export default App;
