import fs from 'fs';
import path from 'path';
import { EncBlob, decryptJson } from './crypto'; // === NUEVO: import decryptJson
import { DBShape } from './types';               // === NUEVO
import { normalize } from './util';             // === NUEVO

const DATA_FILE = path.resolve(process.env.DATA_FILE || './usuarios.json.enc');

export function readEncryptedFile(): EncBlob | null {
  if (!fs.existsSync(DATA_FILE)) return null;
  const raw = fs.readFileSync(DATA_FILE, 'utf8');
  return JSON.parse(raw) as EncBlob;
}

export function writeEncryptedFile(enc: EncBlob) {
  const tmp = DATA_FILE + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(enc), 'utf8');
  fs.renameSync(tmp, DATA_FILE);
}

// === NUEVO ===
// Carga el DB desencriptado. Si no existe, devuelve una forma vacía.
export async function readDecryptedDb(key: Uint8Array): Promise<DBShape> {
  const enc = readEncryptedFile();
  if (!enc) return { usuarios: [] };
  const db = await decryptJson(enc, key);
  // Defensa por si el archivo está vacío o corrupto
  if (!db || !Array.isArray(db.usuarios)) {
    return { usuarios: [] };
  }
  return db;
}

// Proyección "pública" del usuario (sin hash/sesiones/etc.)
export type PublicPerfil = {
  nombre?: string;
  apellido1?: string;
  apellido2?: string;
  telefono?: string;
  hobbie?: string;
  cumple?: string;
  foto?: string;
  color_preferido?: string;  
  tema_preferido?: string;
  cancion_preferida?: string;  // ← AGREGAR
};

export type PublicUser = {
  username: string;
  email?: string;
  perfil?: PublicPerfil;
  primera_vez?: boolean; 
};

function toPublicUser(u: any): PublicUser | null {
  if (!u) return null;
  const username = u.username ?? u.usuario;
  if (!username) return null;

  const p = u.perfil ?? u.profile ?? {};

  // Extraer apellidos: soporta 'apellido1'/'apellido2' o 'apellidos' en una sola cadena
  let apellido1: string | undefined = p.apellido1;
  let apellido2: string | undefined = p.apellido2;

  if ((!apellido1 && !apellido2) && typeof p.apellidos === "string") {
    const parts = p.apellidos.trim().split(/\s+/);
    apellido1 = parts[0] || "";
    apellido2 = parts.slice(1).join(" ") || "";
  }

  return {
    username,
    email: u.email ?? p.email,
    perfil: {
      nombre: p.nombre ?? p.first_name,
      apellido1,
      apellido2,
      telefono: p.telefono ?? u.telefono,
      hobbie: p.hobbie ?? p.hobby,
      cumple: p.cumple ?? p.fecha_nacimiento ?? p.birthday,
      foto: p.foto ?? u.avatar,
      color_preferido: p.color_preferido,  // ← AGREGAR
      tema_preferido: p.tema_preferido,
      cancion_preferida: p.cancion_preferida, 
    },
    primera_vez: u.primera_vez ?? false,
  };
}

// Búsqueda por username (case/normalizado) y proyección a PublicUser
export async function getPublicUserByUsername(username: string, key: Uint8Array): Promise<PublicUser | null> {
  const db = await readDecryptedDb(key);
  const needle = normalize(username);
  const found = db.usuarios.find(
    (u: any) => normalize(u?.username) === needle || normalize(u?.usuario) === needle
  );
  return toPublicUser(found);
}
// === FIN NUEVO ===
