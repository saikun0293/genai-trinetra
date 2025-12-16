import { MessageSquare, Home } from "lucide-react"

interface SideNavProps {
  activeView: "dashboard" | "verify"
  onViewChange: (view: "dashboard" | "verify") => void
}

export function SideNav({ activeView, onViewChange }: SideNavProps) {
  const navItems = [
    {
      id: "dashboard" as const,
      label: "Dashboard",
      icon: Home
    },
    {
      id: "verify" as const,
      label: "Verify",
      icon: MessageSquare
    }
  ]

  return (
    <div
      className="fixed left-0 top-0 h-full w-20 flex flex-col items-center py-6 shadow-lg"
      style={{
        backgroundColor: "#FFFFFF",
        borderRight: "1px solid #D0D5DD",
        zIndex: 50
      }}
    >
      {/* Logo/Brand */}
      <div className="mb-8">
        <div
          className="w-12 h-12 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: "#E9EEF6" }}
        >
          <span className="text-2xl">🛡️</span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex flex-col gap-4 flex-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeView === item.id

          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className="flex flex-col items-center gap-2 px-3 py-3 rounded-lg transition-all group relative"
              style={{
                backgroundColor: isActive ? "#E9EEF6" : "transparent",
                color: isActive ? "#3b82f6" : "#74777C"
              }}
              title={item.label}
            >
              <Icon
                className="w-6 h-6 transition-transform group-hover:scale-110"
                style={{
                  color: isActive ? "#3b82f6" : "#74777C"
                }}
              />
              <span
                className="text-xs font-medium"
                style={{
                  color: isActive ? "#3b82f6" : "#74777C"
                }}
              >
                {item.label}
              </span>

              {/* Active indicator */}
              {isActive && (
                <div
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r"
                  style={{ backgroundColor: "#3b82f6" }}
                />
              )}
            </button>
          )
        })}
      </nav>
    </div>
  )
}
