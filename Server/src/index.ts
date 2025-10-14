import 'dotenv/config';
import express from 'express';
import argon2 from 'argon2';
import { loadOrCreateKey, encryptJson, decryptJson } from './crypto';
import { readEncryptedFile, writeEncryptedFile } from './storage';
import { ensureDb, isAlnumMax8, isEmailBasic, normalize, nowIso, uuid } from './util';
import { DBShape, RegisterReq, UserRecord } from './types';

async function main() {
  const app = express();
  app.use(express.json({ limit: '1mb' }));

  const key = await loadOrCreateKey();

  app.get('/health', (_req, res) => res.json({ ok: true, ts: Date.now() }));

  // REGISTER
  app.post('/auth/register', async (req, res) => {
    try {
      const body = req.body as RegisterReq;

      if (!body?.acepto_tyc) return res.status(400).json({ ok: false, field: 'acepto_tyc', error: 'required' });
      if (!body?.cuenta?.username || !body?.cuenta?.email || !body?.cuenta?.password || !body?.cuenta?.password_confirm)
        return res.status(400).json({ ok: false, field: 'password', error: 'required' });
      if (!isAlnumMax8(body.cuenta.password))
        return res.status(400).json({ ok: false, field: 'password', error: 'invalid_format' });
      if (body.cuenta.password !== body.cuenta.password_confirm)
        return res.status(400).json({ ok: false, field: 'password', error: 'mismatch' });
      if (!isEmailBasic(body.cuenta.email))
        return res.status(400).json({ ok: false, field: 'email', error: 'invalid_format' });

      const enc = readEncryptedFile();
      let db: DBShape = ensureDb(enc ? await decryptJson(enc, key) : null);

      const userExists = db.usuarios.find(u => normalize(u.username) === normalize(body.cuenta.username));
      if (userExists) return res.status(409).json({ ok: false, field: 'username', error: 'already_exists' });

      const emailExists = db.usuarios.find(u => normalize(u.email) === normalize(body.cuenta.email));
      if (emailExists) return res.status(409).json({ ok: false, field: 'email', error: 'already_exists' });

      const password_hash = await argon2.hash(body.cuenta.password, { type: argon2.argon2id });
      const user: UserRecord = {
        id: uuid(),
        username: body.cuenta.username,
        email: body.cuenta.email,
        password_hash,
        perfil: body.perfil,
        pago: body.pago,
        acepto_tyc: true,
        createdAt: nowIso(),
        updatedAt: nowIso()
      };
      db.usuarios.push(user);

      const newEnc = await encryptJson(db, key);
      writeEncryptedFile(newEnc);
      return res.status(201).json({ ok: true, id: user.id, createdAt: user.createdAt });
    } catch (err) {
      console.error(err);
      res.status(500).json({ ok: false, error: 'internal_error' });
    }
  });

  // LOGIN
  app.post('/auth/login', async (req, res) => {
    try {
      const { username_or_email, password } = req.body;
      if (!username_or_email || !password)
        return res.status(400).json({ ok: false, error: 'bad_request' });

      const enc = readEncryptedFile();
      if (!enc) return res.status(401).json({ ok: false, error: 'invalid_credentials' });

      const db: DBShape = await decryptJson(enc, key);
      const user = db.usuarios.find(
        u => normalize(u.username) === normalize(username_or_email) || normalize(u.email) === normalize(username_or_email)
      );
      if (!user) return res.status(401).json({ ok: false, error: 'invalid_credentials' });

      const valid = await argon2.verify(user.password_hash, password);
      if (!valid) return res.status(401).json({ ok: false, error: 'invalid_credentials' });

      return res.status(200).json({ ok: true, user: { id: user.id, username: user.username } });
    } catch (err) {
      console.error(err);
      res.status(500).json({ ok: false, error: 'internal_error' });
    }
  });

  const PORT = Number(process.env.PORT || 3007);
  app.listen(PORT, () => console.log(`Servidor corriendo en http://localhost:${PORT}`));
}

main();
