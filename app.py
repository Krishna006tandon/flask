import os
import logging
from flask import Flask, session, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models
from models import User, Product, Category, Cart, Order, OrderItem

# In-memory data storage
users = {}         # userid: User object
products = {}      # productid: Product object  
categories = {}    # categoryid: Category object
carts = {}         # userid: Cart object
orders = {}        # orderid: Order object
order_items = {}   # orderitemid: OrderItem object

# Initialize sample data
def init_sample_data():
    # Create categories
    category_ids = ["mobiles", "mobile_covers", "laptops", "games"]
    category_names = ["Mobile Phones", "Mobile Covers", "Laptops", "Open World Games"]
    
    for i, cat_id in enumerate(category_ids):
        category = Category(
            id=cat_id,
            name=category_names[i],
            description=f"All {category_names[i]} products"
        )
        categories[cat_id] = category
    
    # Add admin user
    admin_id = str(uuid.uuid4())
    admin_user = User(
        id=admin_id,
        username="admin",
        email="admin@example.com",
        password_hash=generate_password_hash("adminpass"),
        is_admin=True,
        is_seller=True
    )
    users[admin_id] = admin_user
    
    # Add seller user
    seller_id = str(uuid.uuid4())
    seller_user = User(
        id=seller_id,
        username="seller",
        email="seller@example.com",
        password_hash=generate_password_hash("sellerpass"),
        is_admin=False,
        is_seller=True
    )
    users[seller_id] = seller_user

    # Add some products
    product_data = [
        {
            "name": "iPhone 15 Pro", 
            "description": "Apple's flagship smartphone with A17 Pro chip and advanced camera system.",
            "price": 999.99,
            "category_id": "mobiles",
            "seller_id": seller_id,
            "details": "The iPhone 15 Pro features a titanium design, 48MP camera with 5x optical zoom, A17 Pro chip with 6-core CPU and 6-core GPU, ProMotion technology with adaptive refresh rates up to 120Hz, and all-day battery life. Available in multiple color options.",
            "image_urls": ["https://via.placeholder.com/800x600?text=iPhone+15+Pro", "https://via.placeholder.com/800x600?text=iPhone+15+Pro+Camera", "https://via.placeholder.com/800x600?text=iPhone+15+Pro+Display"],
            "specs": {"Display": "6.1-inch Super Retina XDR", "Processor": "A17 Pro chip", "Storage": "128GB, 256GB, 512GB, 1TB", "Battery": "All-day battery life"}
        },
        {
            "name": "Samsung Galaxy S24 Ultra", 
            "description": "Premium Android smartphone with S Pen and AI features.",
            "price": 1199.99,
            "category_id": "mobiles",
            "seller_id": seller_id,
            "details": "The Samsung Galaxy S24 Ultra features a large 6.8-inch Dynamic AMOLED display, Snapdragon 8 Gen 3 processor, 200MP main camera with 10x optical zoom, built-in S Pen, and Galaxy AI features. With its titanium frame and Corning Gorilla Armor, it offers premium build quality and durability.",
            "image_urls": ["https://via.placeholder.com/800x600?text=Galaxy+S24+Ultra", "https://via.placeholder.com/800x600?text=S24+Ultra+Camera", "https://via.placeholder.com/800x600?text=S24+Ultra+S+Pen"],
            "specs": {"Display": "6.8-inch Dynamic AMOLED 2X", "Processor": "Snapdragon 8 Gen 3", "RAM": "12GB", "Storage": "256GB, 512GB, 1TB"}
        },
        {
            "name": "Premium Silicone iPhone Case", 
            "description": "Protective silicone case with soft microfiber lining for iPhone models.",
            "price": 29.99,
            "category_id": "mobile_covers",
            "seller_id": seller_id,
            "details": "This premium silicone case provides excellent grip and protection for your iPhone. The soft microfiber lining helps protect your device from scratches, while the silicone exterior offers a comfortable grip. Available in a variety of colors to match your style.",
            "image_urls": ["https://via.placeholder.com/800x600?text=Silicone+iPhone+Case", "https://via.placeholder.com/800x600?text=iPhone+Case+Colors", "https://via.placeholder.com/800x600?text=iPhone+Case+Details"],
            "specs": {"Material": "Silicone with microfiber lining", "Compatibility": "iPhone 13/14/15 series", "Wireless Charging": "Compatible", "Colors": "Multiple options available"}
        },
        {
            "name": "MacBook Pro 16", 
            "description": "Powerful laptop with M3 Pro chip and stunning Liquid Retina XDR display.",
            "price": 2499.99,
            "category_id": "laptops",
            "seller_id": admin_id,
            "details": "The MacBook Pro 16-inch featuring the M3 Pro chip delivers exceptional performance for demanding workflows. With its stunning Liquid Retina XDR display, up to 24-core CPU, 32-core GPU, up to 96GB of unified memory, and up to 22 hours of battery life, it's designed for professionals who need power and portability.",
            "image_urls": ["https://via.placeholder.com/800x600?text=MacBook+Pro+16", "https://via.placeholder.com/800x600?text=MacBook+Pro+Display", "https://via.placeholder.com/800x600?text=MacBook+Pro+Keyboard"],
            "specs": {"Processor": "M3 Pro or M3 Max", "Display": "16.2-inch Liquid Retina XDR", "Memory": "Up to 96GB", "Storage": "Up to 8TB SSD"}
        },
        {
            "name": "Dell XPS 15", 
            "description": "Premium Windows laptop with OLED display and Intel Core processors.",
            "price": 1899.99,
            "category_id": "laptops",
            "seller_id": admin_id,
            "details": "The Dell XPS 15 combines performance and portability with its sleek design. Featuring a stunning 15.6-inch OLED display, latest Intel Core processors, NVIDIA RTX graphics, and a premium CNC machined aluminum chassis. Perfect for creative professionals and power users.",
            "image_urls": ["https://via.placeholder.com/800x600?text=Dell+XPS+15", "https://via.placeholder.com/800x600?text=XPS+Display", "https://via.placeholder.com/800x600?text=XPS+Ports"],
            "specs": {"Processor": "Intel Core i7/i9", "Graphics": "NVIDIA RTX", "Display": "15.6-inch 3.5K OLED", "Memory": "Up to 64GB DDR5"}
        },
        {
            "name": "The Legend of Zelda: Tears of the Kingdom", 
            "description": "Epic open-world adventure game for Nintendo Switch.",
            "price": 59.99,
            "category_id": "games",
            "seller_id": seller_id,
            "details": "The Legend of Zelda: Tears of the Kingdom is the sequel to Breath of the Wild, taking the open-world adventure to new heights. Explore the vast lands and skies of Hyrule with new abilities, craft weapons and vehicles, solve puzzles in sky islands, and discover an epic story.",
            "image_urls": ["https://via.placeholder.com/800x600?text=Zelda+TOTK", "https://via.placeholder.com/800x600?text=Zelda+Gameplay", "https://via.placeholder.com/800x600?text=Zelda+Sky+Islands"],
            "specs": {"Platform": "Nintendo Switch", "Genre": "Action-Adventure", "Players": "1", "Release": "2023"}
        },
        {
            "name": "Red Dead Redemption 2", 
            "description": "Award-winning western-themed open world action-adventure game.",
            "price": 39.99,
            "category_id": "games",
            "seller_id": seller_id,
            "details": "Red Dead Redemption 2 is an epic tale of life in America's unforgiving heartland. The game's vast and atmospheric world provides the foundation for a brand new online multiplayer experience. Play as Arthur Morgan, a member of the Van der Linde gang, as you navigate the decline of the Wild West.",
            "image_urls": ["https://via.placeholder.com/800x600?text=RDR2", "https://via.placeholder.com/800x600?text=RDR2+Gameplay", "https://via.placeholder.com/800x600?text=RDR2+World"],
            "specs": {"Platform": "PlayStation, Xbox, PC", "Genre": "Action-Adventure", "Players": "1 (Story), Multiplayer Online", "Developer": "Rockstar Games"}
        },
        {
            "name": "Samsung Galaxy S24 Case", 
            "description": "Rugged protective case with kickstand for Samsung Galaxy S24 series.",
            "price": 24.99,
            "category_id": "mobile_covers",
            "seller_id": admin_id,
            "details": "This rugged case provides military-grade drop protection for your Samsung Galaxy S24. Features include a built-in kickstand for hands-free viewing, precise cutouts for ports and cameras, raised bezels to protect the screen and camera, and a non-slip grip texture.",
            "image_urls": ["https://via.placeholder.com/800x600?text=Galaxy+S24+Case", "https://via.placeholder.com/800x600?text=Case+Kickstand", "https://via.placeholder.com/800x600?text=Case+Protection"],
            "specs": {"Material": "TPU and Polycarbonate", "Protection": "Military-grade drop tested", "Features": "Built-in kickstand, wireless charging compatible", "Compatibility": "Samsung Galaxy S24 series"}
        }
    ]
    
    for i, p_data in enumerate(product_data):
        product_id = str(uuid.uuid4())
        product = Product(
            id=product_id,
            name=p_data["name"],
            description=p_data["description"],
            price=p_data["price"],
            category_id=p_data["category_id"],
            seller_id=p_data["seller_id"],
            details=p_data["details"],
            image_urls=p_data["image_urls"],
            specs=p_data["specs"],
            created_at=datetime.now()
        )
        products[product_id] = product

