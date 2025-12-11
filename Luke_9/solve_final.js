const CryptoJS = require('crypto-js');

// Correct Ll from game.js snippet verification
// [67,102,112,109,101,98,116,105,119,113,98,116,118,113,105,104,113,113,109,105]
const Ll = "Cfpmebtiwqbtvqihqqmi";
const Fl = (e, t) => CryptoJS.MD5(e + t).toString();

const colors = ['red', 'green', 'blue'];

// All island hashes
const Rl = {
    island2: "88cf335b3e3d3c1b9bb6a0d063f59657",
    island3: "76998b2425c927aaba89eaeee6bf3814",
    island4: "9e7c55ae3233a9a17d9106e9b1a91f0f",
    island5: "ba49f14ef0faf4c3f38c87fb0bcdc607",
    island6: "d8512e1c7c36ea48e745172fce15fec5",
    island7: "f292f64f5238bba783297fb176a38ee6",
    island8: "1f5563ac27bc67f4607b14948fb6e8ed"
};

// Count lights from the game code
const lightsCount = {
    island2: 3,
    island3: 4,
    island4: 5,
    island5: 5,
    island6: 5,
    island7: 4,
    island8: 3
};

function* generateCombinations(n) {
    if (n === 0) {
        yield [];
        return;
    }
    for (let combo of generateCombinations(n - 1)) {
        for (let c of colors) {
            yield [...combo, c];
        }
    }
}

const solutions = {};

for (let [island, target] of Object.entries(Rl)) {
    console.log(`Solving ${island}...`);
    const numLights = lightsCount[island];

    let found = false;
    // Try exact number of lights first
    for (let combo of generateCombinations(numLights)) {
        const joined = combo.join('');
        const hash = Fl(joined, Ll);
        if (hash === target) {
            console.log(`  ✓ FOUND: ${joined}`);
            solutions[island] = joined;
            found = true;
            break;
        }
    }

    if (!found) {
        console.log(`  ✗ NOT FOUND for ${island}`);
        process.exit(1);
    }
}

// Combine all solutions
const key = ['island2', 'island3', 'island4', 'island5', 'island6', 'island7', 'island8']
    .map(i => solutions[i]).join('');

console.log(`\nCombined key: ${key}`);

// Decrypt the flag
const Pl = "U2FsdGVkX1/A4CVLNIe1W8ClMhbZj4KfPwecI1SDodPne2PXecVMBgxLzZZYBuvQP4Pau5SyrSqlEHjH6ZRvdVqphn8fKVUU9DO8+2iwXLs=";

try {
    const decrypted = CryptoJS.AES.decrypt(Pl, key);
    console.log(`FLAG: ${decrypted.toString(CryptoJS.enc.Utf8)}`);
} catch (e) {
    console.log(`Decryption error: ${e.message}`);
}
