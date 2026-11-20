// Proxy du serveur de développement : /api vers l'API FastAPI (`uv run couverture api`, port 8001).
//
// La clé de l'API n'entre jamais dans le navigateur : ce proxy la lit dans le `.env` du projet
// (`COUVERTURE_API_KEY`, ou la variable d'environnement du même nom) et l'ajoute à chaque appel.
// En production, c'est le serveur placé devant l'API (nginx, passerelle) qui l'ajoute.

import { existsSync, readFileSync } from 'node:fs';

function lireCle() {
    if (process.env.COUVERTURE_API_KEY) {
        return process.env.COUVERTURE_API_KEY;
    }
    const env = new URL('../.env', import.meta.url);
    if (!existsSync(env)) {
        return '';
    }
    for (const ligne of readFileSync(env, 'utf-8').split(/\r?\n/)) {
        const m = ligne.match(/^\s*COUVERTURE_API_KEY\s*=\s*(.*?)\s*$/);
        if (m) {
            return m[1].replace(/^(['"])(.*)\1$/, '$2');
        }
    }
    return '';
}

const cle = lireCle();
if (!cle) {
    console.warn('COUVERTURE_API_KEY introuvable (.env du projet) : l’API refusera les appels.');
}

export default {
    '/api': {
        target: process.env.COUVERTURE_API_URL ?? 'http://localhost:8001',
        secure: false,
        changeOrigin: true,
        headers: { 'x-api-key': cle }
    }
};
