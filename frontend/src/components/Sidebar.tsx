import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/projects', label: 'Projects' },
  { to: '/tasks', label: 'Tasks' },
  { to: '/documents', label: 'Documents' },
  { to: '/risks', label: 'Risks' },
  { to: '/settings', label: 'Settings' },
]

export function Sidebar() {
  return (
    <aside className="w-full border border-slate-200 bg-white p-4 lg:max-w-64 lg:border-r lg:border-t-0">
      <h1 className="mb-5 text-xl font-semibold text-slate-900">Carb Assistant</h1>
      <nav className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:flex lg:flex-col">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `rounded-lg px-3 py-2 text-sm transition ${
                isActive ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
