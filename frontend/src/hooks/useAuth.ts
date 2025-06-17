import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState, useEffect } from "react"
import type { User, Session } from "@supabase/supabase-js"

import {
  type Body_login_login_access_token as AccessToken,
  type ApiError,
  LoginService,
  type UserPublic,
  type UserRegister,
  UsersService,
} from "@/client"
import { auth, supabase } from "@/lib/supabase"
import { handleError } from "@/utils"

const isLoggedIn = () => {
  // Check both legacy token and Supabase session
  return localStorage.getItem("access_token") !== null || 
         localStorage.getItem("sb-access-token") !== null
}

const useAuth = () => {
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Initialize Supabase auth state
  useEffect(() => {
    // Get initial session
    auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = auth.onAuthStateChange(
      async (event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)

        if (session?.access_token) {
          localStorage.setItem("sb-access-token", session.access_token)
        } else {
          localStorage.removeItem("sb-access-token")
        }

        // Invalidate queries when auth state changes
        queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      }
    )

    return () => subscription.unsubscribe()
  }, [queryClient])

  // Legacy user query for backward compatibility
  const { data: legacyUser } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    enabled: localStorage.getItem("access_token") !== null && !user,
  })

  const signUpMutation = useMutation({
    mutationFn: async (data: UserRegister & { full_name?: string }) => {
      const { data: authData, error } = await auth.signUp(
        data.email,
        data.password,
        { full_name: data.full_name }
      )
      
      if (error) throw error
      return authData
    },
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: (err: any) => {
      setError(err.message || "Sign up failed")
    },
  })

  const signUpWithPhoneMutation = useMutation({
    mutationFn: async (data: { phone: string; password: string; full_name?: string }) => {
      const { data: authData, error } = await auth.signUpWithPhone(
        data.phone,
        data.password,
        { full_name: data.full_name }
      )
      
      if (error) throw error
      return authData
    },
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: (err: any) => {
      setError(err.message || "Phone sign up failed")
    },
  })

  const loginMutation = useMutation({
    mutationFn: async (data: { email: string; password: string }) => {
      const { data: authData, error } = await auth.signIn(data.email, data.password)
      
      if (error) throw error
      return authData
    },
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: (err: any) => {
      setError(err.message || "Login failed")
    },
  })

  const loginWithPhoneMutation = useMutation({
    mutationFn: async (data: { phone: string; password: string }) => {
      const { data: authData, error } = await auth.signInWithPhone(data.phone, data.password)
      
      if (error) throw error
      return authData
    },
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: (err: any) => {
      setError(err.message || "Phone login failed")
    },
  })

  const sendOTPMutation = useMutation({
    mutationFn: async (phone: string) => {
      const { data, error } = await auth.signInWithOTP(phone)
      if (error) throw error
      return data
    },
    onError: (err: any) => {
      setError(err.message || "Failed to send OTP")
    },
  })

  const verifyOTPMutation = useMutation({
    mutationFn: async (data: { phone: string; token: string }) => {
      const { data: authData, error } = await auth.verifyOTP(data.phone, data.token)
      
      if (error) throw error
      return authData
    },
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: (err: any) => {
      setError(err.message || "OTP verification failed")
    },
  })

  const signInWithGoogleMutation = useMutation({
    mutationFn: async (redirectTo?: string) => {
      const { data, error } = await auth.signInWithGoogle(redirectTo)
      if (error) throw error
      return data
    },
    onError: (err: any) => {
      setError(err.message || "Google sign in failed")
    },
  })

  const signInWithAppleMutation = useMutation({
    mutationFn: async (redirectTo?: string) => {
      const { data, error } = await auth.signInWithApple(redirectTo)
      if (error) throw error
      return data
    },
    onError: (err: any) => {
      setError(err.message || "Apple sign in failed")
    },
  })

  const signInWithGitHubMutation = useMutation({
    mutationFn: async (redirectTo?: string) => {
      const { data, error } = await auth.signInWithGitHub(redirectTo)
      if (error) throw error
      return data
    },
    onError: (err: any) => {
      setError(err.message || "GitHub sign in failed")
    },
  })

  const logout = async () => {
    const { error } = await auth.signOut()
    if (error) {
      setError(error.message)
    } else {
      localStorage.removeItem("access_token") // Remove legacy token
      localStorage.removeItem("sb-access-token")
      navigate({ to: "/login" })
    }
  }

  const resetPasswordMutation = useMutation({
    mutationFn: async (email: string) => {
      const { error } = await auth.resetPassword(email)
      if (error) throw error
    },
    onError: (err: any) => {
      setError(err.message || "Password reset failed")
    },
  })

  return {
    signUpMutation,
    signUpWithPhoneMutation,
    loginMutation,
    loginWithPhoneMutation,
    sendOTPMutation,
    verifyOTPMutation,
    signInWithGoogleMutation,
    signInWithAppleMutation,
    signInWithGitHubMutation,
    resetPasswordMutation,
    logout,
    user: user || legacyUser, // Prefer Supabase user, fallback to legacy
    session,
    loading,
    error,
    resetError: () => setError(null),
  }
}

export { isLoggedIn }
export default useAuth
