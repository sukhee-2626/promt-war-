import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Onboarding() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ name: '', role: '', goal: '' });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Integrate with backend API
    console.log('Form submitted:', formData);
    // Dummy navigation
    navigate('/dashboard/user123');
  };

  return (
    <main className="max-w-2xl mx-auto px-6 py-12 space-y-8">
      <h1 className="text-4xl font-bold tracking-tighter">Set up your profile</h1>
      <form onSubmit={handleSubmit} className="space-y-6 card">
        <div className="space-y-2">
          <label className="block font-medium">Name</label>
          <input type="text" className="w-full p-2 border rounded" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
        </div>
        <div className="space-y-2">
          <label className="block font-medium">Current Role</label>
          <input type="text" className="w-full p-2 border rounded" value={formData.role} onChange={e => setFormData({ ...formData, role: e.target.value })} required />
        </div>
        <div className="space-y-2">
          <label className="block font-medium">Career Goal</label>
          <textarea className="w-full p-2 border rounded" value={formData.goal} onChange={e => setFormData({ ...formData, goal: e.target.value })} required />
        </div>
        <button type="submit" className="btn-primary w-full">Complete Onboarding</button>
      </form>
    </main>
  );
}
