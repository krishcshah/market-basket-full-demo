"use client";

import React, { useState, useEffect } from 'react';

export default function Home() {
  const [rules, setRules] = useState([]);
  const [items, setItems] = useState("");
  const [recommendations, setRecommendations] = useState([]);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetch(`${API_URL}/rules?limit=10`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setRules(data);
        } else {
          console.error("Failed to load rules:", data);
          setRules([]);
        }
      })
      .catch(console.error);
  }, []);

  const getRecommendations = async () => {
    const itemList = items.split(',').map(i => i.trim());
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
    <div className="p-8 font-sans">
      <h1 className="text-3xl font-bold mb-6">Market Basket Analysis Demo</h1>
      
      <div className="mb-8 p-4 border rounded shadow">
        <h2 className="text-xl font-semibold mb-4">Get Recommendations</h2>
        <input 
          type="text" 
          value={items}
          onChange={(e) => setItems(e.target.value)}
          placeholder="Enter items e.g., Milk, Bread"
          className="border p-2 mr-4 w-64 rounded"
        />
        <button 
          onClick={getRecommendations}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Recommend
        </button>

        {recommendations.length > 0 && (
          <div className="mt-4">
            <h3 className="font-semibold">Recommended for you:</h3>
            <ul className="list-disc pl-6">
              {recommendations.map((r, i) => (
                <li key={i}>{r.item} (Confidence: {r.confidence.toFixed(2)}, Lift: {r.lift.toFixed(2)})</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Top Association Rules</h2>
        <table className="min-w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2">Antecedents</th>
              <th className="border p-2">Consequents</th>
              <th className="border p-2">Support</th>
              <th className="border p-2">Confidence</th>
              <th className="border p-2">Lift</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule, idx) => (
              <tr key={idx} className="border">
                <td className="border p-2">{rule.antecedents}</td>
                <td className="border p-2">{rule.consequents}</td>
                <td className="border p-2">{rule.support?.toFixed(4)}</td>
                <td className="border p-2">{rule.confidence?.toFixed(4)}</td>
                <td className="border p-2">{rule.lift?.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
