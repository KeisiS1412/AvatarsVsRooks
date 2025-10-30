import fs from 'fs';
import path from 'path';
import { EncBlob } from './crypto';

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
