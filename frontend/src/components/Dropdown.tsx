import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export const Dropdown = ({trigger, children}: {trigger: React.ReactNode, children: React.ReactNode}) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)} className="flex items-center gap-1">{trigger}<ChevronDown size={16}/></button>
      {open && <div className="absolute top-full mt-1 p-2 bg-white border rounded shadow z-10">{children}</div>}
    </div>
  );
}
