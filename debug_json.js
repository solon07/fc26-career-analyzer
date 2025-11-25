const fs = require('fs');
const path = 'parser/output/test_parse.json';

try {
    const rawData = fs.readFileSync(path);
    const data = JSON.parse(rawData);
    
    let players = [];
    if (Array.isArray(data)) {
        for (const db of data) {
            if (db.players) {
                players = db.players;
                break;
            }
        }
    } else if (data.players) {
        players = data.players;
    }

    if (players.length > 0) {
        const validPlayers = players.filter(p => p.playerid !== 0 && p.playerid !== null && p.playerid !== undefined);
        console.log("Valid players count:", validPlayers.length);
        
        const ids = validPlayers.map(p => p.playerid);
        const uniqueIds = new Set(ids);
        console.log("Unique valid IDs:", uniqueIds.size);
        
        if (uniqueIds.size < ids.length) {
            console.log("Duplicate IDs found!");
            // Count occurrences
            const counts = {};
            ids.forEach(id => counts[id] = (counts[id] || 0) + 1);
            const duplicates = Object.entries(counts).filter(([id, count]) => count > 1);
            console.log("Sample duplicates:", duplicates.slice(0, 5));
        } else {
            console.log("All valid IDs are unique.");
        }
    }
} catch (e) {
    console.error("Error:", e.message);
}
