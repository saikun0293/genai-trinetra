import Box from "@mui/material/Box"
import Button from "@mui/material/Button"
import Typography from "@mui/material/Typography"
import Paper from "@mui/material/Paper"
import { InputForm } from "@/components/InputForm"

interface WelcomeScreenProps {
  handleSubmit: (query: string) => void
  isLoading: boolean
  onCancel: () => void
}

export function WelcomeScreen({
  handleSubmit,
  isLoading,
  onCancel
}: WelcomeScreenProps) {
  return (
    <Box
      sx={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        p: 4,
        overflow: "hidden",
        position: "relative"
      }}
    >
      <Paper
        elevation={24}
        sx={{
          width: "100%",
          maxWidth: 800,
          p: 6,
          backdropFilter: "blur(10px)",
          backgroundColor: "rgba(18, 18, 18, 0.8)",
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 3,
          transition: "all 0.3s ease-in-out",
          "&:hover": {
            borderColor: "primary.main",
            boxShadow: 24
          }
        }}
      >
        <Box sx={{ textAlign: "center", mb: 4 }}>
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 700,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 2
            }}
          >
            ✨ Deep Search - ADK 🚀
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ maxWidth: 600, mx: "auto" }}
          >
            Turns your questions into comprehensive reports!
          </Typography>
        </Box>

        <Box sx={{ mt: 4 }}>
          <InputForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            context="homepage"
          />
          {isLoading && (
            <Box sx={{ mt: 3, display: "flex", justifyContent: "center" }}>
              <Button
                variant="outlined"
                color="error"
                onClick={onCancel}
                sx={{ textTransform: "none" }}
              >
                Cancel
              </Button>
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  )
}
