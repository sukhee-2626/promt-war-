// Usage: <MentorChat /> in Layout or App
import { useState, useRef, useEffect } from 'react'

export default function MentorChat() {
  const [open, setOpen] = useState(false)
  const [msgs, setMsgs] = useState([{ role: 'bot', text: 'Hi! How can I help?' }])
  const [input, setInput] = useState('')
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleOutside = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false) }
    if (open) document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [open])

  return (
    <div className="fixed bottom-4 right-4 z-50" ref={ref}>
      {open && (
        <div className="w-72 h-96 bg-white border rounded-xl shadow-2xl p-4 mb-3 flex flex-col">
          <h3 className="font-bold mb-2">Mentor Chat</h3>
          <div className="flex-1 overflow-y-auto mb-2 text-sm space-y-2">
            {msgs.map((m, i) => <div key={i} className={`p-2 rounded ${m.role === 'bot' ? 'bg-gray-100' : 'bg-blue-100'}`}>{m.text}</div>)}
          </div>
          <input 
            className="border p-2 text-sm rounded" 
            placeholder="Ask..." 
            value={input} 
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && input.trim()) {
                setMsgs([...msgs, { role: 'user', text: input }])
                setInput('')
              }
            }}
          />
        </div>
      )}
      <button 
        onClick={() => setOpen(!open)} 
        className="bg-blue-600 p-4 rounded-full text-white shadow-lg hover:bg-blue-700 transition"
      >
        💬
      </button>
    </div>
  )
}
