# 🤝 Influencer Engagement & Sponsorship Coordination Platform (V2)

> A full-stack influencer marketing platform architected for seamless collaboration between **brands** and **influencers**, with **role-based access**, **JWT-secured authentication**, and **Redis-backed performance optimization**.

## 👨‍💻 Author

**Manoj Prathapa**  

## 🚀 Project Overview

**Influencia** is a web-based SaaS platform designed to bridge the gap between **brands**, **sponsors**, and **influencers** through automated campaign management, intelligent matchmaking, and scalable backend infrastructure. The platform is modular, scalable, and aligned with modern engineering practices followed by top-tier tech companies.

This platform simulates the **real-world ad tech flow**, empowering:
- Sponsors to **launch targeted campaigns**
- Influencers to **accept brand deals**
- Admins to **monitor platform activity and engagement**

Built with **Flask + Vue.js**, it leverages:
- 🔐 Secure Authentication (JWT + bcrypt)
- 📊 Redis Caching for performance
- 📅 Celery for task scheduling
- 🔧 Modular Flask API architecture

---

## 🧠 Key Features

### ✅ User Authentication & Authorization
- Secure login using **JWT**
- Passwords hashed with **bcrypt**
- Role-based redirection (Admin, Sponsor, Influencer)

### 🧑‍💼 Role-Based Access System
- **Admins** manage users, oversee the platform
- **Sponsors** create campaigns, manage budgets
- **Influencers** browse ad requests and accept campaigns

### 📈 Campaign & Ad Request Management
- Sponsors create and manage campaigns
- Influencers receive requests, negotiate deals
- Real-time status tracking of campaigns

### 🚀 Performance Optimization
- **Redis** for caching campaign/influencer data
- Fast-loading dashboards with cache fallbacks

### 🧪 Robust Backend Architecture
- RESTful Flask APIs with **Flask-RESTful**
- ORM: **Flask-SQLAlchemy**
- Lightweight and fast: **SQLite** for schema prototyping

### 🖥️ Modern Frontend Stack
- Built using **Vue.js**
- Responsive UI powered by **Bootstrap**
- Dynamic routing via **Vue Router**
- Token handling via **localStorage**

---

## 📂 Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Frontend     | Vue.js, Bootstrap, Axios            |
| Backend      | Flask, Flask-RESTful, Flask-JWT     |
| Database     | SQLite (relational schema)          |
| Caching      | Redis                               |
| Task Queue   | Celery                              |
| Auth         | JWT, bcrypt                         |
| Deployment   | Localhost (Docker-ready)            |

---

## 🗃️ Database Schema

### Entities:
- **User**: `user_id`, `username`, `password`, `role`, `bio`
- **Sponsor**: `sponsor_id`, `user_id`, `company`, `sector`, `budget`
- **Influencer**: `influencer_id`, `user_id`, `specialization`, `audience_size`
- **Campaign**: `campaign_id`, `sponsor_id`, `title`, `description`, `start_date`, `end_date`, `visibility`, `budget`
- **Ad Request**: `request_id`, `campaign_id`, `influencer_id`, `requirements`, `payment_amount`, `status`

---

## 🔌 API Endpoints

### Campaigns
- `GET /api/campaigns-list` — Fetch all campaigns  
- `POST /api/campaigns` — Create a new campaign  

### Ad Requests
- `POST /sponsor/add_adRequest_data` — Add ad request  
- `GET /api/requests` — View all requests  

### Influencers
- `GET /api/creators` — Fetch influencers list  

### Auth
- `POST /auth/login` — JWT login  

---

## 🎯 Why This Project Matters

This platform reflects my ability to:
- Design real-world systems used in **ad-tech and influencer marketplaces**
- Implement **full-stack microservice-style solutions**
- Manage **data consistency, security, and performance** at scale
- Combine backend + frontend + DevOps thinking like a **Product Engineer**

---

## 📈 Future Enhancements
- ML-based influencer-brand matching (audience fit, pricing models)
- Admin dashboards with advanced analytics
- Firebase integration for real-time messaging
- Docker containerization for scalable deployment
