import Card from "@mui/material/Card"
import CardContent from "@mui/material/CardContent"
import Box from "@mui/material/Box"
import Typography from "@mui/material/Typography"
import Chip from "@mui/material/Chip"
import CircularProgress from "@mui/material/CircularProgress"
import {
  Activity,
  Info,
  Search,
  TextSearch,
  Brain,
  Pen,
  ChevronDown,
  ChevronUp,
  Link
} from "lucide-react"
import { useEffect, useState } from "react"
import ReactMarkdown from "react-markdown"

export interface ProcessedEvent {
  title: string
  data: any
}

interface ActivityTimelineProps {
  processedEvents: ProcessedEvent[]
  isLoading: boolean
  websiteCount: number
}

export function ActivityTimeline({
  processedEvents,
  isLoading,
  websiteCount
}: ActivityTimelineProps) {
  const [isTimelineCollapsed, setIsTimelineCollapsed] = useState<boolean>(false)

  const formatEventData = (data: any): string => {
    if (typeof data === "object" && data !== null && data.type) {
      switch (data.type) {
        case "functionCall":
          return `Calling function: ${data.name}\nArguments: ${JSON.stringify(
            data.args,
            null,
            2
          )}`
        case "functionResponse":
          return `Function ${data.name} response:\n${JSON.stringify(
            data.response,
            null,
            2
          )}`
        case "text":
          return data.content
        case "sources":
          const sources = data.content as Record<
            string,
            { title: string; url: string }
          >
          if (Object.keys(sources).length === 0) {
            return "No sources found."
          }
          return Object.values(sources)
            .map(
              (source) =>
                `[${source.title || "Untitled Source"}](${source.url})`
            )
            .join(", ")
        default:
          return JSON.stringify(data, null, 2)
      }
    }

    if (typeof data === "string") {
      try {
        const parsed = JSON.parse(data)
        return JSON.stringify(parsed, null, 2)
      } catch {
        return data
      }
    } else if (Array.isArray(data)) {
      return data.join(", ")
    } else if (typeof data === "object" && data !== null) {
      return JSON.stringify(data, null, 2)
    }
    return String(data)
  }

  const isJsonData = (data: any): boolean => {
    if (typeof data === "object" && data !== null && data.type) {
      if (data.type === "sources") {
        return false
      }
      return data.type === "functionCall" || data.type === "functionResponse"
    }

    if (typeof data === "string") {
      try {
        JSON.parse(data)
        return true
      } catch {
        return false
      }
    }
    return typeof data === "object" && data !== null
  }

  const getEventIcon = (title: string, index: number) => {
    if (index === 0 && isLoading && processedEvents.length === 0) {
      return <CircularProgress size={16} sx={{ color: "text.secondary" }} />
    }
    if (title.toLowerCase().includes("function call")) {
      return <Activity size={16} color="#60a5fa" />
    } else if (title.toLowerCase().includes("function response")) {
      return <Activity size={16} color="#4ade80" />
    } else if (title.toLowerCase().includes("generating")) {
      return <TextSearch size={16} color="#9ca3af" />
    } else if (title.toLowerCase().includes("thinking")) {
      return <CircularProgress size={16} sx={{ color: "text.secondary" }} />
    } else if (title.toLowerCase().includes("reflection")) {
      return <Brain size={16} color="#9ca3af" />
    } else if (title.toLowerCase().includes("research")) {
      return <Search size={16} color="#9ca3af" />
    } else if (title.toLowerCase().includes("finalizing")) {
      return <Pen size={16} color="#9ca3af" />
    } else if (title.toLowerCase().includes("retrieved sources")) {
      return <Link size={16} color="#fbbf24" />
    }
    return <Activity size={16} color="#9ca3af" />
  }

  useEffect(() => {
    if (!isLoading && processedEvents.length !== 0) {
      setIsTimelineCollapsed(true)
    }
  }, [isLoading, processedEvents])

  return (
    <Card
      sx={{
        border: "1px solid #D0D5DD",
        borderRadius: 2,
        backgroundColor: "#FFFFFF",
        height: isTimelineCollapsed ? 48 : "auto",
        maxHeight: isTimelineCollapsed ? 48 : 500,
        py: 1
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          px: 2,
          py: 0.5,
          cursor: "pointer"
        }}
        onClick={() => setIsTimelineCollapsed(!isTimelineCollapsed)}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            Research
          </Typography>
          {websiteCount > 0 && (
            <Chip
              label={`${websiteCount} websites`}
              size="small"
              sx={{
                height: 20,
                fontSize: "0.7rem",
                backgroundColor: "rgba(82, 82, 82, 0.8)"
              }}
            />
          )}
        </Box>
        {isTimelineCollapsed ? (
          <ChevronDown size={16} />
        ) : (
          <ChevronUp size={16} />
        )}
      </Box>
      {!isTimelineCollapsed && (
        <Box sx={{ maxHeight: 400, overflowY: "auto", px: 2, pb: 1 }}>
          <CardContent sx={{ p: 0 }}>
            {isLoading && processedEvents.length === 0 && (
              <Box sx={{ position: "relative", pl: 4, pb: 2 }}>
                <Box
                  sx={{
                    position: "absolute",
                    left: 12,
                    top: 14,
                    height: "100%",
                    width: 2,
                    backgroundColor: "rgba(38, 38, 38, 0.8)"
                  }}
                />
                <Box
                  sx={{
                    position: "absolute",
                    left: 2,
                    top: 8,
                    height: 20,
                    width: 20,
                    borderRadius: "50%",
                    backgroundColor: "rgba(38, 38, 38, 0.8)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    border: "4px solid",
                    borderColor: "rgba(23, 23, 23, 0.9)"
                  }}
                >
                  <CircularProgress
                    size={12}
                    sx={{ color: "text.secondary" }}
                  />
                </Box>
                <Typography
                  variant="body2"
                  sx={{ fontWeight: 500, color: "text.primary" }}
                >
                  Thinking...
                </Typography>
              </Box>
            )}
            {processedEvents.length > 0 ? (
              <Box>
                {processedEvents.map((eventItem, index) => (
                  <Box key={index} sx={{ position: "relative", pl: 4, pb: 2 }}>
                    {(index < processedEvents.length - 1 ||
                      (isLoading && index === processedEvents.length - 1)) && (
                      <Box
                        sx={{
                          position: "absolute",
                          left: 12,
                          top: 14,
                          height: "100%",
                          width: 2,
                          backgroundColor: "rgba(82, 82, 82, 0.8)"
                        }}
                      />
                    )}
                    <Box
                      sx={{
                        position: "absolute",
                        left: 2,
                        top: 8,
                        height: 24,
                        width: 24,
                        borderRadius: "50%",
                        backgroundColor: "rgba(82, 82, 82, 0.8)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        border: "4px solid",
                        borderColor: "rgba(64, 64, 64, 0.8)"
                      }}
                    >
                      {getEventIcon(eventItem.title, index)}
                    </Box>
                    <Box>
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 500, mb: 0.5, color: "text.primary" }}
                      >
                        {eventItem.title}
                      </Typography>
                      <Box
                        sx={{
                          fontSize: "0.75rem",
                          color: "text.secondary",
                          lineHeight: 1.5
                        }}
                      >
                        {isJsonData(eventItem.data) ? (
                          <Box
                            component="pre"
                            sx={{
                              backgroundColor: "rgba(38, 38, 38, 0.8)",
                              p: 1,
                              borderRadius: 1,
                              fontSize: "0.75rem",
                              overflowX: "auto",
                              whiteSpace: "pre-wrap"
                            }}
                          >
                            {formatEventData(eventItem.data)}
                          </Box>
                        ) : (
                          <ReactMarkdown
                            components={{
                              p: ({ children }) => <span>{children}</span>,
                              a: ({ href, children }) => (
                                <a
                                  href={href}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{
                                    color: "#60a5fa",
                                    textDecoration: "underline"
                                  }}
                                >
                                  {children}
                                </a>
                              ),
                              code: ({ children }) => (
                                <code
                                  style={{
                                    backgroundColor: "rgba(38, 38, 38, 0.8)",
                                    padding: "2px 4px",
                                    borderRadius: 4,
                                    fontSize: "0.75rem"
                                  }}
                                >
                                  {children}
                                </code>
                              )
                            }}
                          >
                            {formatEventData(eventItem.data)}
                          </ReactMarkdown>
                        )}
                      </Box>
                    </Box>
                  </Box>
                ))}
                {isLoading && processedEvents.length > 0 && (
                  <Box sx={{ position: "relative", pl: 4, pb: 2 }}>
                    <Box
                      sx={{
                        position: "absolute",
                        left: 2,
                        top: 8,
                        height: 20,
                        width: 20,
                        borderRadius: "50%",
                        backgroundColor: "rgba(82, 82, 82, 0.8)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        border: "4px solid",
                        borderColor: "rgba(64, 64, 64, 0.8)"
                      }}
                    >
                      <CircularProgress
                        size={12}
                        sx={{ color: "text.secondary" }}
                      />
                    </Box>
                    <Typography
                      variant="body2"
                      sx={{ fontWeight: 500, color: "text.primary" }}
                    >
                      Thinking...
                    </Typography>
                  </Box>
                )}
              </Box>
            ) : !isLoading ? (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  height: "100%",
                  color: "text.disabled",
                  pt: 5
                }}
              >
                <Info size={24} style={{ marginBottom: 12 }} />
                <Typography variant="body2">No activity to display.</Typography>
                <Typography
                  variant="caption"
                  sx={{ color: "text.disabled", mt: 0.5 }}
                >
                  Timeline will update during processing.
                </Typography>
              </Box>
            ) : null}
          </CardContent>
        </Box>
      )}
    </Card>
  )
}
