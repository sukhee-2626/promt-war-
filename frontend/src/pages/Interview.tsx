import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../lib/api';

export default function Interview() {
  const { userId } = useParams<{ userId: string }>();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [feedback, setFeedback] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'bot'; text: string }[]>([
    { role: 'bot', text: 'Welcome! Ready to start your technical interview?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const simulateMic = () => {
    setIsListening(true);
    setFeedback('Listening...');
    setTimeout(() => {
      setIsListening(false);
      setTranscript('I think implementing a balanced BST would be the best approach for this problem.');
      setInput('I think implementing a balanced BST would be the best approach for this problem.');
      setFeedback('Feedback: Excellent, focusing on efficiency (O(log n)).');
    }, 2000);
  };

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages]);

  const send = async () => {
    if (!input.trim() || !userId) return;
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      // Assuming api.mentorChat works as a proxy for technical questions
      const res: any = await api.mentorChat(parseInt(userId), `Technical Interview context: ${userMsg}`);
      setMessages(prev => [...prev, { role: 'bot', text: res.response || res.message || 'No response.' }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Error: Could not get response.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-8">Technical Interview Simulation</h1>
      <div className="card h-[500px] flex flex-col p-4">
        <div ref={scrollRef} className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`p-3 rounded ${m.role === 'user' ? 'bg-blue-100 ml-auto max-w-[80%]' : 'bg-gray-100 mr-auto max-w-[80%]'}`}>
              {m.text}
            </div>
          ))}
          {loading && <div className="text-gray-500">Thinking...</div>}
        </div>
        <div className="flex gap-2">
          <button 
            className={`px-4 py-2 rounded ${isListening ? 'bg-red-500' : 'bg-green-500'} text-white`}
            onClick={simulateMic}
            disabled={loading || isListening}
          >
            {isListening ? 'Listening...' : '🎤 Speak'}
          </button>
          <input
            className="flex-1 border p-2 rounded"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Type your answer..."
            disabled={loading}
          />
          <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={send} disabled={loading}>Send</button>
        </div>
        {feedback && <div className="text-sm text-green-700 mt-2 p-2 bg-green-50 rounded">{feedback}</div>}
      </div>
    </main>
  );
}
