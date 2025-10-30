import fs from 'fs';
import path from 'path';
import sodium from 'libsodium-wrappers';

const KEY_FILE = path.resolve('secret.key');

export async function loadOrCreateKey(): Promise<Uint8Array> {
  await sodium.ready;

  const envKey = process.env.KEY_B64?.trim();
  if (envKey) {
    return sodium.from_base64(envKey, sodium.base64_variants.ORIGINAL);
  }

  if (fs.existsSync(KEY_FILE)) {
    const b64 = fs.readFileSync(KEY_FILE, 'utf8').trim();
    return sodium.from_base64(b64, sodium.base64_variants.ORIGINAL);
  }

  const key = sodium.randombytes_buf(sodium.crypto_aead_xchacha20poly1305_ietf_KEYBYTES);
  const b64 = sodium.to_base64(key, sodium.base64_variants.ORIGINAL);
  fs.writeFileSync(KEY_FILE, b64, 'utf8');
  return key;
}

export type EncBlob = { nonce_b64: string; ct_b64: string };

export async function encryptJson(obj: unknown, key: Uint8Array): Promise<EncBlob> {
  await sodium.ready;
  const ad: Uint8Array | null = null;
  const nonce = sodium.randombytes_buf(sodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES);
  const plaintext = Buffer.from(JSON.stringify(obj), 'utf8');

  const ct = sodium.crypto_aead_xchacha20poly1305_ietf_encrypt(plaintext, ad, null, nonce, key);

  return {
    nonce_b64: sodium.to_base64(nonce, sodium.base64_variants.ORIGINAL),
    ct_b64: sodium.to_base64(ct, sodium.base64_variants.ORIGINAL),
  };
}

export async function decryptJson(blob: EncBlob, key: Uint8Array): Promise<any> {
  await sodium.ready;
  const ad: Uint8Array | null = null;
  const pt = sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(
    null,
    sodium.from_base64(blob.ct_b64, sodium.base64_variants.ORIGINAL),
    ad,
    sodium.from_base64(blob.nonce_b64, sodium.base64_variants.ORIGINAL),
    key
  );
  return JSON.parse(Buffer.from(pt).toString('utf8'));
}
