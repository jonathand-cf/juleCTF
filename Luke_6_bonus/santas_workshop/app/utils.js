const Database = require("better-sqlite3");
const bcrypt = require("bcrypt");
const db = new Database("database.db");

db.exec(`
    CREATE TABLE IF NOT EXISTS elf (
        id VARCHAR(11) PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        verified INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS elf_roles (
        elf_id VARCHAR(11) NOT NULL,
        role_id INTEGER NOT NULL,
        PRIMARY KEY (elf_id, role_id),
        FOREIGN KEY (elf_id) REFERENCES elf(id) ON DELETE CASCADE,
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
    );

    INSERT OR IGNORE INTO roles (name) VALUES ('elf');
    INSERT OR IGNORE INTO roles (name) VALUES ('intern');
    INSERT OR IGNORE INTO roles (name) VALUES ('toy-maker');
    INSERT OR IGNORE INTO roles (name) VALUES ('reindeer');
    INSERT OR IGNORE INTO roles (name) VALUES ('santa');
`);


function getElfRoles(elfId) {
    const stmt = db.prepare(`
        SELECT r.name 
        FROM roles r
        JOIN elf_roles er ON r.id = er.role_id
        WHERE er.elf_id = ?
    `);
    const roles = stmt.all(elfId);
    return roles.map(r => r.name);
}

function addRoleToElf(elfId, roleName) {
    const roleStmt = db.prepare("SELECT id FROM roles WHERE name = ?");
    const role = roleStmt.get(roleName);

    if (!role) {
        throw new Error(`Role "${roleName}" does not exist`);
    }

    const insertStmt = db.prepare("INSERT OR IGNORE INTO elf_roles (elf_id, role_id) VALUES (?, ?)");
    insertStmt.run(elfId, role.id);
}

function getElfWithRoles(elfId) {
    const stmt = db.prepare("SELECT id, username, verified FROM elf WHERE id = ?");
    const elf = stmt.get(elfId);

    if (!elf) {
        return null;
    }

    elf.roles = getElfRoles(elfId);
    return elf;
}

function generateElfId() {
    return Math.floor(Math.random() * 1e11).toString();
}

async function createElf(elfData) {
    const defaults = {
        id: generateElfId(),
        verified: false
    };

    const elf = Object.assign(defaults, elfData);
    elf.password = await bcrypt.hash(elf.password, 12);

    const stmt = db.prepare("INSERT INTO elf (id, username, password, verified) VALUES (?, ?, ?, ?)");
    stmt.run(elf.id, elf.username, elf.password, elf.verified ? 1 : 0);

    return elf.id;
}

module.exports = {
    db,
    getElfRoles,
    addRoleToElf,
    getElfWithRoles,
    generateElfId,
    createElf
};
