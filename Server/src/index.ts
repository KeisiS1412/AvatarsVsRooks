import 'dotenv/config';
import express from 'express';
import multer from "multer";
import argon2 from 'argon2';
import fs from 'fs';
import path from 'path';
import { encryptBytes } from './crypto';
import crypto from 'crypto';
import { loadOrCreateKey, encryptJson, decryptJson } from './crypto';
import { readEncryptedFile, writeEncryptedFile } from './storage';
import { ensureDb, isAlnumMax8, isEmailBasic, normalize, nowIso, uuid } from './util';
import { DBShape, RegisterReq, UserRecord } from './types';

// === NUEVO ===
import { getPublicUserByUsername } from './storage'; // para el endpoint de perfil público
// === FIN NUEVO ===

async function main() {
  const app = express();
  app.use(express.json({ limit: '20mb' }));

  const key = await loadOrCreateKey();

  app.get('/health', (_req, res) => res.json({ ok: true, ts: Date.now() }));

  app.post('/auth/register', async (req, res) => {
    try {
      const body = req.body as RegisterReq;

      if (!body?.acepto_tyc)
        return res.status(400).json({ ok: false, field: 'acepto_tyc', error: 'required' });
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
      user.primera_vez = true;

      // --- NUEVO: guardar avatar cifrado si llegó en base64 ---
      try {
        const { avatar_b64, avatar_mime } = body as { avatar_b64?: string; avatar_mime?: string };
        if (avatar_b64) {
          const raw = Buffer.from(avatar_b64, "base64");           // bytes de la imagen
          const encBlob = await encryptBytes(new Uint8Array(raw), key);

          const dir = path.resolve("data", "avatars");
          fs.mkdirSync(dir, { recursive: true });

          const avatarPath = path.join(dir, `${user.id}.bin.enc`);
          fs.writeFileSync(avatarPath, JSON.stringify(encBlob), "utf8");

          user.avatar = {
            path: "./data/avatars/" + `${user.id}.bin.enc`,
            mime: avatar_mime || "application/octet-stream",
          };
        } else {
          user.avatar = null;
        }
      } catch (e) {
        console.error("Error cifrando/guardando avatar:", e);
        user.avatar = null; // no tumbar el registro si falla el avatar
      }


      db.usuarios.push(user);

      const newEnc = await encryptJson(db, key);
      writeEncryptedFile(newEnc);
      return res.status(201).json({ ok: true, id: user.id, createdAt: user.createdAt });
    } catch (err) {
      console.error(err);
      res.status(500).json({ ok: false, error: 'internal_error' });
    }
  });

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

      // Se mantiene la respuesta mínima; el cliente podrá ampliar con /users/:username
      return res.status(200).json({ ok: true, user: { id: user.id, username: user.username } });
    } catch (err) {
      console.error(err);
      res.status(500).json({ ok: false, error: 'internal_error' });
    }
  });

  function generateToken(length = 32) {
    return crypto.randomBytes(length).toString('hex');
  }

  function hashToken(token: string) {
    return crypto.createHash('sha256').update(token).digest('hex');
  }

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
  user.resetExpires = Date.now() + 15 * 60 * 1000; // 15 minutos

  const newEnc = await encryptJson(db, key);
  writeEncryptedFile(newEnc);

  console.log(`Token para ${email}: ${token}`); // visible en consola

  return res.json({ ok: true, token });
});

  // Confirmar recuperación con token + nueva contraseña
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

    if (Date.now() > user.resetExpires)
      return res.status(400).json({ ok: false, error: 'token_expired' });

    if (hashToken(token) !== user.resetTokenHash)
      return res.status(400).json({ ok: false, error: 'invalid_token' });

    user.password_hash = await argon2.hash(newPassword, { type: argon2.argon2id });
    delete user.resetTokenHash;
    delete user.resetExpires;

    const newEnc = await encryptJson(db, key);
    writeEncryptedFile(newEnc);

    return res.json({ ok: true, message: 'contraseña_actualizada' });
  });

  // === NUEVO ===
  // Endpoint de solo lectura para obtener el "perfil público" del usuario
  app.get('/users/:username', async (req, res) => {
    try {
      const username = (req.params.username || '').trim();
      
      if (!username) {
        return res.status(400).json({ ok: false, error: 'missing_username' });
      }
      const pub = await getPublicUserByUsername(username, key);
      
      if (!pub) {
        return res.status(404).json({ ok: false, error: 'not_found' });
      }
      return res.json({ ok: true, user: pub });
    } catch (e) {
      console.error('GET /users/:username error:', e);
      return res.status(500).json({ ok: false, error: 'internal_error' });
    }
  });

  // Actualizar preferencias de usuario 
  app.patch('/users/:username/preferences', async (req, res) => {
    try {
      const username = (req.params.username || '').trim();
      const { color, theme, song } = req.body;

      if (!username) {
        console.log('Error: missing_username');
        return res.status(400).json({ ok: false, error: 'missing_username' });
      }

      if (!color || !theme) {
        console.log('Error: missing_preferences');
        return res.status(400).json({ ok: false, error: 'missing_preferences' });
      }

      const enc = readEncryptedFile();
      if (!enc) {
        console.log('Error: no_data');
        return res.status(404).json({ ok: false, error: 'no_data' });
      }

      const db: DBShape = await decryptJson(enc, key);
      
      const user = db.usuarios.find(u => normalize(u.username) === normalize(username));

      if (!user) {
        console.log(`Usuario ${username} no encontrado`);
        return res.status(404).json({ ok: false, error: 'user_not_found' });
      }

      // Guardar preferencias en el perfil del usuario
      if (!user.perfil) {
        user.perfil = {} as any;
      }
      (user.perfil as any).color_preferido = color;
      (user.perfil as any).tema_preferido = theme;
      if (song !== undefined) (user.perfil as any).cancion_preferida = song;

      user.primera_vez = false;
      user.updatedAt = nowIso();

      const newEnc = await encryptJson(db, key);
      writeEncryptedFile(newEnc);

      console.log(`Preferencias guardadas para ${username}: color=${color}, theme=${theme}`);

      return res.json({ ok: true, message: 'preferences_updated' });
    } catch (err) {
      console.error('PATCH /users/:username/preferences error:', err);
      res.status(500).json({ ok: false, error: 'internal_error' });
    }
  });

  // === FIN NUEVO ===
