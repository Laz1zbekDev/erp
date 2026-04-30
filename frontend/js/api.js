/* ═══════════════════════════════════════════
   api.js — Backend bilan muloqot
   VAZIFASI: Faqat HTTP so'rovlarni yuborish.
             Token/sessiya logikasi — auth.js da.
   
   ⚠️ SHART: Bu fayl auth.js dan KEYIN yuklanishi kerak.
              <script src="auth.js"></script>
              <script src="api.js"></script>
   ═══════════════════════════════════════════ */

const API_BASE = "http://127.0.0.1:8000/api/v1";

const Api = {

  /* ────────────────────────────────────────
     LOGIN
     Nima: username/password yuborib, token oladi
           va Auth.save() orqali saqlaydi
     Qaytadi: { access_token, role, token_type }
     
     Nima uchun URLSearchParams?
       FastAPI OAuth2PasswordRequestForm faqat
       application/x-www-form-urlencoded qabul qiladi,
       JSON emas.
  ──────────────────────────────────────── */
  async login(username, password) {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
      credentials: 'include', // refresh_token cookie ni qabul qilish uchun
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Login xatolik");
    }

    const data = await response.json();
    // { access_token, role, token_type }

    // Tokenni Auth ga topshiramiz — Api o'zi saqlamaydi
    Auth.save(data.access_token, data.role);

    return data;
  },

  /* ────────────────────────────────────────
     HIMOYALANGAN SO'ROV (universal)
     Nima: Har qanday himoyalangan endpoint ga
           so'rov yuboradi.
     
     Mantiq (2 bosqichli urinish):
       1-urinish: mavjud token bilan
       401 kelsa: Auth.refreshToken() → yangi token
       2-urinish: yangi token bilan
       Baribir 401: Auth.logout() → login sahifasi
     
     Ishlatilishi:
       Api.request('/books')
       Api.request('/books/1', { method: 'DELETE' })
       Api.request('/books', { method: 'POST', body: JSON.stringify({...}) })
  ──────────────────────────────────────── */
  async request(url, options = {}) {
    // Tokenni Auth dan olamiz — Api o'zi saqlamaydi
    const token = Auth.getToken();

    // ── 1-urinish ──
    let response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers, // caller o'z headerlarini qo'sha oladi
      },
      credentials: 'include',
    });

    // ── Token muddati o'tgan bo'lsa ──
    if (response.status === 401) {
      // Refresh logikasi Auth da — Api qayta yozmaydi
      const refreshed = await Auth.refreshToken();

      if (!refreshed) {
        // Refresh ham ishlamadi → chiqish
        Auth.logout();
        return;
      }

      // ── 2-urinish: yangi token bilan ──
      const newToken = Auth.getToken(); // Auth yangilagan tokenni olamiz

      response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers: {
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json',
          ...options.headers,
        },
        credentials: 'include',
      });
    }

    // So'rov muvaffaqiyatsiz (401 dan boshqa xato)
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "So'rov xatolik");
    }

    return await response.json();
  },
};