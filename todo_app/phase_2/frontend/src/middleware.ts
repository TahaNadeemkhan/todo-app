import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const sessionToken = request.cookies.get('better-auth.session_token')

  // If trying to access a protected route without a token, redirect to login
  if (!sessionToken) {
    // Keep the original requested path so the user is redirected back after login
    const url = request.nextUrl.clone()
    url.pathname = '/login'
    url.searchParams.set('callbackUrl', request.nextUrl.pathname)
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

// Apply this middleware only to the authenticated routes
export const config = {
  matcher: [
    '/dashboard/:path*', 
    '/today/:path*', 
    '/upcoming/:path*', 
    '/completed/:path*',
    '/settings/:path*'
  ],
}
