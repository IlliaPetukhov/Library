# 📚 Library API

**Library API** is a full-featured RESTful backend service for managing books, users, borrowing operations, and online payments via Stripe. Built using Django, Django REST Framework, JWT authentication, and Docker — with support for local development via ngrok and webhook integration.

## 🔧 Features

- 🔐 JWT-based authentication (registration, login, token refresh)
- 📚 Full CRUD operations for books
- 👤 User profiles and role-based access
- 🔄 Borrowing and returning books
- 💳 Stripe Checkout integration for payment processing
- 🔔 Stripe Webhook support for payment status updates
- 🧪 Local tunnel testing via ngrok
- 🐳 Docker support for containerized development
- 📄 Auto-generated API documentation (Swagger & ReDoc)

## 🛠 Tech Stack

**Backend:** Django, Django REST Framework  
**Authentication:** Simple JWT  
**Payments:** Stripe Checkout + Webhooks  
**Documentation:** drf-yasg (Swagger), ReDoc  
**Dev Tools:** Docker, ngrok, Git, virtualenv  
**Database:** SQLite / PostgreSQL (configurable)

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/IlliaPetukhov/Library.git
cd Library

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

## 🧾 Environment Variables

Create a `.env` file in the root directory with the following:

```
SECRET_KEY=your_django_secret_key
DEBUG=True
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

## 🐳 Run with Docker

```bash
# Build and run the container
docker build -t library-api .
docker run -p 8000:8000 library-api
```

## 🌐 Webhook Testing with ngrok

If you're running locally and want to test Stripe webhooks:

```bash
ngrok http 8000
```

Set your Stripe webhook URL to:

```
https://your-ngrok-subdomain.ngrok.io/stripe/webhook/
```

## 🔑 Authentication Endpoints

| Method | Endpoint              | Description                         |
|--------|-----------------------|-------------------------------------|
| POST   | `/api/token/`         | Obtain JWT access and refresh token |
| POST   | `/api/token/refresh/` | Refresh JWT token                   |

## 📘 API Documentation

Once the server is running, visit:

- [http://localhost:8000/swagger/](http://localhost:8000/swagger/) — Swagger UI  
- [http://localhost:8000/redoc/](http://localhost:8000/redoc/) — ReDoc

## 📁 Project Structure

<details>
<summary>Click to expand</summary>

```
Library/
├── user/              # User management & authentication
├── books/             # Book-related endpoints
├── borrow/            # Borrowing/returning logic
├── library_borrow/    # Core settings & URL routing
├── manage.py
├── Dockerfile
├── ngrok.yml
├── requirements.txt
```

</details>

## 👨‍💻 Author

**Illia Petukhov**  
https://github.com/IlliaPetukhov
