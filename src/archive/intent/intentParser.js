const fs = require('fs');
const path = require('path');

const DEFAULT_CATALOG_PATH = path.join(__dirname, '..', 'config', 'intent_catalog.json');

function loadIntentCatalog(catalogPath = DEFAULT_CATALOG_PATH) {
    const raw = fs.readFileSync(catalogPath, 'utf8');
    return JSON.parse(raw);
}

function scoreIntent(query, catalog) {
    const text = (query || '').toLowerCase();
    const scores = {};

    for (const intent of catalog.intents) {
        let score = 0;
        for (const keyword of intent.keywords) {
            if (text.includes(keyword.toLowerCase())) {
                score += 1;
            }
        }
        scores[intent.id] = score;
    }

    return scores;
}

function pickIntent(scores, catalog) {
    const entries = Object.entries(scores);
    const [bestIntent, bestScore] = entries.reduce(
        (acc, [intentId, score]) => (score > acc[1] ? [intentId, score] : acc),
        [catalog.defaultIntent, 0]
    );

    const totalScore = entries.reduce((sum, [, score]) => sum + score, 0) || 1;
    const confidence = bestScore / totalScore;
    const oosThreshold = catalog.oosThreshold ?? 0.15;
    const isOutOfScope = confidence < oosThreshold;

    return {
        intentId: bestIntent,
        confidence,
        bestScore,
        isOutOfScope,
        rationale: isOutOfScope
            ? `Confidence ${confidence.toFixed(2)} below threshold ${oosThreshold}`
            : `Matched intent ${bestIntent} with score ${bestScore}`
    };
}

function parseIntent(query, options = {}) {
    const catalog = options.catalog || loadIntentCatalog(options.catalogPath);
    const scores = scoreIntent(query, catalog);
    const selection = pickIntent(scores, catalog);

    return {
        query,
        ...selection,
        scores
    };
}

module.exports = {
    loadIntentCatalog,
    scoreIntent,
    pickIntent,
    parseIntent
};
