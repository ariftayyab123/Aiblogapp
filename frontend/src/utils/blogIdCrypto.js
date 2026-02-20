import CryptoJS from 'crypto-js';

const BLOG_ID_SECRET =
  import.meta.env.VITE_BLOG_ID_SECRET || 'ai-blog-default-secret-change-me';

export function encryptBlogId(id) {
  if (id === null || id === undefined) return '';
  const cipher = CryptoJS.AES.encrypt(String(id), BLOG_ID_SECRET).toString();
  return encodeURIComponent(cipher);
}

export function decryptBlogId(token) {
  if (!token) return null;
  try {
    const decoded = decodeURIComponent(token);
    const bytes = CryptoJS.AES.decrypt(decoded, BLOG_ID_SECRET);
    const plaintext = bytes.toString(CryptoJS.enc.Utf8);
    const id = Number.parseInt(plaintext, 10);
    return Number.isNaN(id) ? null : id;
  } catch {
    return null;
  }
}

