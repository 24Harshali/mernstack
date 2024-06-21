create a requirement text
Flask==2.0.3
Flask-SQLAlchemy==2.5.1
requests==2.26.0

#config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

#Database model
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)

#main application file
from flask import Flask, jsonify
from config import Config
from models import db, Item
import requests

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/initialize-db', methods=['POST'])
def initialize_db():
    try:
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()

        # Fetch data from third-party API
        response = requests.get('https://api.example.com/data')
        data = response.json()

        # Seed the database
        for item_data in data:
            item = Item(
                name=item_data['name'],
                description=item_data.get('description', ''),
                price=item_data['price']
            )
            db.session.add(item)
        
        db.session.commit()
        return jsonify({"message": "Database initialized and seeded successfully."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
        app.run(debug=True)

#database initialization

from app import app
from models import db

with app.app_context():
    db.create_all()


#for activate virtual enviroment

 On Windows: venv\Scripts\activate

install dependencies
pip install -r requirements.txt

#run database initialization
python seed.py

#run flask application
python app.py

#Create an API to list the all transactions
update models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Boolean, default=False)
    sale_date = db.Column(db.DateTime, nullable=True)
    transactions = db.relationship('Transaction', backref='item', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

#update app.py
from flask import Flask, jsonify, request
from config import Config
from models import db, Item, Transaction
import requests
from datetime import datetime
from sqlalchemy import extract, or_

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/initialize-db', methods=['POST'])
def initialize_db():
    try:
        db.drop_all()
        db.create_all()

        response = requests.get('https://api.example.com/data')
        data = response.json()

        for item_data in data:
            item = Item(
                name=item_data['name'],
                description=item_data.get('description', ''),
                price=item_data['price'],
                sold=item_data.get('sold', False),
                sale_date=datetime.strptime(item_data['sale_date'], '%Y-%m-%d') if item_data.get('sale_date') else None
            )
            db.session.add(item)
        
        db.session.commit()
        return jsonify({"message": "Database initialized and seeded successfully."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/statistics/<int:year>/<int:month>', methods=['GET'])
def get_statistics(year, month):
    try:
        total_sales = db.session.query(db.func.sum(Item.price)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == True
        ).scalar() or 0

        total_sold_items = db.session.query(db.func.count(Item.id)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == True
        ).scalar() or 0

        total_not_sold_items = db.session.query(db.func.count(Item.id)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == False
        ).scalar() or 0

        return jsonify({
            "total_sales": total_sales,
            "total_sold_items": total_sold_items,
            "total_not_sold_items": total_not_sold_items
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

Create an API for statistics
update models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Boolean, default=False)
    sale_date = db.Column(db.DateTime, nullable=True)

#update app.py

from flask import Flask, jsonify, request
from config import Config
from models import db, Item
from datetime import datetime
from sqlalchemy import extract

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/initialize-db', methods=['POST'])
def initialize_db():
    try:
        db.drop_all()
        db.create_all()

        response = requests.get('https://api.example.com/data')
        data = response.json()

        for item_data in data:
            item = Item(
                name=item_data['name'],
                description=item_data.get('description', ''),
                price=item_data['price'],
                sold=item_data.get('sold', False),
                sale_date=datetime.strptime(item_data['sale_date'], '%Y-%m-%d') if item_data.get('sale_date') else None
            )
            db.session.add(item)
        
        db.session.commit()
        return jsonify({"message": "Database initialized and seeded successfully."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/statistics/<int:year>/<int:month>', methods=['GET'])
def get_statistics(year, month):
    try:
        total_sales = db.session.query(db.func.sum(Item.price)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == True
        ).scalar() or 0

        total_sold_items = db.session.query(db.func.count(Item.id)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == True
        ).scalar() or 0

        total_not_sold_items = db.session.query(db.func.count(Item.id)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == False
        ).scalar() or 0

        return jsonify({
            "total_sales": total_sales,
            "total_sold_items": total_sold_items,
            "total_not_sold_items": total_not_sold_items
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

Create an API for bar chart ( the response should contain price range and the number
of items in that range for the selected month regardless of the year )

models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Boolean, default=False)
    sale_date = db.Column(db.DateTime, nullable=True)

app.py
from flask import Flask, jsonify, request
from config import Config
from models import db, Item
from sqlalchemy import extract, func

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/initialize-db', methods=['POST'])
def initialize_db():
    try:
        db.drop_all()
        db.create_all()

        response = requests.get('https://api.example.com/data')
        data = response.json()

        for item_data in data:
            item = Item(
                name=item_data['name'],
                description=item_data.get('description', ''),
                price=item_data['price'],
                sold=item_data.get('sold', False),
                sale_date=datetime.strptime(item_data['sale_date'], '%Y-%m-%d') if item_data.get('sale_date') else None
            )
            db.session.add(item)
        
        db.session.commit()
        return jsonify({"message": "Database initialized and seeded successfully."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/statistics/<int:year>/<int:month>', methods=['GET'])
def get_statistics(year, month):
    try:
        total_sales = db.session.query(func.sum(Item.price)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == True
        ).scalar() or 0

        total_sold_items = db.session.query(func.count(Item.id)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == True
        ).scalar() or 0

        total_not_sold_items = db.session.query(func.count(Item.id)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == False
        ).scalar() or 0

        return jsonify({
            "total_sales": total_sales,
            "total_sold_items": total_sold_items,
            "total_not_sold_items": total_not_sold_items
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/bar-chart/<int:month>', methods=['GET'])
def bar_chart(month):
    try:
        price_ranges = {
            "0 - 100": [0, 100],
            "101 - 200": [101, 200],
            "201 - 300": [201, 300],
            "301 - 400": [301, 400],
            "401 - 500": [401, 500],
            "501 - 600": [501, 600],
            "601 - 700": [601, 700],
            "701 - 800": [701, 800],
            "801 - 900": [801, 900],
            "901 - above": [901, float('inf')]
        }

        result = {}

        for label, (min_price, max_price) in price_ranges.items():
            count = db.session.query(func.count(Item.id)).filter(
                extract('month', Item.sale_date) == month,
                Item.price.between(min_price, max_price)
            ).scalar() or 0
            result[label] = count

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


Create an API for pie chart Find unique categories and number of items from that
category for the selected month regardless of the year.
models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Boolean, default=False)
    sale_date = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(50), nullable=False)

app.py

from flask import Flask, jsonify, request
from config import Config
from models import db, Item
from sqlalchemy import extract, func

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/initialize-db', methods=['POST'])
def initialize_db():
    try:
        db.drop_all()
        db.create_all()

        response = requests.get('https://api.example.com/data')
        data = response.json()

        for item_data in data:
            item = Item(
                name=item_data['name'],
                description=item_data.get('description', ''),
                price=item_data['price'],
                sold=item_data.get('sold', False),
                sale_date=datetime.strptime(item_data['sale_date'], '%Y-%m-%d') if item_data.get('sale_date') else None,
                category=item_data['category']
            )
            db.session.add(item)
        
        db.session.commit()
        return jsonify({"message": "Database initialized and seeded successfully."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/statistics/<int:year>/<int:month>', methods=['GET'])
def get_statistics(year, month):
    try:
        total_sales = db.session.query(func.sum(Item.price)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == True
        ).scalar() or 0

        total_sold_items = db.session.query(func.count(Item.id)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == True
        ).scalar() or 0

        total_not_sold_items = db.session.query(func.count(Item.id)).filter(
            extract('year', Item.sale_date) == year,
            extract('month', Item.sale_date) == month,
            Item.sold == False
        ).scalar() or 0

        return jsonify({
            "total_sales": total_sales,
            "total_sold_items": total_sold_items,
            "total_not_sold_items": total_not_sold_items
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/pie-chart/<int:month>', methods=['GET'])
def pie_chart(month):
    try:
        categories = db.session.query(Item.category, func.count(Item.id)).filter(
            extract('month', Item.sale_date) == month
        ).group_by(Item.category).all()

        result = {}
        for category, count in categories:
            result[category] = count

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


Create an API which fetches the data from all the 3 APIs mentioned above, combines
the response and sends a final response of the combined JSON

app.py

from flask import Flask, jsonify, request
from config import Config
from models import db, Item
from sqlalchemy import extract, func

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Assume your existing routes for statistics, bar-chart, and pie-chart are defined here

@app.route('/combined-data/<int:year>/<int:month>', methods=['GET'])
def combined_data(year, month):
    try:
        # Fetch statistics data
        statistics_response = requests.get(f'http://127.0.0.1:5000/statistics/{year}/{month}')
        statistics_data = statistics_response.json()

        # Fetch bar chart data
        bar_chart_response = requests.get(f'http://127.0.0.1:5000/bar-chart/{month}')
        bar_chart_data = bar_chart_response.json()

        # Fetch pie chart data
        pie_chart_response = requests.get(f'http://127.0.0.1:5000/pie-chart/{month}')
        pie_chart_data = pie_chart_response.json()

        # Combine all data into a single response
        combined_data = {
            "statistics": statistics_data,
            "bar_chart": bar_chart_data,
            "pie_chart": pie_chart_data
        }

        return jsonify(combined_data), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


Frontend task

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transaction Data</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1 {
            text-align: center;
        }
        .container {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }
        .chart-container, .table-container {
            width: 45%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Transaction Data for Selected Month</h1>

    <div class="container">
        <div class="chart-container">
            <h2>Bar Chart (Price Ranges)</h2>
            <canvas id="barChart"></canvas>
        </div>
        <div class="chart-container">
            <h2>Pie Chart (Categories)</h2>
            <canvas id="pieChart"></canvas>
        </div>
    </div>

    <div class="table-container">
        <h2>Transactions Table</h2>
        <table id="transactionsTable">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Price</th>
                    <th>Sold</th>
                    <th>Sale Date</th>
                    <th>Category</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function() {
            // Function to fetch data from API and populate charts and table
            function fetchData(year, month) {
                // Clear previous data
                $('#transactionsTable tbody').empty();

                // Fetch statistics
                $.ajax({
                    url: `/statistics/${year}/${month}`,
                    type: 'GET',
                    success: function(data) {
                        // Populate statistics (optional, can be used for other purposes)
                        console.log('Statistics:', data);
                    },
                    error: function(error) {
                        console.error('Error fetching statistics:', error);
                    }
                });

                // Fetch bar chart data
                $.ajax({
                    url: `/bar-chart/${month}`,
                    type: 'GET',
                    success: function(data) {
                        // Render bar chart
                        renderBarChart(data);
                    },
                    error: function(error) {
                        console.error('Error fetching bar chart data:', error);
                    }
                });

                // Fetch pie chart data
                $.ajax({
                    url: `/pie-chart/${month}`,
                    type: 'GET',
                    success: function(data) {
                        // Render pie chart
                        renderPieChart(data);
                    },
                    error: function(error) {
                        console.error('Error fetching pie chart data:', error);
                    }
                });

                // Fetch transactions table data
                $.ajax({
                    url: `/transactions/${year}/${month}`,  // Replace with actual API endpoint for transactions
                    type: 'GET',
                    success: function(data) {
                        // Populate transactions table
                        populateTransactionsTable(data);
                    },
                    error: function(error) {
                        console.error('Error fetching transactions data:', error);
                    }
                });
            }

            // Function to render bar chart
            function renderBarChart(data) {
                var labels = Object.keys(data);
                var values = Object.values(data);

                var ctx = document.getElementById('barChart').getContext('2d');
                var barChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Number of Items',
                            data: values,
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                }
                            }]
                        }
                    }
                });
            }

            // Function to render pie chart
            function renderPieChart(data) {
                var labels = Object.keys(data);
                var values = Object.values(data);

                var ctx = document.getElementById('pieChart').getContext('2d');
                var pieChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Number of Items',
                            data: values,
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)',
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }

            // Function to populate transactions table
            function populateTransactionsTable(data) {
                var tableBody = $('#transactionsTable tbody');
                $.each(data, function(index, item) {
                    var row = '<tr>' +
                        '<td>' + item.name + '</td>' +
                        '<td>' + item.description + '</td>' +
                        '<td>' + item.price + '</td>' +
                        '<td>' + (item.sold ? 'Yes' : 'No') + '</td>' +
                        '<td>' + (item.sale_date ? new Date(item.sale_date).toLocaleDateString() : '-') + '</td>' +
                        '<td>' + item.category + '</td>' +
                        '</tr>';
                    tableBody.append(row);
                });
            }

            // Call fetchData function with a specific year and month (adjust as needed)
            fetchData(2024, 6);  // Example: Fetch data for June 2024
        });
    </script>
</body>
</html>
