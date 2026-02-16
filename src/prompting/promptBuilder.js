const fs = require('fs');
const path = require('path');
const YAML = require('yaml');

const DEFAULT_TEMPLATE_PATH = path.join(__dirname, '..', 'config', 'prompt_templates.yml');

function loadTemplates(templatePath = DEFAULT_TEMPLATE_PATH) {
    const raw = fs.readFileSync(templatePath, 'utf8');
    return YAML.parse(raw).templates;
}

function chooseTemplate(templates, intentId, variant = 'summary') {
    const intentTemplates = templates[intentId] || templates.generalInfo || {};
    return intentTemplates[variant] || intentTemplates.default || templates.fallback?.reject;
}

function render(templateStr, variables = {}) {
    return Object.keys(variables).reduce((acc, key) => {
        const token = new RegExp(`{{${key}}}`, 'g');
        return acc.replace(token, variables[key] ?? '');
    }, templateStr);
}

function buildPrompt({ query, intentId, variant = 'summary', variables = {}, templates }) {
    const catalog = templates || loadTemplates();
    const chosen = chooseTemplate(catalog, intentId, variant);
    if (!chosen) {
        return {
            prompt: '',
            templateId: null,
            error: 'No template found'
        };
    }

    const userBlock = render(chosen.user, { query, ...variables });
    const systemBlock = render(chosen.system || '', { query, ...variables });
    const prompt = [systemBlock.trim(), userBlock.trim()].filter(Boolean).join('\n\n');

    return {
        prompt,
        templateId: chosen.templateId,
        variablesUsed: Object.keys(variables),
        intentId,
        variant
    };
}

module.exports = {
    loadTemplates,
    chooseTemplate,
    render,
    buildPrompt
};
