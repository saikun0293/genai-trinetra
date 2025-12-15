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
      className="fixed left-0 top-0 h-full w-20 flex flex-col items-center py-6 shadow-2xl"
      style={{
        backgroundColor: "#17181A",
        borderRight: "1px solid #2D2E2F",
        zIndex: 50
      }}
    >
      {/* Logo/Brand */}
      <div className="mb-8">
        <div
          className="w-12 h-12 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: "#2D2E2F" }}
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
                backgroundColor: isActive ? "#2D2E2F" : "transparent",
                color: isActive ? "#60A5FA" : "#B8BCC1"
              }}
              title={item.label}
            >
              <Icon
                className="w-6 h-6 transition-transform group-hover:scale-110"
                style={{
                  color: isActive ? "#60A5FA" : "#B8BCC1"
                }}
              />
              <span
                className="text-xs font-medium"
                style={{
                  color: isActive ? "#60A5FA" : "#B8BCC1"
                }}
              >
                {item.label}
              </span>

              {/* Active indicator */}
              {isActive && (
                <div
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r"
                  style={{ backgroundColor: "#60A5FA" }}
                />
              )}
            </button>
          )
        })}
      </nav>
    </div>
  )
}
