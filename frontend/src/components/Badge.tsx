import { clsx } from 'clsx';
import React from 'react';

export const Badge = ({children, className}: {children: React.ReactNode, className?: string}) =>
  <span className={clsx("px-2 py-1 text-xs rounded-full bg-gray-100", className)}>{children}</span>
