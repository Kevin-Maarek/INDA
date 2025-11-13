*מומלץ להציץ באחד מפרויקטי הRAG שלי: https://github.com/Kevin-Maarek/qrag_v2

*שאלות שמערכת ניתוח משובים ענתה עליהם בהצלחה

תציג לי את כל הביקורות.

תראה לי את כל הביקורות של שירות X

תציג לי את כל הביקורות שקיבלו ציון מתחת ל־3

מה הדירוג הממוצע של שירות X

כמה ביקורות יש לכל שירות?

מה הבעיה העיקרית בשירות X?

האם המשתמשים מרוצים משירות X?

מה הנושא המרכזי של הביקורות שקיבלו ציון נמוך מ־3?

חלק את המשובים ל־5 נושאים מרכזיים.

מה התלונה העיקרית שיש בשירות חידוש ויזה ומה יפתור אותה?

תסכם לי בשלוש שורות מה אנשים חושבים על השירות X

ועוד כמה שאלות מורכבות יותר ומורכבות פחות, אתם מוזמנים לאתגר :-)

*תהליך ההעלאת קובץ הפידבקים יכול לקחת זמן אז כדי לקצר אני מצרף את קובץ הוקטורים שאותו מעלים לQDRANT, נכנסים לhttp://localhost:6333/dashboard#/collections (לאחר הרצה בדוקר) ואז לחיצה על UPLOAD_SNAPSHOT ובcollection name לרשום feedback_embeddings ואז להעלות את הקובץ הנ"ל.
קישור לקובץ הוקטורים: https://drive.google.com/file/d/1Nrjm3T8jpcDA0Iqua4vkblHKbc0h5NVU/view?usp=sharing

לשאלות או בעיה בהרצה - 0542492505 קווין




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
