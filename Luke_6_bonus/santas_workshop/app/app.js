const express = require("express");
const session = require("express-session");
const bodyParser = require("body-parser");
const bcrypt = require("bcrypt");
const path = require("path");

const { db, getElfRoles, addRoleToElf, getElfWithRoles, createElf } = require("./utils");

const app = express();

const PORT = process.env.PORT || 8000;
const PRESENT_API = process.env.PRESENT_SERVER_URL || "http://localhost:1337";

const FLAG = process.env.FLAG || "JUL{dummy_flag}";

const publicDir = path.join(__dirname, "public");

const sessionSecret = require("crypto").randomBytes(64).toString("hex");

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(session({
    secret: sessionSecret,
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false }
}));

app.use(express.static(publicDir));

const isAuthenticated = (req, res, next) => {
    if (req.session.userId) {
        next();
    } else {
        res.status(401).json({ error: "Not authenticated" });
    }
};

const isVerified = (req, res, next) => {
    const elf = getElfWithRoles(req.session.userId);
    if (elf && elf.verified) {
        next();
    } else {
        res.status(403).json({ error: "Account not verified. Please wait for Santa's approval." });
    }
};

const sendPublicFile = (res, filename) => res.sendFile(path.join(publicDir, filename));

app.get("/", (req, res) => {
    if (req.session.userId) {
        res.redirect("/workshop");
    } else {
        sendPublicFile(res, "index.html");
    }
});

app.get("/register", (req, res) => {
    if (req.session.userId) {
        res.redirect("/workshop");
    } else {
        sendPublicFile(res, "register.html");
    }
});

app.get("/login", (req, res) => {
    if (req.session.userId) {
        res.redirect("/workshop");
    } else {
        sendPublicFile(res, "login.html");
    }
});

app.get("/workshop", (req, res) => {
    if (!req.session.userId) {
        res.redirect("/login");
    } else {
        const elf = getElfWithRoles(req.session.userId);
        if (!elf || !elf.verified) {
            return res.status(403).send("Account not verified. Please wait for admin approval.");
        }
        sendPublicFile(res, "dashboard.html");
    }
});

app.post("/api/workshop/register", async (req, res) => {
    try {
        const { username, password } = req.body;

        if (!username || !password) {
            return res.status(400).json({ error: "Elf name and secret code are required" });
        }

        if (password.length < 6) {
            return res.status(400).json({ error: "Secret code must be at least 6 characters" });
        }

        const userId = await createElf(req.body);

        addRoleToElf(userId, "elf");
        addRoleToElf(userId, "intern");

        res.json({
            success: true,
            message: "Elf registered successfully. Please wait for admin verification.",
        });
    } catch (error) {
        if (error.message.includes("UNIQUE constraint failed")) {
            res.status(400).json({ error: "Elf name already exists" });
        } else {
            console.error("Registration error:", error);
            res.status(500).json({ error: "Registration failed" });
        }
    }
});

app.post("/api/workshop/login", async (req, res) => {
    try {
        const { username, password } = req.body;

        if (!username || !password) {
            return res.status(400).json({ error: "Elf name and secret code are required" });
        }

        const stmt = db.prepare("SELECT * FROM elf WHERE username = ?");
        const elf = stmt.get(username);

        if (!elf) {
            return res.status(401).json({ error: "Invalid credentials" });
        }

        const validPassword = await bcrypt.compare(password, elf.password);

        if (!validPassword) {
            return res.status(401).json({ error: "Invalid credentials" });
        }

        const roles = getElfRoles(elf.id);

        req.session.userId = elf.id;
        req.session.username = elf.username;
        req.session.roles = roles;

        res.json({
            success: true,
            message: "Welcome to the workshop!",
        });
    } catch (error) {
        console.error("Login error:", error);
        res.status(500).json({ error: "Login failed" });
    }
});

app.post("/api/workshop/logout", (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).json({ error: "Logout failed" });
        }
        res.json({ success: true, message: "Logged out successfully" });
    });
});

app.get("/api/workshop/elf", isAuthenticated, (req, res) => {
    const elf = getElfWithRoles(req.session.userId);

    if (elf) {
        res.json({ elf: elf });
    } else {
        res.status(404).json({ error: "Elf not found" });
    }
});

app.get("/api/workshop/notices", isAuthenticated, isVerified, (_, res) => {
    const notices = [
        { id: 0, message: `Here is a thank you to all the elves who have worked extra hard this season: <b>${FLAG}</b>` }
    ];
    res.json({ notices });
});

app.post("/api/workshop/present", isAuthenticated, isVerified, async (req, res) => {
    const { presentname } = req.body;

    if (!presentname) {
        return res.status(400).json({ error: "The present name is required" });
    }

    let data = new FormData();
    const elf = getElfWithRoles(req.session.userId);

    if (!elf) {
        return res.status(404).json({ error: "Elf not found" });
    }

    data.append("roles", JSON.stringify(elf.roles));
    data.append("presentname", presentname);

    fetch(`${PRESENT_API}/present/info`, {
        body: data,
        method: "POST"
    })
        .then(async r => {
            const body = await r.text();
            res.status(r.status).send(body);
        })
        .catch(_ => {
            res.status(502).send("Proxy error");
        });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
