"use client";

import React, { useState, useEffect } from 'react';

export default function Home() {
  const [rules, setRules] = useState([]);
  const [items, setItems] = useState("");
  const [topProducts, setTopProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showToast, setShowToast] = useState(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    // Auto-hide toast after 8 seconds
    const timer = setTimeout(() => setShowToast(false), 8000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    // Fetch rules
    fetch(`${API_URL}/rules?limit=15`)
      .then(res => {
        if (!res.ok) throw new Error("Backend not reachable or returned error");
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data)) {
          setRules(data);
          setLoading(false);
        } else if (data.error) {
          setError(data.error);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error(err);
        setError("Could not connect to backend server on port 8000");
        setLoading(false);
      });

    // Fetch top products for datalist suggestions
    fetch(`${API_URL}/top-products`)
      .then(res => res.json())
      .then(data => {
        if (data.top_products) setTopProducts(data.top_products);
      })
      .catch(console.error);
  }, []);

  const getRecommendations = async () => {
    const itemList = items.split(',').map(i => i.trim()).filter(i => i);
    if (itemList.length === 0) return;
    try {
      const res = await fetch(`${API_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: itemList })
      });
      const data = await res.json();
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-2">Market Basket Analysis</h1>
          <p className="text-gray-600">Discover product associations powered by Machine Learning</p>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Prediction Panel */}
          <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 col-span-1">
            <h2 className="text-2xl font-bold text-indigo-700 mb-4">Predict Basket</h2>
            <p className="text-sm text-gray-500 mb-4">
              Enter real items (comma-separated). Uses the FP-Growth model generated from the entire dataset.
            </p>
            
            <input 
              type="text" 
              list="product-suggestions"
              value={items}
              onChange={(e) => setItems(e.target.value)}
              placeholder="e.g., JUMBO BAG RED RETROSPOT"
              className="w-full border border-gray-300 p-3 rounded-lg mb-4 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
            />
            <datalist id="product-suggestions">
              {topProducts.slice(0, 100).map((prod, idx) => (
                <option key={idx} value={prod} />
              ))}
            </datalist>

            <button 
              onClick={getRecommendations}
              className="w-full bg-indigo-600 hover:bg-indigo-700 transition duration-200 text-white font-semibold px-4 py-3 rounded-lg shadow-md"
            >
              Get Recommendations
            </button>

            {recommendations.length > 0 && (
              <div className="mt-8 animate-fade-in">
                <h3 className="font-bold text-lg text-gray-800 border-b pb-2 mb-3">Frequently Bought Together:</h3>
                <ul className="space-y-3">
                  {recommendations.map((r, i) => (
                    <li key={i} className="bg-indigo-50 p-3 rounded-md border border-indigo-100 text-indigo-900 shadow-sm flex items-start justify-between">
                       <span className="font-semibold text-sm">{r.item}</span>
                       <span className="text-xs bg-indigo-200 text-indigo-800 px-2 py-1 rounded-full whitespace-nowrap ml-2">
                         Lift: {r.lift.toFixed(1)}
                       </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {recommendations.length === 0 && items && (
               <div className="mt-6 text-sm text-gray-400 italic">No strong recommendations found for these items. Try full exact names like "LUNCH BAG RED RETROSPOT".</div>
            )}
          </div>

          {/* Top Rules Panel */}
          <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 col-span-2 overflow-hidden">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Top Discovered Association Rules</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-100 text-gray-700 text-sm uppercase tracking-wider">
                    <th className="p-3 font-semibold rounded-tl-lg">When they buy...</th>
                    <th className="p-3 font-semibold">They also buy...</th>
                    <th className="p-3 font-semibold text-center">Confidence</th>
                    <th className="p-3 font-semibold text-center rounded-tr-lg">Lift</th>
                  </tr>
                </thead>
                <tbody className="text-gray-700 text-sm">
                  {rules.map((rule, idx) => (
                    <tr key={idx} className="border-b border-gray-50 hover:bg-gray-50 transition">
                      <td className="p-3 py-4 max-w-xs truncate" title={rule.antecedents}>
                         <div className="flex flex-wrap gap-1">
                           {rule.antecedents.split(',').map((item, i) => (
                             <span key={i} className="bg-gray-100 border border-gray-300 px-2 py-1 rounded text-xs">{item}</span>
                           ))}
                         </div>
                      </td>
                      <td className="p-3 py-4 max-w-xs" title={rule.consequents}>
                         <div className="font-semibold text-indigo-600">
                           {rule.consequents.split(',').map(i => i.trim()).join(', ')}
                         </div>
                      </td>
                      <td className="p-3 py-4 text-center">
                         <span className="font-mono bg-blue-50 text-blue-700 px-2 py-1 rounded">{(rule.confidence * 100).toFixed(1)}%</span>
                      </td>
                      <td className="p-3 py-4 text-center">
                         <span className="font-mono bg-green-50 text-green-700 px-2 py-1 rounded">{rule.lift?.toFixed(2)}x</span>
                      </td>
                    </tr>
                  ))}
                  {loading && (
                    <tr><td colSpan={4} className="p-6 text-center text-gray-500">Loading rules...</td></tr>
                  )}
                  {error && !loading && (
                    <tr><td colSpan={4} className="p-6 text-center text-red-500 font-semibold">{error}</td></tr>
                  )}
                  {!loading && !error && rules.length === 0 && (
                    <tr><td colSpan={4} className="p-6 text-center text-gray-500">No rules found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>

      {/* Toast Notification */}
      {showToast && (
        <div className="fixed bottom-4 right-4 max-w-sm bg-blue-600 text-white px-4 py-3 rounded-lg shadow-xl z-50 flex items-start space-x-3 transition-opacity duration-300">
          <div className="flex-1 text-sm font-medium">
            Note: After long periods of inactivity on this project demo, the backend ML model running on the server can take up to 50 seconds to fire up and send data again.
          </div>
          <button onClick={() => setShowToast(false)} className="text-blue-200 hover:text-white mt-0.5">
             <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
             </svg>
          </button>
        </div>
      )}
    </div>
  );
}
