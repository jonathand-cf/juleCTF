const express = require("express");
const multer = require("multer");
const Database = require("better-sqlite3");

const app = express();
app.use(multer().none());

const db = new Database("presents.db");

const FLAG_BONUS = process.env.FLAG_BONUS || "JUL{dummy_flag_bonus}";

db.exec(`
    CREATE TABLE IF NOT EXISTS present (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        info TEXT NOT NULL
    );

    INSERT OR IGNORE INTO present (name, info) VALUES ('flag', '${FLAG_BONUS}');
`);


app.post("/present/info", (req, res) => {
    const { presentname, roles } = req.body;

    if (!roles.includes("santa") && !roles.includes("toy-maker")) {
        return res.status(403).send("Access denied");
    }

    const stmt = db.prepare("SELECT info FROM present WHERE name = ?");
    const present = stmt.get(presentname);

    if (!present) {
        return res.status(404).send("Present not found");
    }

    res.status(200).send(present.info);
});

app.listen(1337, () => {
    console.log("Present server running on port 1337");
});
