import { useState } from "react";
import "./App.css";
import logo from "./assets/Web-Watchdogs.png"; // Import the logo
import CircularProgressBar from "./CircularProgressBar"; // Import Circular Display Component

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [sent, setSent] = useState(null);
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

      const response1 = await fetch("http://127.0.0.1:8000/llmSentiment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      if (!response1.ok){
        throw new Error("Failed to get LLM analysis")
      }

      // Show result in frontend
      setResult({
        status: "received",
        message1: `URL Received: ${data.url}`,
        message2: data.message2,
        message3: data.message3
      });

      const data1 = await response1.json();
      console.log('response 2', data1);

      setSent({
        llm_ans: data1.result,
        point1: data1.p1,
        point2: data1.p2,
        point3: data1.p3
      })

      setConfidenceScore(100); // Placeholder confidence score
    } catch (error) {
      console.error("Error:", error);
      alert(error);
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
          <p>{result.message1}</p>
          <p>{result.message2}</p>
          <p>{result.message3}</p>
        </div>
      )
      }

      {/* Circular Percentage Display (Appears after scan) */}
      {confidenceScore !== null && (
        <div className="circle-wrapper">
          <CircularProgressBar percentage={confidenceScore} />
          <p className="confidence-text">Confidence Score</p>
        </div>
      )}
      {sent && (
        <div className={`sentiment ${sent.status}`}>
          <p>LLM sentiment analysis</p>
        <h2>Result: {sent.result}</h2>
        <p></p>
        <p>{sent.p1}</p>
        <p>{sent.p2}</p>
        <p>{sent.p3}</p>
      </div>
      )}
    </div>
  );
}

export default App;
