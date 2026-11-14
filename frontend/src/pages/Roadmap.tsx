import React from 'react';

const events = [
  { id: 1, date: 'Q1 2024', title: 'Phase 1', desc: 'Setup & Core' },
  { id: 2, date: 'Q2 2024', title: 'Phase 2', desc: 'Interactive Features' },
];

export default function Roadmap() {
  return (
    <div className="p-8">
      <h1>Roadmap</h1>
      <div className="flex flex-col gap-4 mt-4">
        {events.map(e => (
          <div key={e.id} className="p-4 border rounded hover:bg-gray-50 transition">
            <strong className="block text-sm text-blue-600">{e.date}</strong>
            <h2 className="text-xl">{e.title}</h2>
            <p className="text-gray-600">{e.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
