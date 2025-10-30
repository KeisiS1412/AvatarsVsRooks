import crypto from 'crypto';
import { DBShape } from './types';

export function uuid(): string {
  return crypto.randomUUID();
}

export function nowIso(): string {
  return new Date().toISOString();
}

export function normalize(s: string): string {
  return (s || '').trim().toLowerCase();
}

export function ensureDb(db: DBShape | null): DBShape {
  return db && Array.isArray(db.usuarios) ? db : { usuarios: [] };
}

export function isAlnumMax8(s: string): boolean {
  if (typeof s !== 'string') return false;
  if (s.length === 0 || s.length > 8) return false;
  for (let c of s) {
    if (!(/[A-Za-z0-9]/.test(c))) return false;
  }
  return true;
}

export function isEmailBasic(s: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}
