# DS_Predictor

A comprehensive data science project framework demonstrating the complete workflow: **Web Scraping → Data Processing → Predictive Modeling**

## 🚀 Quick Start

This repository provides a production-ready environment for building end-to-end data science projects, from web data collection through ETL pipelines to predictive modeling and deployment.

## Database setup

### 1. Install PostgreSQL

Download and install PostgreSQL from: https://www.postgresql.org/download/windows/

During installation, remember the password you set for the `postgres` user.

### 2. Create Database

Open **pgAdmin** or use **psql** command line:

```sql
CREATE DATABASE car_data;
```

### 3. Configure Database Connection

Edit `config.yaml` and update the database section with your credentials:

```yaml
database:
  host: "localhost"
  port: 5432
  dbname: "car_data"
  user: "postgres"
  password: "your_password_here"  # Replace with your PostgreSQL password
  table_name: "car_listings"
```

### 📚 Documentation

- **[Installation Instructions](markdown/install-instructions.md)** - Complete setup guide for Miniconda, environment configuration, and verification

## 📋 Prerequisites

- Python 3.9+
- Miniconda or Anaconda (see installation guide)
- Basic knowledge of Python and data science concepts

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---