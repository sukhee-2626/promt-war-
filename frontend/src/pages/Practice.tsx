import React, { useState } from 'react';
import dsaChallenges from '../../../content/dsa/data.json';
import sqlChallenges from '../../../content/sql/challenges.json';

type Challenge = { id: number; title: string; difficulty: string; topic?: string; tags?: string[] };

export default function Practice() {
  const [activeTab, setActiveTab] = useState<'dsa' | 'sql'>('dsa');
  const challenges = activeTab === 'dsa' ? (dsaChallenges as Challenge[]) : (sqlChallenges as Challenge[]);

  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-8">Practice Challenges</h1>
      
      <div className="flex gap-4 mb-8">
        {(['dsa', 'sql'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-2 rounded-full font-semibold ${
              activeTab === tab ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-300'
            }`}
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="bg-gray-900 rounded-lg p-6">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-gray-700 text-gray-400">
              <th className="py-3">Title</th>
              <th className="py-3">Difficulty</th>
              <th className="py-3">Category</th>
              <th className="py-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {challenges.map(c => (
              <tr key={c.id} className="border-b border-gray-800">
                <td className="py-3">{c.title}</td>
                <td className="py-3 capitalize">{c.difficulty}</td>
                <td className="py-3">{c.topic || c.tags?.join(', ')}</td>
                <td className="py-3">
                  <button className="text-indigo-400 hover:text-indigo-300 font-semibold">Start</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
