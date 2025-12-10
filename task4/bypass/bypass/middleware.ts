import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const isAuthenticated = false

export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/protected')) {
    if (!isAuthenticated) {
      console.log('Auth failed - redirecting to /')      
      return NextResponse.redirect(new URL('/', request.url))
    }
  }
  return NextResponse.next()
}

// Protect these paths
export const config = {
  matcher: ['/protected/:path*'],
} 