Django Project README

## Overview

This is a Django web application project. It provides \[brief description of your project's purpose, e.g., a blog platform, e-commerce site, etc.\].

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- PostgreSQL

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/nguyenbaduy011/IE229_be
   cd IE229_be
   ```

2. **Set up environment variables**:

   - Copy the `.env.example` file to create a `.env` file:

     ```bash
     cp .env.example .env
     ```

   - Edit the `.env` file to include your specific configuration (e.g., database credentials, secret key, etc.). Example fields in `.env.example`:

     ```
     SECRET_KEY=your-secret-key
     DATABASE_URL=your-database-url
     DEBUG=True
     ```

3. **Install dependencies**: Run the following command to install all required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**:

   - Ensure the database settings in `.env` are correct.
   - Run migrations to set up the database:

     ```bash
     python manage.py migrate
     ```

5. **Run the development server**: Start the Django development server:

   ```bash
   python manage.py runserver
   ```

   The application will be available at `http://127.0.0.1:8000/`.
