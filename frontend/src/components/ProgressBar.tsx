import { clsx } from 'clsx';
import React from 'react';

export const ProgressBar = ({value, className}: {value: number, className?: string}) =>
  <div className={clsx("w-full bg-gray-200 rounded-full h-2.5", className)}>
    <div className="bg-blue-600 h-2.5 rounded-full" style={{width: `${Math.min(100, Math.max(0, value))}%`}}></div>
  </div>
