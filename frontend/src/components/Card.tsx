import { clsx } from 'clsx';
import React from 'react';

export const Card = ({children, className}: {children: React.ReactNode, className?: string}) =>
  <div className={clsx("p-4 border rounded shadow bg-white", className)}>{children}</div>
