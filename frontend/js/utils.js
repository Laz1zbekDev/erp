/* ── utils.js — yordamchi funksiyalar ── */

const Utils = {

  /* Sanani o'zbek formatida ko'rsatadi: 16.04.2026 */
  formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('ru-RU'); /* 16.04.2026 */
  },

  /* Pulni formatlaydi: 150000 → "150 000 so'm" */
  formatMoney(amount) {
    if (amount == null) return '—';
    return Number(amount).toLocaleString('uz-UZ') + " so'm";
  },

  /* Telefon raqamni formatlaydi: 998901234567 → +998 90 123-45-67 */
  formatPhone(phone) {
    if (!phone) return '—';
    const p = String(phone).replace(/\D/g, '');
    if (p.length === 12) {
      return `+${p.slice(0,3)} ${p.slice(3,5)} ${p.slice(5,8)}-${p.slice(8,10)}-${p.slice(10)}`;
    }
    return phone;
  },

  /* Matn qisqartiradi: "Juda uzun matn..." */
  truncate(str, maxLen = 40) {
    if (!str) return '—';
    return str.length > maxLen ? str.slice(0, maxLen) + '...' : str;
  },

  /* Toast xabar ko'rsatadi (muvaffaqiyat yoki xato) */
  toast(message, type = 'success') {
    const existing = document.getElementById('__toast');
    if (existing) existing.remove();

    const el = document.createElement('div');
    el.id = '__toast';
    el.textContent = message;
    Object.assign(el.style, {
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      padding: '12px 18px',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: '500',
      color: '#fff',
      background: type === 'success' ? '#2d7a4f' : '#c0392b',
      zIndex: '9999',
      opacity: '0',
      transition: 'opacity 0.2s',
    });
    document.body.appendChild(el);
    requestAnimationFrame(() => { el.style.opacity = '1'; });
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 300);
    }, 3000);
  },

  /* Jadval uchun bo'sh holat (ma'lumot yo'q) */
  emptyState(container, message = "Ma'lumot topilmadi") {
    container.innerHTML = `
      <div style="text-align:center;padding:3rem 1rem;color:#888;font-size:14px;">
        ${message}
      </div>`;
  },
};
