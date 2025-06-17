import { Container, Image, Input, Text, VStack, HStack, Separator, Box } from "@chakra-ui/react"
import {
  Link as RouterLink,
  createFileRoute,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiLock, FiMail } from "react-icons/fi"
import { useState } from "react"

import type { Body_login_login_access_token as AccessToken } from "@/client"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { InputGroup } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import { OAuthSection } from "@/components/ui/oauth-button"
import { PhoneAuth } from "@/components/ui/phone-auth"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import Logo from "/assets/images/fastapi-logo.svg"
import { emailPattern, passwordRules } from "../utils"

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
})

function Login() {
  const { 
    loginMutation, 
    loginWithPhoneMutation,
    sendOTPMutation,
    verifyOTPMutation,
    signInWithGoogleMutation,
    signInWithAppleMutation,
    signInWithGitHubMutation,
    error, 
    resetError 
  } = useAuth()

  const [authMethod, setAuthMethod] = useState<"email" | "phone">("email")

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AccessToken>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const onEmailSubmit: SubmitHandler<AccessToken> = async (data) => {
    if (isSubmitting) return
    resetError()
    try {
      // Map the form data to the expected format
      await loginMutation.mutateAsync({ email: data.username, password: data.password })
    } catch {
      // error is handled by useAuth hook
    }
  }

  const handleOAuthGoogle = async () => {
    resetError()
    try {
      await signInWithGoogleMutation.mutateAsync()
    } catch {
      // error is handled by useAuth hook
    }
  }

  const handleOAuthApple = async () => {
    resetError()
    try {
      await signInWithAppleMutation.mutateAsync()
    } catch {
      // error is handled by useAuth hook
    }
  }

  const handleOAuthGitHub = async () => {
    resetError()
    try {
      await signInWithGitHubMutation.mutateAsync()
    } catch {
      // error is handled by useAuth hook
    }
  }

  const handleSendOTP = async (phone: string) => {
    resetError()
    await sendOTPMutation.mutateAsync(phone)
  }

  const handleVerifyOTP = async (phone: string, otp: string) => {
    resetError()
    await verifyOTPMutation.mutateAsync({ phone, token: otp })
  }

  const isLoading = isSubmitting || 
    signInWithGoogleMutation.isPending || 
    signInWithAppleMutation.isPending || 
    signInWithGitHubMutation.isPending ||
    sendOTPMutation.isPending ||
    verifyOTPMutation.isPending

  return (
    <Container
      h="100vh"
      maxW="md"
      alignItems="stretch"
      justifyContent="center"
      gap={6}
      centerContent
    >
      <Image
        src={Logo}
        alt="FastAPI logo"
        height="auto"
        maxW="2xs"
        alignSelf="center"
        mb={4}
      />

      <VStack gap={6} width="100%">
        {/* OAuth Section */}
        <VStack gap={4} width="100%">
          <Text fontSize="lg" fontWeight="semibold" textAlign="center">
            Welcome back
          </Text>
          
          <OAuthSection
            onGoogleClick={handleOAuthGoogle}
            onAppleClick={handleOAuthApple}
            onGitHubClick={handleOAuthGitHub}
            loading={isLoading}
            showGitHub={true}
          />
        </VStack>

        <HStack width="100%">
          <Separator />
          <Text fontSize="sm" color="gray.500" minW="fit-content">
            or continue with
          </Text>
          <Separator />
        </HStack>

        {/* Authentication Method Selector */}
        <HStack gap={2} width="100%">
          <Button
            variant={authMethod === "email" ? "solid" : "outline"}
            onClick={() => setAuthMethod("email")}
            flex={1}
          >
            Email
          </Button>
          <Button
            variant={authMethod === "phone" ? "solid" : "outline"}
            onClick={() => setAuthMethod("phone")}
            flex={1}
          >
            Phone
          </Button>
        </HStack>

        {/* Authentication Forms */}
        <Box width="100%">
          {authMethod === "email" ? (
            <VStack
              as="form"
              onSubmit={handleSubmit(onEmailSubmit)}
              gap={4}
              width="100%"
            >
              <Field
                invalid={!!errors.username}
                errorText={errors.username?.message || !!error}
              >
                <InputGroup w="100%" startElement={<FiMail />}>
                  <Input
                    id="username"
                    {...register("username", {
                      required: "Email is required",
                      pattern: emailPattern,
                    })}
                    placeholder="Email"
                    type="email"
                  />
                </InputGroup>
              </Field>
              
              <PasswordInput
                type="password"
                startElement={<FiLock />}
                {...register("password", passwordRules())}
                placeholder="Password"
                errors={errors}
              />
              
              <RouterLink to="/recover-password" className="main-link">
                Forgot Password?
              </RouterLink>
              
              <Button 
                variant="solid" 
                type="submit" 
                loading={isSubmitting} 
                size="md"
                width="100%"
              >
                Sign In with Email
              </Button>
            </VStack>
          ) : (
            <PhoneAuth
              onSendOTP={handleSendOTP}
              onVerifyOTP={handleVerifyOTP}
              loading={sendOTPMutation.isPending || verifyOTPMutation.isPending}
              error={error}
            />
          )}
        </Box>

        <Text textAlign="center">
          Don't have an account?{" "}
          <RouterLink to="/signup" className="main-link">
            Sign Up
          </RouterLink>
        </Text>
      </VStack>
    </Container>
  )
}
