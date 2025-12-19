"""Main application routes."""
from flask import jsonify, render_template, session
from models import db, Position, Bouquet
from flask import request, redirect, url_for
from dao.user_dao import UserDAO
from models import User


def main_routes(app):
    """Register main application routes."""
    
    @app.route('/')
    def index():
        """Index route."""
        # render a simple HTML page from templates/index.html
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check route."""
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'database': db_status
        })

    @app.route('/shop')
    def shop():
        # list available positions and render shop page
        positions = db.session.query(Position).all()
        return render_template('shop.html', positions=positions)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        # POST: attempt to find user
        name = request.form.get('name')
        password = request.form.get('password')
        udao = UserDAO(User, db.session)
        user = db.session.query(User).filter_by(name=name, password=password).first()
        if not user:
            # simple flow: redirect to register if not found
            return redirect(url_for('register'))
        # set session to mark user as logged in
        session['user_id'] = user.id
        return redirect(url_for('profile', user_id=user.id))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('register.html')
        name = request.form.get('name')
        password = request.form.get('password')
        card = request.form.get('card') or None
        udao = UserDAO(User, db.session)
        # create as regular customer (user_type_id == 2)
        try:
            user = udao.create(name=name, password=password, card=card, user_type_id=2)
        except Exception:
            # fallback: create without explicit user_type_id
            user = udao.create(name=name, password=password, card=card)
        # set session so user is considered logged in
        session['user_id'] = user.id
        return redirect(url_for('profile', user_id=user.id))

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('index'))

    @app.route('/profile/<int:user_id>')
    def profile(user_id: int):
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'user not found'}), 404
        return render_template('profile.html', user=user)

    @app.route('/bouquet/<int:bouquet_id>')
    def bouquet_detail(bouquet_id: int):
        try:
            # prefer session.get to support newer SQLAlchemy APIs
            bouquet = db.session.get(Bouquet, bouquet_id)
        except Exception:
            bouquet = None
        # find a position for this bouquet if exists (defensive)
        try:
            position = db.session.query(Position).filter_by(bouquet_id=bouquet_id).first()
        except Exception:
            position = None
        if not bouquet:
            return jsonify({'error': 'bouquet not found'}), 404
        return render_template('bouquet.html', bouquet=bouquet, position=position)
