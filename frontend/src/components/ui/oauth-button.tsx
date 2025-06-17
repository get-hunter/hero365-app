import React from "react"
import { Button } from "./button"
import { Box, HStack, Icon, Text } from "@chakra-ui/react"
import { FaGoogle, FaApple, FaGithub } from "react-icons/fa"

interface OAuthButtonProps {
  provider: "google" | "apple" | "github"
  onClick: () => void
  loading?: boolean
  size?: "sm" | "md" | "lg"
  variant?: "outline" | "solid"
}

const providerConfig = {
  google: {
    icon: FaGoogle,
    label: "Continue with Google",
    color: "#4285F4",
  },
  apple: {
    icon: FaApple,
    label: "Continue with Apple",
    color: "#000000",
  },
  github: {
    icon: FaGithub,
    label: "Continue with GitHub",
    color: "#24292e",
  },
}

export function OAuthButton({ 
  provider, 
  onClick, 
  loading = false, 
  size = "md",
  variant = "outline" 
}: OAuthButtonProps) {
  const config = providerConfig[provider]
  const IconComponent = config.icon

  return (
    <Button
      onClick={onClick}
      loading={loading}
      size={size}
      variant={variant}
      width="100%"
      borderColor={variant === "outline" ? "gray.300" : undefined}
      color={variant === "outline" ? config.color : "white"}
      backgroundColor={variant === "solid" ? config.color : "transparent"}
      _hover={{
        backgroundColor: variant === "outline" ? "gray.50" : undefined,
        borderColor: variant === "outline" ? config.color : undefined,
      }}
    >
      <HStack gap={3}>
        <Icon as={IconComponent} boxSize={5} />
        <Text fontWeight="medium">{config.label}</Text>
      </HStack>
    </Button>
  )
}

interface OAuthSectionProps {
  onGoogleClick: () => void
  onAppleClick: () => void
  onGitHubClick?: () => void
  loading?: boolean
  showGitHub?: boolean
}

export function OAuthSection({ 
  onGoogleClick, 
  onAppleClick, 
  onGitHubClick,
  loading = false,
  showGitHub = false 
}: OAuthSectionProps) {
  return (
    <Box>
      <HStack gap={2} width="100%">
        <OAuthButton
          provider="google"
          onClick={onGoogleClick}
          loading={loading}
        />
        <OAuthButton
          provider="apple"
          onClick={onAppleClick}
          loading={loading}
        />
      </HStack>
      {showGitHub && onGitHubClick && (
        <Box mt={2}>
          <OAuthButton
            provider="github"
            onClick={onGitHubClick}
            loading={loading}
          />
        </Box>
      )}
    </Box>
  )
} 