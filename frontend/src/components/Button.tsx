import { clsx } from 'clsx';
import React from 'react';

export const Button = ({children, className, ...props}: React.ButtonHTMLAttributes<HTMLButtonElement>) =>
  <button className={clsx("px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700", className)} {...props}>{children}</button>