# Initialize data
init_sample_data()

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Routes
@app.route('/')
def index():
    featured_products = list(products.values())[:4]  # Get first 4 products as featured
    all_categories = list(categories.values())
    return render_template('index.html', 
                          featured_products=featured_products,
                          categories=all_categories)

@app.route('/category/<category_id>')
def category(category_id):
    if category_id not in categories:
        flash('Category not found', 'error')
        return redirect(url_for('index'))
    
    category_obj = categories[category_id]
    category_products = [p for p in products.values() if p.category_id == category_id]
    
    return render_template('index.html', 
                          products=category_products,
                          current_category=category_obj,
                          categories=list(categories.values()))

@app.route('/product/<product_id>')
def product(product_id):
    if product_id not in products:
        flash('Product not found', 'error')
        return redirect(url_for('index'))
    
    product = products[product_id]
    seller = users.get(product.seller_id)
    category = categories.get(product.category_id)
    
    # Get related products (same category, excluding current product)
    related = [p for p in products.values() 
               if p.category_id == product.category_id and p.id != product_id][:4]
    
    return render_template('product.html', 
                          product=product,
                          seller=seller,
                          category=category,
                          related_products=related)

@app.route('/register', methods=['GET', 'POST'])
def register():
    from forms import RegistrationForm
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        if any(u.username == form.username.data for u in users.values()):
            flash('Username already exists', 'error')
            return render_template('register.html', form=form)
        
        if any(u.email == form.email.data for u in users.values()):
            flash('Email already exists', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            is_seller=form.is_seller.data,
            is_admin=False
        )
        
        # Add to in-memory storage
        users[user_id] = new_user
        
        # Create empty cart for the user
        cart = Cart(user_id=user_id, items={})
        carts[user_id] = cart
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    from forms import LoginForm
    form = LoginForm()
    
    if form.validate_on_submit():
        # Find user by username
        user = next((u for u in users.values() if u.username == form.username.data), None)
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            
            # Create cart if user doesn't have one
            if user.id not in carts:
                carts[user.id] = Cart(user_id=user.id, items={})
                
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Get user's orders
    user_orders = [o for o in orders.values() if o.user_id == current_user.id]
    user_orders.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('profile.html', user=current_user, orders=user_orders)

