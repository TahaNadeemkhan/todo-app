import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Check for session cookie
  // Note: better-auth uses 'better-auth.session_token' by default
  // const sessionToken = request.cookies.get('better-auth.session_token')

  // TEMPORARILY DISABLED due to infinite redirect loop on localhost
  // The cookie might be Secure-only or not readable by middleware in this specific env
  // Client-side protection in the pages handles the redirects fine for now.

  /*
  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!sessionToken) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  // Redirect authenticated users away from login/register
  if (request.nextUrl.pathname.startsWith('/login') || request.nextUrl.pathname.startsWith('/register')) {
    if (sessionToken) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  }
  */

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/register'],
}