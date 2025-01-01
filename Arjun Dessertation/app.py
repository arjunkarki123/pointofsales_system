from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate

# Initialize the Flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pos_system.db'  # Use SQLite for local development
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications
db = SQLAlchemy(app)

# Initialize Flask-Migrate for handling migrations
migrate = Migrate(app, db)

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# Define the Sale model
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

# Initialize the database (run this once)
def create_tables():
    with app.app_context():
        db.create_all()

# Ensure the tables are created on the first run
create_tables()

# Route to display products
@app.route('/')
def index():
    products = Product.query.all()  # Retrieve all products from the database
    return render_template('index.html', products=products)

# Route to add products to the cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    # Get the selected quantity for each product and add it to the cart
    for product_id in request.form:
        quantity = int(request.form[product_id])
        if quantity > 0:
            product = Product.query.get(product_id)
            cart_item = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'total': product.price * quantity
            }
            session['cart'].append(cart_item)

    session.modified = True
    return redirect(url_for('cart'))

# Route to view cart and proceed with sale
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart_items=cart_items)

# Route to process sale and clear cart
@app.route('/process_sale', methods=['POST'])
def process_sale():
    cart_items = session.get('cart', [])
    total_sale = 0
    for item in cart_items:
        product = Product.query.get(item['id'])
        product.stock -= item['quantity']
        db.session.commit()
        
        # Record the sale
        sale = Sale(product_id=item['id'], quantity=item['quantity'], total=item['total'])
        db.session.add(sale)
        total_sale += item['total']
    
    # Clear the cart after processing the sale
    session.pop('cart', None)
    db.session.commit()

    return f"Sale processed successfully! Total: ${total_sale}"

if __name__ == '__main__':
    app.run(debug=True)