@app.route('/add_to_cart/<product_id>')
@login_required
def add_to_cart(product_id):
    if product_id not in products:
        flash('Product not found', 'error')
        return redirect(url_for('index'))
    
    cart = carts.get(current_user.id)
    if not cart:
        cart = Cart(user_id=current_user.id, items={})
        carts[current_user.id] = cart
    
    # Add item to cart or increase quantity
    if product_id in cart.items:
        cart.items[product_id] += 1
    else:
        cart.items[product_id] = 1
    
    flash('Product added to cart', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
@login_required
def view_cart():
    cart = carts.get(current_user.id, Cart(user_id=current_user.id, items={}))
    
    # Get product details for cart items
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items.items():
        product = products.get(product_id)
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    cart = carts.get(current_user.id)
    if not cart or product_id not in cart.items:
        flash('Product not in cart', 'error')
        return redirect(url_for('view_cart'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        # Remove item from cart
        del cart.items[product_id]
        flash('Product removed from cart', 'info')
    else:
        # Update quantity
        cart.items[product_id] = quantity
        flash('Cart updated', 'success')
    
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    from forms import CheckoutForm
    form = CheckoutForm()
    
    cart = carts.get(current_user.id, Cart(user_id=current_user.id, items={}))
    
    # Calculate cart total and items
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items.items():
        product = products.get(product_id)
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
    
    if form.validate_on_submit():
        # Create order
        order_id = str(uuid.uuid4())
        new_order = Order(
            id=order_id,
            user_id=current_user.id,
            total=total,
            status='paid',
            shipping_address=f"{form.address.data}, {form.city.data}, {form.postal_code.data}, {form.country.data}",
            created_at=datetime.now()
        )
        orders[order_id] = new_order
        
        # Create order items
        for product_id, quantity in cart.items.items():
            product = products.get(product_id)
            if product:
                item_id = str(uuid.uuid4())
                order_items[item_id] = OrderItem(
                    id=item_id,
                    order_id=order_id,
                    product_id=product_id,
                    quantity=quantity,
                    price=product.price
                )
        
        # Clear cart
        cart.items = {}
        
        flash('Order completed successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('checkout.html', form=form, cart_items=cart_items, total=total)

@app.route('/seller/dashboard')
@login_required
def seller_dashboard():
    if not current_user.is_seller:
        flash('Access denied. Seller account required.', 'error')
        return redirect(url_for('index'))
    
    # Get seller's products
    seller_products = [p for p in products.values() if p.seller_id == current_user.id]
    
    # Get orders containing the seller's products
    seller_orders = []
    for order_id, order in orders.items():
        # Find order items for this order
        order_product_ids = [item.product_id for item in order_items.values() if item.order_id == order_id]
        
        # Check if any of the ordered products belong to this seller
        if any(pid for pid in order_product_ids if pid in [p.id for p in seller_products]):
            seller_orders.append(order)
    
    return render_template('seller_dashboard.html', products=seller_products, orders=seller_orders)

@app.route('/seller/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_seller:
        flash('Access denied. Seller account required.', 'error')
        return redirect(url_for('index'))
    
    from forms import ProductForm
    form = ProductForm()
    
    # Set choices for category field
    form.category_id.choices = [(c.id, c.name) for c in categories.values()]
    
    if form.validate_on_submit():
        product_id = str(uuid.uuid4())
        
        # Create placeholder image URLs (in a real app, image upload would be implemented)
        image_urls = [f"https://via.placeholder.com/800x600?text={form.name.data.replace(' ', '+')}"]
        
        # Parse specifications from form
        specs = {}
        for i in range(1, 4):  # Assuming up to 3 specs
            key = request.form.get(f'spec_key_{i}')
            value = request.form.get(f'spec_value_{i}')
            if key and value:
                specs[key] = value
        
        # Create new product
        new_product = Product(
            id=product_id,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category_id=form.category_id.data,
            seller_id=current_user.id,
            details=form.details.data,
            image_urls=image_urls,
            specs=specs,
            created_at=datetime.now()
        )
        products[product_id] = new_product
        
        flash('Product added successfully', 'success')
        return redirect(url_for('seller_dashboard'))
    
    return render_template('seller_dashboard.html', form=form, categories=list(categories.values()))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    all_users = list(users.values())
    all_products = list(products.values())
    all_orders = list(orders.values())
    all_categories = list(categories.values())
    
    return render_template('admin.html', 
                          users=all_users, 
                          products=all_products, 
                          orders=all_orders,
                          categories=all_categories)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    # Search products by name or description
    search_results = [p for p in products.values() 
                     if query.lower() in p.name.lower() or 
                     query.lower() in p.description.lower()]
    
    return render_template('search.html', 
                          products=search_results, 
                          query=query,
                          categories=list(categories.values()))

@app.route('/theme', methods=['POST'])
def toggle_theme():
    theme = request.form.get('theme', 'light')
    session['theme'] = theme
    return redirect(request.referrer or url_for('index'))

@app.context_processor
def inject_theme():
    return dict(theme=session.get('theme', 'light'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, message="Internal server error"), 500
