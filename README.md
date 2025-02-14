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

For the deployment of **Bazaprix**, we will use the following infrastructure setup:

1. **Cloud Hosting**: 
    - AWS EC2 for the virtual server hosting.
    - Amazon RDS (MySQL) to host the database securely.
    - Amazon S3 for storing product images.
    - Elastic Load Balancer (ELB) for distributing traffic to multiple instances of the application if required.

2. **Docker**:
    - The application will be containerized using Docker, ensuring consistency across different environments (development, staging, production).
    - Docker Compose will be used to manage multi-container setups like the application server and database.

3. **CI/CD**:
    - Jenkins or GitHub Actions for automated deployment pipelines.
    - GitHub repository for version control and collaboration.

### 1. Dockerize the Application

To deploy the application in a Docker container, create a `Dockerfile` in the root directory of your project:

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

# Start the Django app using the development server (for demo purposes)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 2. Deploying on AWS EC2

1. **Set up an EC2 instance**: Use a free-tier or appropriate EC2 instance for your application.
    - Choose an Amazon Machine Image (AMI) like Ubuntu.
    - Configure security groups to allow access to HTTP (port 80) and SSH (port 22).

2. **Deploy the Docker container**:
    - SSH into the EC2 instance:
    ```bash
    ssh -i "your-aws-key.pem" ubuntu@your-ec2-public-ip
    ```
    - Install Docker:
    ```bash
    sudo apt-get update
    sudo apt-get install docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    ```
    - Build the Docker image and run the container:
    ```bash
    docker build -t bazaprix .
    docker run -d -p 8000:8000 bazaprix
    ```

### 3. Set Up Amazon RDS for MySQL

1. **Create an RDS instance** in the AWS Management Console.
2. **Update `settings.py`** with the RDS endpoint and credentials to connect to the MySQL database.
3. Ensure your RDS instance allows connections from the EC2 instance or from anywhere if necessary.

### 4. Set Up S3 for Static and Media Files

1. **Create an S3 bucket** in the AWS Console.
2. **Configure `settings.py`** for static and media file storage:
    ```python
    AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
    AWS_ACCESS_KEY_ID = 'your-access-key'
    AWS_SECRET_ACCESS_KEY = 'your-secret-key'
    
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    ```

### 5. Set Up Load Balancer (ELB)

1. **Set up an Elastic Load Balancer** in AWS to distribute traffic between multiple EC2 instances if necessary.
2. Ensure that the EC2 instances are configured to listen to traffic on port 80, with your Django app running behind the load balancer.

## Final Thoughts

Once deployed, **Bazaprix** will be available as a fully functional price comparison platform, allowing users to explore products and vendors efficiently. With secure, scalable hosting on AWS and Docker, the platform is capable of handling a large number of users and product listings.

---