// === NUEVO BLOQUE: Endpoints para reconocimiento facial ===


  const facesDir = path.resolve("data", "faces");
  if (!fs.existsSync(facesDir)) {
    fs.mkdirSync(facesDir, { recursive: true });
    console.log(" Carpeta 'faces' creada.");
  }

  const storage = multer.diskStorage({
    destination: (_, __, cb) => cb(null, facesDir),
    filename: (req, file, cb) => {
      const username = (req.body.username || "unknown").toLowerCase();
      cb(null, `${username}.npy`);
    },
  });
  const upload = multer({ storage });

  // === BLOQUE CORREGIDO: UPLOAD & VERIFY ===

  app.post("/faces/upload", async (req, res) => {
  try {
    const { username, face_data } = req.body;
    if (!username || !face_data) {
      return res.status(400).json({ ok: false, error: "Faltan datos (username o face_data)" });
    }

    const faceArray = Array.isArray(face_data) ? face_data : JSON.parse(face_data);
    const finalPath = path.join(facesDir, `${username.toLowerCase()}.json`);
    fs.writeFileSync(finalPath, JSON.stringify(faceArray));

    console.log(`✅ Rostro recibido y guardado como ${username}.json`);
    return res.json({ ok: true, filename: `${username}.json` });
  } catch (err) {
    console.error("❌ Error en /faces/upload:", err);
    res.status(500).json({ ok: false, error: "Error interno" });
  }
});

  app.post("/faces/verify", async (req, res) => {
    try {
      const { face_data } = req.body;
      if (!face_data) {
        return res.status(400).json({ ok: false, error: "Falta el rostro" });
      }

      // Normalizar entrada
      const uploadedArray = Array.isArray(face_data)
        ? face_data
        : JSON.parse(face_data);

      const files = fs.readdirSync(facesDir).filter(f => f.endsWith(".json"));
      if (files.length === 0) {
        return res.json({ ok: true, match: false, error: "No hay rostros registrados" });
      }

      let bestMatch: string | null = null;
      let minDistance = Infinity;
      const distances: { file: string; dist: number }[] = [];

      // Calcular distancia con cada rostro guardado
      for (const file of files) {
        const knownArray = JSON.parse(fs.readFileSync(path.join(facesDir, file), "utf8"));
        if (knownArray.length !== uploadedArray.length) continue;

        const dist = Math.sqrt(
          uploadedArray.reduce((sum: number, val: number, i: number) => 
            sum + Math.pow(val - knownArray[i], 2), 
          0)
        );

        distances.push({ file, dist });
        if (dist < minDistance) {
          minDistance = dist;
          bestMatch = file.replace(".json", "");
        }
      }

      // --- NUEVO: calcular umbral dinámico basado en los datos existentes ---
      const avgDist = distances.reduce((acc, d) => acc + d.dist, 0) / distances.length;
      const threshold = Math.max(5000, avgDist * 0.8); // se ajusta automáticamente

      const match = minDistance < threshold;

      console.log("🧠 Verificación facial:");
      console.log("  • Mejor coincidencia:", bestMatch);
      console.log("  • Distancia mínima:", minDistance.toFixed(2));
      console.log("  • Promedio global:", avgDist.toFixed(2));
      console.log("  • Umbral dinámico:", threshold.toFixed(2));
      console.log("  • Resultado final:", match ? "✅ MATCH" : "❌ SIN MATCH");

      res.json({ 
        ok: true, 
        match, 
        username: match ? bestMatch : null, 
        distance: minDistance,
        threshold,
        avgDistance: avgDist
      });
    } catch (err) {
      console.error("❌ Error en /faces/verify:", err);
      res.status(500).json({ ok: false, error: "Error interno" });
    }
  });

  // === FIN BLOQUE NUEVO ===
  const PORT = Number(process.env.PORT || 3007);
  app.listen(PORT, () => console.log(`Servidor corriendo en http://localhost:${PORT}`));
}

main();
