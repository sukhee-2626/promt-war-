import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../lib/api';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid
} from 'recharts';
import { GripVertical, Plus, CheckCircle, Clock, Zap } from 'lucide-react';
import { Tour } from '../components/Tour';

const tourSteps = [
  { element: '#quick-action', intro: 'Perform quick actions here.' },
  { element: '#activity-chart', intro: 'View your activity over the last 7 days.' },
  { element: '#radar-chart', intro: 'See your skill mastery radar.' },
  { element: '#syllabus-progress', intro: 'Track your syllabus progress.' },
];

interface Task {
  id: string;
  title: string;
  status: 'todo' | 'in-progress' | 'done';
}

const INITIAL_TASKS: Task[] = [
  { id: '1', title: 'Setup project', status: 'done' },
  { id: '2', title: 'Implement Dashboard', status: 'in-progress' },
  { id: '3', title: 'Add Kanban', status: 'todo' },
];

// Mock activity data
const ACTIVITY_DATA = [
  { name: 'Mon', active: 4 }, { name: 'Tue', active: 6 }, { name: 'Wed', active: 8 },
  { name: 'Thu', active: 5 }, { name: 'Fri', active: 9 }, { name: 'Sat', active: 2 }, { name: 'Sun', active: 3 },
];

export default function Dashboard() {
  const { userId } = useParams<{ userId: string }>();
  const [data, setData] = useState<any>(null);
  const [tasks, setTasks] = useState<Task[]>(INITIAL_TASKS);

  useEffect(() => {
    if (userId) {
      api.skillAnalysis(parseInt(userId)).then(setData).catch(console.error);
    }
  }, [userId]);

  if (!data) return <div className="p-12 text-center">Loading skill analysis...</div>;

  const progress = Math.round((tasks.filter(t => t.status === 'done').length / tasks.length) * 100);

  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      <Tour steps={tourSteps} />
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Skill Twin: User {userId}</h1>
        <button id="quick-action" className="flex items-center gap-2 bg-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-700">
          <Zap size={18} /> Quick Action
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <div id="activity-chart" className="card p-6 h-[300px]">
          <h2 className="text-xl font-semibold mb-4">Activity (Last 7 days)</h2>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={ACTIVITY_DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
              <Bar dataKey="active" fill="#818cf8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div id="radar-chart" className="card h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data.radar}>
              <PolarGrid stroke="#4b5563" />
              <PolarAngleAxis dataKey="category" tick={{ fill: '#e5e7eb' }} />
              <PolarRadiusAxis angle={30} domain={[0, 1]} tick={{ fill: '#e5e7eb' }} />
              <Radar name="Mastery" dataKey="mastery" stroke="#818cf8" fill="#818cf8" fillOpacity={0.6} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div id="syllabus-progress" className="card p-6 h-[300px] flex flex-col">
          <h2 className="text-xl font-semibold mb-4">Syllabus Progress</h2>
          <div className="flex-1 flex flex-col justify-center gap-4">
            <div className="flex justify-between"><span>Core Concepts</span> <span>80%</span></div>
            <div className="w-full bg-gray-700 rounded-full h-4"><div className="bg-indigo-500 h-4 rounded-full" style={{ width: `80%` }}></div></div>
            <div className="flex justify-between"><span>Advanced Labs</span> <span>45%</span></div>
            <div className="w-full bg-gray-700 rounded-full h-4"><div className="bg-emerald-500 h-4 rounded-full" style={{ width: `45%` }}></div></div>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-6 gap-6">
        {(['todo', 'in-progress', 'done'] as const).map(status => (
          <div key={status} className="bg-gray-800 p-4 rounded-lg" onDragOver={e => e.preventDefault()} onDrop={e => {
            const id = e.dataTransfer.getData('taskId');
            setTasks(tasks.map(t => t.id === id ? { ...t, status } : t));
          }}>
            <h3 className="capitalize font-medium mb-4 text-gray-300">{status.replace('-', ' ')}</h3>
            {tasks.filter(t => t.status === status).map(task => (
              <div key={task.id} draggable onDragStart={e => e.dataTransfer.setData('taskId', task.id)} className="bg-gray-700 p-3 mb-2 rounded flex items-center cursor-grab">
                <GripVertical size={16} className="mr-2 text-gray-500" />
                {task.title}
              </div>
            ))}
          </div>
        ))}
      </div>
    </main>
  );
}
