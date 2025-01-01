from app import app, db, Product

# Wrap the code within the application context
with app.app_context():
    # Manually insert products
    new_products = [
        Product(name="Smartphone", price=699.99, stock=30),
        Product(name="Laptop", price=999.99, stock=20),
        Product(name="Geyser", price=150.00, stock=50),
        Product(name="TV", price=500.00, stock=15),
        Product(name="Fridge", price=600.00, stock=10)
    ]
    
    # Add the products to the database
    db.session.bulk_save_objects(new_products)
    db.session.commit()

    print("Products added successfully!")
