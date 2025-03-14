
# **BazaPrix 🛍️**  

📌 **Overview**  
**BazaPrix** is an intelligent price comparison platform that enables consumers to compare real-time prices of essential products across various categories. Vendors can list their products, manage pricing, and receive feedback from customers. The platform also provides AI-powered price insights, product recommendations, and multilingual support to cater to a diverse user base.

---

## **🚀 Key Features**
✅ **User Authentication** (Consumers, Vendors, Admins)  
✅ **Product Management** (Upload, Edit, Delete, View Products)  
✅ **Category-Based Product Listings** (Food, Electronics, Apparel, etc.)  
✅ **AI-Powered Price Insights** (Predictive analytics & trends)  
✅ **Vendor Rating & Feedback System** (Consumers can rate and review vendors)  
✅ **Multilingual Support** (Translate content dynamically)  
✅ **AI-Generated Products** (AI suggests new products based on trends)  
✅ **Email Notifications** (Vendors receive automated emails for new ratings & product updates)  
✅ **Secure Payment Integration** (For premium vendor features)  
✅ **Responsive & Interactive UI** (Modern frontend with Bootstrap)  
✅ **Deployed on Render** (Auto-deployments from GitHub)  
✅ **SQLite/PostgreSQL Database** (Depending on deployment)  

---

## **🛠️ Setup Instructions**

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/uwaseedith/BazaPrix.git
cd BazaPrix
```

### **2️⃣ Set Up Virtual Environment**
```bash
python -m venv myenv
source myenv/bin/activate  # For Linux/macOS
myenv\Scripts\activate  # For Windows
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Configure Environment Variables**
Create a `.env` file in the root directory:

```ini
SECRET_KEY='your-secret-key'
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # ✅ Using SQLite for local development
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='your-email@gmail.com'
EMAIL_HOST_PASSWORD='your-email-password'
```

### **5️⃣ Apply Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **6️⃣ Create Superuser (For Admin Access)**
```bash
python manage.py createsuperuser
```

### **7️⃣ Run the Server**
```bash
python manage.py runserver
```
🔗 **Access the platform at:** `http://127.0.0.1:8000/`

---

## **🚀 Deployment Plan**

### **🏰 Infrastructure Setup**
✅ **Deployed on Render**  
✅ **Frontend:** Static site hosting on Render  
✅ **Backend:** Django application deployed as a Web Service  
✅ **Database:** PostgreSQL (For production) / SQLite3 (For local development)  
✅ **CI/CD:** Auto-deployments from GitHub to Render  
✅ **Security:** SSL/TLS certificates via Let's Encrypt (Auto-provisioned by Render)  

---

### **🚀 Deployment Steps**

#### **1️⃣ Deploy Django Backend on Render**
- Log in to Render and create a new **Web Service**.
- Connect **GitHub repository** to Render.
- Set the build command:
  ```bash
  pip install -r requirements.txt
  ```
- Set the start command:
  ```bash
  gunicorn Baza.wsgi:application
  ```
- Configure **environment variables** in the Render dashboard (`DATABASE_URL`, `EMAIL_HOST`, `SECRET_KEY`).
- Run migrations after deployment:
  ```bash
  python manage.py migrate
  ```

#### **2️⃣ Deploy Frontend on Render**
- Create a **new Static Site** on Render.
- Connect to **GitHub repository** (if separate frontend repo exists).
- Set the build command (if applicable).
- Deploy the static files.

#### **3️⃣ Automated CI/CD Pipeline**
- On every push to the **main** branch, Render **automatically triggers** a build and deployment.
- **Optional:** Use GitHub Actions for pre-deployment testing.

---

## **📩 Email Notifications**
✅ **Users receive automated email notifications for:**
- **New Vendor Ratings** → Vendors are notified when customers leave reviews.
- **Product Updates** → Vendors receive updates when their products are modified.

---

## **🌍 Multi-Language Support**
✅ **Django Translation System (gettext) Integrated**  
✅ **Users can switch languages dynamically**  
✅ **Supports English, French, Spanish, Swahili, and Kinyarwanda**  

---

## **🤖 AI-Powered Price Insights**
✅ **Automated price predictions using AI models**  
✅ **Suggests price trends based on historical data**  
✅ **Provides smart recommendations for competitive pricing**  

---


## **🚀 GitHub Repository**
🔗 **BazaPrix GitHub Repo**: [BazaPrix Repository](https://github.com/uwaseedith/Bazaprix) 
---


## **🎨 Figma UI Design**
🔗 **Figma Link**: [BazaPrix UI Design](https://www.figma.com/design/SQBQLhZn1FqcaLMGmaSBX9/BazaPrix?node-id=1-144&t=uG6fU1Tj0tx0VBjg-0)

---

## **🌍 Live Deployment**
🔗 **BazaPrix on Render**: [Live Site](https://bazaprix.onrender.com)

---

## **🎥 Demo Video**
🔗 **Initial Demo**: [YouTube Link](https://youtu.be/Ldb5UkxVfRM)  
🔗 **Final Product Demo**: [YouTube Link](https://youtu.be/fbyY9DIL6wM)

---

## **🤝 Contribution Guidelines**
1️⃣ Fork the repository.  
2️⃣ Create a new branch (`feature-branch-name`).  
3️⃣ Commit your changes (`git commit -m "Added new feature"`).  
4️⃣ Push to GitHub (`git push origin feature-branch-name`).  
5️⃣ Create a pull request.  

---

## **🎉 Enjoy Shopping with BazaPrix! 🔥**  
