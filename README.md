# 📘 README — מערכת ניתוח משובים מבוססת DSL + RAG

מערכת זו כוללת 3 רכיבים עיקריים:

1. **Query Service** — שירות יצירת ה־DSL וביצוע שאילתות (פורט 8004)  
2. **Indexing Service** — שירות קליטת CSV + יצירת אמבדינגים והכנסה ל־Qdrant (פורט 8010)  
3. **Frontend (Next.js)** — ממשק משתמש גרפי (פורט 3000)  
4. **Qdrant** — מסד נתוני וקטורים (רץ בדוקר מקומי)

---

## 🧩 מבנה הפרויקט

INDA/  
│  
├── backend/  
│   ├── query_service/           ← שירות השאילתות וה־DSL  
│   ├── indexing_service/        ← שירות האינדוקס  
│   ├── .env                     ← קובץ משתני סביבה לשני השירותים  
│  
└── frontend/  
    └── (קבצי Next.js)

---

## 🚀 איך מריצים את המערכת?

### שלב 1 — להרים Qdrant בדוקר (פעם אחת בלבד)

פתח טרמינל והרץ:  
docker run -p 6333:6333 qdrant/qdrant  

✔️ עכשיו Qdrant זמין ב־ http://localhost:6333

---

### 🟦 שלב 2 — הפעלת Query Service (פורט 8004)

בטרמינל:  
cd INDA\backend  
uvicorn query_service.app:app --host 0.0.0.0 --port 8004  

השירות הזה אחראי על:  
• הבנת השאלה של המשתמש  
• יצירת DSL אוטומטי  
• הפעלת פונקציות כמו fetch_all_feedbacks, filter_by_level, group_by_topic  
• ביצוע חישובים ושליפת נתונים מ־Qdrant  

---

### 🟧 שלב 3 — הפעלת Indexing Service (פורט 8010)

בטרמינל נוסף:  
cd INDA\backend  
uvicorn indexing_service.app:app --host 0.0.0.0 --port 8010  

השירות הזה מאפשר:  
• העלאת CSV דרך הפרונט  
• יצירת אמבדינגים לכל שורה  
• הכנסת הווקטורים לקולקציה ב־Qdrant  

---

### 🟩 שלב 4 — הפעלת הפרונט־אנד (Next.js) (פורט 3000)

בטרמינל חדש:  
cd INDA\frontend  
npm install  
npm run dev  

דפדפן:  
http://localhost:3000  

הפרונט מבצע:  
• שליחת שאלה לשירות השאילתות (/query על פורט 8004)  
• הצגת התוצאות (טבלאות / טקסט / JSON)  
• העלאת קבצי CSV לאינדוקס (/ingest_csv על פורט 8010)  
• הצגת טעינה / שגיאות בצורה נוחה  

---

## 🔧 קובץ ה־.env לשירותי הבקאנד (backend/.env)


---

## ✨ מה עוד נשאר לעשות / רעיונות להמשך

• הצגת תהליך ה־DSL בפרונט (steps בלייב)  
• הוספת זיכרון לשיחה מתמשכת  
• יצירת DSL Functions חדשות אוטומטית (self-evolving DSL)  
• הוספת Auth בסיסי (JWT/cookie)  
• 
---

##
