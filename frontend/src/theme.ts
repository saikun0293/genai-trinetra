import { createTheme } from "@mui/material/styles"

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#3b82f6" // blue-500
    },
    secondary: {
      main: "#a855f7" // purple-500
    },
    background: {
      default: "#0c0c0d", // neutral-950
      paper: "#171717" // neutral-900
    },
    text: {
      primary: "#fafafa", // neutral-50
      secondary: "#a3a3a3" // neutral-400
    }
  },
  typography: {
    fontFamily: "system-ui, -apple-system, sans-serif"
  },
  shape: {
    borderRadius: 8
  }
})
