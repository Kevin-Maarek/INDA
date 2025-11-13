# 📘 מערכת ניתוח משובים

מערכת זו כוללת 3 רכיבים עיקריים:

1. **Query Service** 
2. **Indexing Service**  
3. **Frontend (Next.js)**
4. **Qdrant** 

---

## 🧩 מבנה הפרויקט

INDA/  
│  
├── backend/  
│   ├── query_service/           
│   ├── indexing_service/       
│   ├── .env                      
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

---

### 🟧 שלב 3 — הפעלת Indexing Service (פורט 8010)

בטרמינל נוסף:  
cd INDA\backend  
uvicorn indexing_service.app:app --host 0.0.0.0 --port 8010  
 

---

### 🟩 שלב 4 — הפעלת הפרונט־אנד (Next.js) (פורט 3000)

בטרמינל חדש:  
cd INDA\frontend  
npm install  
npm run dev  

דפדפן:  
http://localhost:3000  
 

---


## ✨ מה עוד נשאר לעשות / רעיונות להמשך

• הצגת תהליך ה־DSL בפרונט (steps בלייב)  
• הוספת זיכרון לשיחה מתמשכת  
• יצירת DSL Functions חדשות אוטומטית (self-evolving DSL)  
• הוספת Auth בסיסי (JWT/cookie)  

---

##
