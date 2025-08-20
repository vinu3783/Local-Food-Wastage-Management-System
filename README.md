🍽️ Local Food Wastage Management System
📌 Overview

The Local Food Wastage Management System is a platform designed to connect restaurants, grocery stores, and individuals with surplus food to NGOs and people in need.
It enables listing, claiming, and redistributing surplus food through a Streamlit-based interface backed by an SQL database for storage, CRUD operations, and analytical insights.

🎯 Objectives

♻️ Reduce food wastage by redistributing surplus food.

📍 Provide easy access to available food through filtering & geolocation features.

📊 Offer data-driven insights into food donation trends for better decision-making.

🛠 Skills Used

Python (Data handling & application logic)

SQL (Database management & queries)

Streamlit (Frontend UI)

Data Analysis (Visualizations & insights)

📂 Features

📋 List Surplus Food by providers.

🤝 Claim Food by NGOs or individuals in need.

📝 CRUD Operations for food listings & claims.

🔎 Filtering Options (by city, provider, food type, meal type).

📊 SQL-powered Analytics (15+ queries).

📞 Contact Information for direct communication.

📈 Data Visualization for trends & wastage patterns.

📊 Business Use Cases

✅ Connect surplus food providers to those in need.

✅ Reduce waste by optimizing distribution.

✅ Provide actionable insights into food wastage patterns.

🗄 Dataset

Providers Dataset → providers_data.csv

Receivers Dataset → receivers_data.csv

Food Listings Dataset → food_listings_data.csv

Claims Dataset → claims_data.csv

⚙️ Tech Stack

Backend → SQL Database

Frontend → Streamlit

Programming Language → Python

Data Storage → CSV + SQL

Deployment → Streamlit Cloud / Localhost

📌 SQL Analysis Queries

The project answers key analytical questions, such as:

📍 Number of food providers and receivers in each city.

🏆 Top contributing provider types.

🍲 Total quantity of available food.

🍴 Most claimed meal types.

📉 Claim success rates.

🔄 Distribution patterns & wastage trends.

🚀 Installation & Setup
# Clone the Repository
git clone https://github.com/yourusername/local-food-wastage-management.git
cd local-food-wastage-management

# Install dependencies
pip install -r requirements.txt

# Run Streamlit App
streamlit run app.py
