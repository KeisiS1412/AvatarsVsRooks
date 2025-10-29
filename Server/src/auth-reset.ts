import express from 'express';
import crypto from 'crypto';
import argon2 from 'argon2';
import { readEncryptedFile, writeEncryptedFile } from './storage';
import { decryptJson, encryptJson } from './crypto';
import { DBShape, UserRecord } from './types';
import { normalize } from './util';

export async function addPasswordResetRoutes(app: express.Application, key: Uint8Array) {

  function generateToken(length = 32) {
    return crypto.randomBytes(length).toString('hex');
  }

  function hashToken(token: string) {
    return crypto.createHash('sha256').update(token).digest('hex');
  }

  // Solicitar recuperación
  app.post('/auth/request-reset', async (req, res) => {
    const { email } = req.body;
    if (!email) return res.status(400).json({ ok: false, error: 'email_required' });

    const enc = readEncryptedFile();
    if (!enc) return res.status(400).json({ ok: false, error: 'no_data' });

    const db: DBShape = await decryptJson(enc, key);
    const user = db.usuarios.find(u => normalize(u.email) === normalize(email));
    if (!user) return res.json({ ok: true, message: 'Si el email existe, se envió un código' });

    const token = generateToken();
    user.resetTokenHash = hashToken(token);
    user.resetExpires = Date.now() + 15 * 60 * 1000; // 15 min

    const newEnc = await encryptJson(db, key);
    writeEncryptedFile(newEnc);

    // Aquí puedes llamar a tu clase MailSender en Python o usar nodemailer en Node
    console.log(`Token para ${email}: ${token}`); // solo para desarrollo

    return res.json({ ok: true, message: 'Si el email existe, se envió un código' });
  });

  // Confirmar recuperación
  app.post('/auth/confirm-reset', async (req, res) => {
    const { email, token, newPassword } = req.body;
    if (!email || !token || !newPassword)
      return res.status(400).json({ ok: false, error: 'missing_fields' });

    const enc = readEncryptedFile();
    if (!enc) return res.status(400).json({ ok: false, error: 'no_data' });

    const db: DBShape = await decryptJson(enc, key);
    const user = db.usuarios.find(u => normalize(u.email) === normalize(email));
    if (!user || !user.resetTokenHash || !user.resetExpires)
      return res.status(400).json({ ok: false, error: 'invalid_token' });

    if (Date.now() > user.resetExpires) return res.status(400).json({ ok: false, error: 'token_expired' });
    if (hashToken(token) !== user.resetTokenHash) return res.status(400).json({ ok: false, error: 'invalid_token' });

    user.password_hash = await argon2.hash(newPassword, { type: argon2.argon2id });
    delete user.resetTokenHash;
    delete user.resetExpires;

    const newEnc = await encryptJson(db, key);
    writeEncryptedFile(newEnc);

    return res.json({ ok: true, message: 'contraseña_actualizada' });
  });
}
