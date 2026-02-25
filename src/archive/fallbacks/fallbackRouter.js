const fs = require('fs');
const path = require('path');
const YAML = require('yaml');

const DEFAULT_POLICY_PATH = path.join(__dirname, '..', 'config', 'fallback_policies.yml');

function loadPolicies(policyPath = DEFAULT_POLICY_PATH) {
    const raw = fs.readFileSync(policyPath, 'utf8');
    return YAML.parse(raw).policies || [];
}

function detectOutOfScope({ intentResult, dataAvailability = {} }) {
    const reasons = [];
    if (intentResult?.isOutOfScope) {
        reasons.push('oos');
    }
    if (dataAvailability.hasClusterData === false) {
        reasons.push('missing-cluster-context');
    }
    if (dataAvailability.isAmbiguous === true) {
        reasons.push('ambiguous');
    }

    return {
        isOOS: reasons.length > 0,
        reasons
    };
}

function applyFallback(reasons, policies = loadPolicies()) {
    for (const policy of policies) {
        if (reasons.includes(policy.match)) {
            return {
                policyId: policy.id,
                action: policy.action,
                reason: policy.match,
                message: policy.message || policy.notes || 'Out of scope'
            };
        }
    }
    return null;
}

function routeFallback({ intentResult, dataAvailability, policies }) {
    const { isOOS, reasons } = detectOutOfScope({ intentResult, dataAvailability });
    if (!isOOS) return null;
    return applyFallback(reasons, policies || loadPolicies());
}

module.exports = {
    loadPolicies,
    detectOutOfScope,
    applyFallback,
    routeFallback
};
