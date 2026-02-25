const fs = require('fs');
const path = require('path');

const LOG_DIR = path.join(__dirname, '..', '..', 'logs');

function ensureLogDir() {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}

function writeJsonl(fileName, payload) {
    ensureLogDir();
    const line = JSON.stringify({
        ts: new Date().toISOString(),
        ...payload
    });
    fs.appendFileSync(path.join(LOG_DIR, fileName), line + '\n');
}

module.exports = { LOG_DIR, writeJsonl };
