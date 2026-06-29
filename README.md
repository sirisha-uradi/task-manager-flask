# Task Manager (Flask + Supabase)

A full-stack task management web app built with Python, Flask, and Supabase. Supports creating, editing, completing, and deleting tasks, with due dates, categories, and live filtering — all backed by a real PostgreSQL database via Supabase.

## Features

- ✅ Create, edit, complete, and delete tasks (full CRUD)
- 📅 Due dates for each task
- 🏷️ Categories (General, Work, Personal, Urgent) with colored badges
- 🔍 Filter tasks by status (All / Pending / Completed)
- 📊 Live task counts (pending vs completed)
- ✅ Input validation (no empty/blank tasks)
- 🎨 Clean, responsive UI built with custom CSS

## Tech Stack

- **Backend:** Python, Flask
- **Database:** Supabase (PostgreSQL)
- **Frontend:** HTML, CSS (Jinja2 templating)
- **Version Control:** Git & GitHub

## How It Works

- Flask routes handle all CRUD operations (`/`, `/add`, `/edit/<id>`, `/complete/<id>`, `/delete/<id>`)
- Supabase Python client connects the app to a PostgreSQL `tasks` table
- Environment variables (Supabase URL and API key) are kept out of version control using a `.env` file and `.gitignore`

## Running Locally

1. Clone the repository
   ```bash
   git clone https://github.com/sirisha-uradi/task-manager-flask.git
   cd task-manager-flask