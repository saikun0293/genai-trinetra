import { createTheme } from "@mui/material/styles"

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#3b82f6" // blue-500
    },
    secondary: {
      main: "#a855f7" // purple-500
    },
    background: {
      default: "#F0F4F8", // light background
      paper: "#FFFFFF" // white paper
    },
    text: {
      primary: "#000000", // black for headers
      secondary: "#74777C" // normal text color
    },
    divider: "#D0D5DD" // light border color
  },
  shape: {
    borderRadius: 8
  }
})
