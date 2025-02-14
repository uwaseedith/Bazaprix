# Bazaprix Price Comparison Platform

## Description

**Bazaprix** is a web application designed to empower consumers in Burundi with the ability to compare product prices from various vendors. The platform allows vendors to list their products, while consumers can explore products categorized into food, electronics, fuel, and other essential categories. The core objective is to provide real-time price comparisons and facilitate informed purchasing decisions. The platform also includes features like price alerts and vendor ratings.

## Features

- **Product Listings**: Vendors can list their products, including images, prices, and other product details.
- **Price Comparison**: Consumers can compare prices of products in various categories like food, electronics, fuel, etc.
- **Price Alerts**: Users can set alerts for price changes on specific products.
- **Vendor Profiles**: Each vendor has a profile with their contact information and business details.
- **Save Products**: Consumers can save products for later viewing and comparison.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (with Django templates for dynamic content rendering)
- **Backend**: Python (Django Framework)
- **Database**: MySQL (for storing product, vendor, and feedback data)
- **Authentication**: JWT for user authentication and authorization
- **Deployment**: Docker, AWS 

## How to Set Up the Environment and Project

### Prerequisites

- Python 3.8 or higher
- MySQL
- Node.js (if you have any front-end dependencies)
- Docker (for containerization)
- Git (for version control)
- AWS (account for deployment)

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/your-username/bazaprix.git
cd bazaprix
```

### 2. Set Up the Virtual Environment

Create and activate a virtual environment to manage your project’s dependencies:

```bash
python -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
```

### 3. Install Dependencies

Install all necessary Python and JavaScript dependencies:

```bash
pip install -r requirements.txt  # Install Python dependencies
npm install  # Install JavaScript dependencies (if applicable)
```

### 4. Set Up the Database

Make sure MySQL is running and create a database for the project:

```bash
mysql -u root -p
CREATE DATABASE bazaprix;
```

Update the database settings in your `settings.py` file under the `DATABASES` section with the correct MySQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bazaprix',
        'USER': 'your-username',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Apply Migrations

Run migrations to set up the database tables:

```bash
python manage.py migrate
```

### 6. Create a Superuser (Optional)

To access the Django admin, you can create a superuser:

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

You can now access the application at `http://127.0.0.1:8000/`.

## Deployment Plan

### Infrastructure

For the deployment of **Bazaprix** using Render, we will use the following infrastructure setup:

1. **Cloud Hosting:**
    - **Render Web Service** for hosting the application.
    - **Render Managed Database** (MySQL or PostgreSQL) to host the database securely.
    - Render automatically scales and load-balances traffic across multiple instances as needed.

2. **Docker:**
    - The application will be containerized using Docker, ensuring consistency across different environments (development, staging, production).
    - Docker Compose can be used locally for multi-container setups (e.g., application server and database).

3. **CI/CD:**
    - Render integrates directly with GitHub for automated deployment pipelines.
    - Optionally, use GitHub Actions for additional testing or building Docker images before deploying.
    - GitHub repository for version control and collaboration.

---

### 1. Dockerize the Application

Create a `Dockerfile` in the root directory of your project:

```Dockerfile
# Use the official Python image from Docker Hub
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Start the Django app using Gunicorn (production-ready)
CMD ["gunicorn", "yourproject.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

### 2. Deploying on Render

1. **Create a Web Service on Render:**
    - Log in to your [Render dashboard](https://dashboard.render.com/).
    - Click **New** > **Web Service**.
    - Connect your GitHub repository.
    - Select the **Docker** option—Render will automatically detect the `Dockerfile` in your repository.
    - Specify any required environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`, etc.).
    - Set the port to match your container’s exposed port (e.g., `8000`).

2. **Deploy the Application:**
    - Render will build your Docker image and deploy your application.
    - Use Render’s one-off command feature to run necessary Django management commands (e.g., migrations):
      ```bash
      python manage.py migrate
      ```

---

### 3. Set Up the Managed Database

1. **Create a Managed Database:**
    - In your Render dashboard, create a new **Managed Database** (choose MySQL).

2. **Configure Database Connection:**
    - Update your Django `settings.py` with the database credentials provided by Render.
    - Ensure your application is configured to securely connect to the managed database.

---

### 4. Configure Storage for Static and Media Files

2.  Using Render Object Storage**
    - If available, set up Render’s Object Storage.
    - Configure your application based on Render’s documentation for object storage.

---

### 5. Load Balancing & Scaling

- Render automatically provides load balancing and scaling for your web service.
- Configure auto-scaling options in the Render dashboard to handle increased traffic.

---

## CI/CD Pipeline

- **Automated Deployments:**
    - On every push to the main branch, Render automatically builds and deploys your application.
    - Optionally, integrate GitHub Actions for additional pre-deployment testing or Docker image building.
- **Version Control:**
    - Use your GitHub repository for version control and collaboration.

---

### 6. Video Link
**Link:** https://youtu.be/Ldb5UkxVfRM

---

### 7. Designs
**Link:** https://github.com/uwaseedith/Bazaprix/tree/main/Designs

---


### 8. Schemas
**Link:** https://drive.google.com/file/d/1-fZaI5ahMmED7v8itQ1KiJrBrYmIAjMH/view?usp=sharing

---


### 9. Github Link
**Link:** https://github.com/uwaseedith/Bazaprix

---
