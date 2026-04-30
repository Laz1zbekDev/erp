/* ═══════════════════════════════════════════
   auth.js — Token va sessiya boshqaruvi
   VAZIFASI: Faqat token/role saqlash, tekshirish,
             refresh qilish va yo'naltirish.
   ═══════════════════════════════════════════ */

const API_AUTH_BASE = "http://127.0.0.1:8000/api/v1";

const Auth = {

  /* ────────────────────────────────────────
     SAQLASH
     Nima: localStorage ga token va role yozadi
     Qachon: Login muvaffaqiyatli bo'lganda
  ──────────────────────────────────────── */
  save(accessToken, role) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('role', role);
    // refresh_token → backend Set-Cookie orqali avtomatik saqlaydi
  },

  /* ────────────────────────────────────────
     O'QISH
  ──────────────────────────────────────── */
  getToken() {
    return localStorage.getItem('access_token');
  },

  getRole() {
    return localStorage.getItem('role');
  },

  /* ────────────────────────────────────────
     TEKSHIRISH
     Nima: token bor-yo'qligini tekshiradi
     !! — qiymatni true/false ga aylantiradi
  ──────────────────────────────────────── */
  isLoggedIn() {
    return !!this.getToken();
  },

  /* ────────────────────────────────────────
     CHIQISH
     Nima: localStorage ni tozalab, login ga yuboradi
  ──────────────────────────────────────── */
  logout() {
    // 1. LocalStorage ni tozala
    localStorage.removeItem('access_token');
    localStorage.removeItem('role');

    // 2. Backendga so'rov yuborib, httpOnly cookie dagi refresh_token ni o'chir
    fetch(`${API_AUTH_BASE}/auth/logout`, {
      method: 'POST',
      credentials: 'include'  // cookie ni yuborish uchun shart
    })
    .catch(err => console.error('Logout xatolik:', err))
    .finally(() => {
      // 3. So'rov tugagandan keyin login sahifasiga o't
      window.location.href = '/login.html';
    });
  },

  /* ────────────────────────────────────────
     HIMOYALANGAN SAHIFA TEKSHIRUVI
     Nima: Token yo'q bo'lsa — login ga yuboradi
     Qachon: Har bir himoyalangan sahifa boshida chaqiriladi
  ──────────────────────────────────────── */
  requireLogin() {isLoggedIn
    if (!this.isLoggedIn()) {
      window.location.href = '/login.html';
    }
  },

  /* ────────────────────────────────────────
     ROLE GA QARAB YO'NALTIRISH
     Nima: role ga mos sahifaga o'tkazadi
  ──────────────────────────────────────── */
  redirectByRole(role) {
    const pages = {
      'superadmin': '/superadmin.html',
      'admin':      '/admin/index.html',
      'teacher':    '/teacher.html',
      'student':    '/student.html',
    };

    const page = pages[role];

    if (page) {
      window.location.href = page;
    } else {
      console.error("Noma'lum role:", role);
      Auth.logout();
    }
  },

  /* ────────────────────────────────────────
     TOKEN TEKSHIRISH (serverga so'rov)
     Nima: /auth/me ga so'rov yuborib, token hali
           amal qiladimi yoki yo'qmi tekshiradi
     Qaytadi: true (valid) / false (invalid/expired)
  ──────────────────────────────────────── */
  async verifyToken(role = "admin") {
    const token = this.getToken();
    if (!token) return false;

    // Rolega qarab endpoint tanlash
    // bu yerda object ishlatamiz — if/else dan toza
    const roleEndpoints = {
      admin:      `${API_AUTH_BASE}/auth/admin_me`,
      superadmin: `${API_AUTH_BASE}/auth/superadmin_me`,
      teacher:    `${API_AUTH_BASE}/auth/teacher_me`,
      student:    `${API_AUTH_BASE}/auth/student_me`,
    };

    // Noto'g'ri rol berilsa — xavfsizlik uchun false
    const url = roleEndpoints[role];
    if (!url) {
      console.warn(`Noma'lum rol: ${role}`);
      return false;
    }

    try {
      const res = await fetch(url, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` },
        credentials: "include"
      });

      return res.ok;
    } catch (err) {
      console.error("verifyToken xatolik:", err);
      return false;
    }
  },

  /* ────────────────────────────────────────
     TOKEN YANGILASH (refresh)
     Nima: Cookie dagi refresh_token orqali yangi
           access_token oladi va saqlaydi
     Qaytadi: true (muvaffaqiyatli) / false (xato)

     DIQQAT: Bu — AUTH.JS dagi YAGONA refresh logikasi.
             api.js bu funksiyani chaqiradi, o'zi yozmaydi.
  ──────────────────────────────────────── */
  async refreshToken() {
    try {
      const res = await fetch(`${API_AUTH_BASE}/auth/refresh`, {
        method: "POST",
        credentials: "include" // refresh_token cookie avtomatik yuboriladi
      });

      if (!res.ok) return false;

      const data = await res.json();

      // Yangi access_token ni saqlaymiz
      localStorage.setItem("access_token", data.access_token);

      // Role ham yangilangan bo'lishi mumkin
      if (data.role) {
        localStorage.setItem("role", data.role);
      }

      return true;
    } catch (err) {
      console.error("refreshToken xatolik:", err);
      return false;
    }
  },

  /* ────────────────────────────────────────
     ASOSIY AUTH TEKSHIRUVI (login sahifasi uchun)
     Nima: Foydalanuvchi allaqachon tizimga kirganmi?
           Kirgan bo'lsa — to'g'ri sahifaga yo'naltiradi.
     
     Mantiq:
       1. Access token valid?  → redirect
       2. Refresh ishlaydi?    → redirect
       3. Ikkalasi ham yo'q    → login
  ──────────────────────────────────────── */
  
  async redirectIfLoggedIn() {
    const isValid = await this.verifyToken(this.getRole());
    if (isValid) {
      this.redirectByRole(this.getRole());
      return;
    }

    const refreshed = await this.refreshToken();
    if (refreshed) {
      this.redirectByRole(this.getRole());
    }

    // Token yo'q → hech narsa qilma, login sahifasida qol
  },
};