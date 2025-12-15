import Chip from "@mui/material/Chip"
import { styled } from "@mui/material/styles"
import type { ChipProps } from "@mui/material/Chip"

type BadgeVariant = "default" | "secondary" | "destructive" | "outline"

interface BadgeProps extends Omit<ChipProps, "variant"> {
  variant?: BadgeVariant
}

interface StyledChipProps {
  badgeVariant?: BadgeVariant
}

const StyledChip = styled(Chip)<StyledChipProps>(
  ({ theme, badgeVariant = "default" }) => {
    const variantStyles = {
      default: {
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.primary.contrastText,
        "&:hover": {
          backgroundColor: theme.palette.primary.dark
        }
      },
      secondary: {
        backgroundColor: theme.palette.secondary.main,
        color: theme.palette.secondary.contrastText,
        "&:hover": {
          backgroundColor: theme.palette.secondary.dark
        }
      },
      destructive: {
        backgroundColor: theme.palette.error.main,
        color: theme.palette.error.contrastText,
        "&:hover": {
          backgroundColor: theme.palette.error.dark
        }
      },
      outline: {
        backgroundColor: "transparent",
        border: `1px solid ${theme.palette.divider}`,
        color: theme.palette.text.primary,
        "&:hover": {
          backgroundColor: theme.palette.action.hover
        }
      }
    }

    return {
      fontSize: "0.75rem",
      height: "auto",
      padding: "0.125rem 0.5rem",
      ...variantStyles[badgeVariant as BadgeVariant]
    }
  }
)

function Badge({ variant = "default", ...props }: BadgeProps) {
  return <StyledChip badgeVariant={variant} {...props} />
}

export { Badge }
