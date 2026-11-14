import { Link } from 'react-router-dom';

export const NavMenu = ({items}: {items: {label: string, to: string}[]}) =>
  <nav className="flex gap-4 p-4">
    {items.map(i => <Link key={i.to} to={i.to} className="hover:text-blue-500">{i.label}</Link>)}
  </nav>
