"""Main application routes."""
from flask import jsonify, render_template, session
from flask import Response
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
        from models import Flower as _Flower, Wrapping as _Wrapping, BouquetType as _Type, Bouquet as _Bouquet
        # expose lists for filter selects
        try:
            flowers = db.session.query(_Flower).all()
            wrappings = db.session.query(_Wrapping).all()
            types = db.session.query(_Type).all()
        except Exception:
            flowers = wrappings = types = []

        # base query
        q = db.session.query(Position).join(Position.bouquet).join(_Bouquet.flower).join(_Bouquet.wrapping).join(_Bouquet.type)

        # apply filters from query params
        search = request.args.get('q')
        if search:
            like = f"%{search}%"
            q = q.filter(_Bouquet.name.ilike(like))

        try:
            flower_id = int(request.args.get('flower_id')) if request.args.get('flower_id') else None
        except Exception:
            flower_id = None
        if flower_id:
            q = q.filter(_Bouquet.flower_id == flower_id)

        try:
            wrapping_id = int(request.args.get('wrapping_id')) if request.args.get('wrapping_id') else None
        except Exception:
            wrapping_id = None
        if wrapping_id:
            q = q.filter(_Bouquet.wrapping_id == wrapping_id)

        try:
            type_id = int(request.args.get('type_id')) if request.args.get('type_id') else None
        except Exception:
            type_id = None
        if type_id:
            q = q.filter(_Bouquet.type_id == type_id)

        try:
            min_price = float(request.args.get('min_price')) if request.args.get('min_price') else None
        except Exception:
            min_price = None
        if min_price is not None:
            q = q.filter(Position.price >= min_price)

        try:
            max_price = float(request.args.get('max_price')) if request.args.get('max_price') else None
        except Exception:
            max_price = None
        if max_price is not None:
            q = q.filter(Position.price <= max_price)

        if request.args.get('in_stock'):
            q = q.filter((Position.quantity != None) & (Position.quantity > 0))

        positions = q.all()
        user_id = session.get('user_id')
        try:
            is_admin_user = _is_admin(user_id) if user_id else False
        except Exception:
            is_admin_user = False
        return render_template('shop.html', positions=positions, is_admin=is_admin_user, flowers=flowers, wrappings=wrappings, types=types)

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
        # load user's orders explicitly to pass into template
        try:
            from models import Order as _Order
            orders = db.session.query(_Order).filter_by(user_id=user_id).all()
        except Exception:
            orders = []
        # also load subscriptions and notifications for convenience
        try:
            from services.subscription_service import SubscriptionService
            from services.notification_service import NotificationService
            subsvc = SubscriptionService(db.session)
            notsvc = NotificationService(db.session)
            subscriptions = subsvc.list_for_user(user_id)
            notifications = notsvc.list_for_user(user_id)
        except Exception:
            subscriptions = []
            notifications = []
        return render_template('profile.html', user=user, orders=orders, subscriptions=subscriptions, notifications=notifications)

    @app.route('/subscribe/<int:bouquet_id>', methods=['POST'])
    def subscribe_bouquet(bouquet_id: int):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        from services.subscription_service import SubscriptionService
        svc = SubscriptionService(db.session)
        try:
            svc.subscribe(user_id=user_id, bouquet_id=bouquet_id)
        except Exception:
            pass
        return redirect(url_for('bouquet_detail', bouquet_id=bouquet_id))

    @app.route('/unsubscribe/<int:bouquet_id>', methods=['POST'])
    def unsubscribe_bouquet(bouquet_id: int):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        from services.subscription_service import SubscriptionService
        svc = SubscriptionService(db.session)
        try:
            svc.unsubscribe(user_id=user_id, bouquet_id=bouquet_id)
        except Exception:
            pass
        return redirect(url_for('bouquet_detail', bouquet_id=bouquet_id))

    @app.route('/events/notifications')
    def events_notifications():
        # SSE endpoint — require login
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'unauthenticated'}), 401
        try:
            from services.realtime import broadcaster
        except Exception:
            return jsonify({'error': 'realtime unavailable'}), 500

        def event_stream():
            for item in broadcaster.listen(user_id):
                if item is None:
                    # keep-alive comment
                    yield ': keep-alive\n\n'
                    continue
                # send as a data event
                yield f'data: {item}\n\n'

        return Response(event_stream(), mimetype='text/event-stream')

    # Debug helpers (not for production)
    @app.route('/debug/notifications/<int:user_id>')
    def debug_notifications(user_id: int):
        from services.notification_service import NotificationService
        svc = NotificationService(db.session)
        items = svc.list_for_user(user_id)
        return jsonify([i.to_dict() for i in items])

    @app.route('/debug/all_notifications')
    def debug_all_notifications():
        from services.notification_service import NotificationService
        svc = NotificationService(db.session)
        # attempt to list all notifications via DAO if available
        try:
            items = svc.dao.list_all()
            return jsonify([{
                'id': i.id, 'user_id': i.user_id, 'bouquet_id': i.bouquet_id,
                'message': i.message, 'read': i.read, 'created_at': i.created_at.isoformat()
            } for i in items])
        except Exception:
            # fallback: try listing per-user for known users (best-effort)
            return jsonify([])

    @app.route('/debug/subscriptions/<int:bouquet_id>')
    def debug_subscriptions(bouquet_id: int):
        from services.subscription_service import SubscriptionService
        svc = SubscriptionService(db.session)
        items = svc.list_for_bouquet(bouquet_id)
        return jsonify([{'id': i.id, 'user_id': i.user_id, 'bouquet_id': i.bouquet_id} for i in items])

    @app.route('/debug/create_notification', methods=['POST'])
    def debug_create_notification():
        """Create a simple notification for a user (body: user_id, bouquet_id, message)."""
        data = request.form or request.json or {}
        try:
            uid = int(data.get('user_id'))
        except Exception:
            return jsonify({'error': 'user_id required'}), 400
        bid = data.get('bouquet_id')
        try:
            bid = int(bid) if bid is not None else None
        except Exception:
            bid = None
        msg = data.get('message') or f'Test notification for user {uid}'
        try:
            from services.notification_service import NotificationService
            svc = NotificationService(db.session)
            n = svc.create(user_id=uid, bouquet_id=bid, message=msg)
            # publish realtime
            try:
                from services.realtime import broadcaster
                broadcaster.publish(uid, msg)
            except Exception:
                pass
            return jsonify({'ok': True, 'id': n.id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/debug/generate_notifications_for_subscriptions', methods=['POST'])
    def debug_generate_notifications_for_subscriptions():
        """Generate a notification for every subscription to test persistence and publish."""
        try:
            from services.subscription_service import SubscriptionService
            from services.notification_service import NotificationService
            sub_svc = SubscriptionService(db.session)
            notif_svc = NotificationService(db.session)
            subs = db.session.query(__import__('models').models.Subscription).all()
        except Exception:
            subs = []
        created = 0
        for s in subs:
            try:
                msg = f"Test: bouquet {s.bouquet_id} update"
                notif_svc.create(user_id=s.user_id, bouquet_id=s.bouquet_id, message=msg)
                try:
                    from services.realtime import broadcaster
                    broadcaster.publish(s.user_id, msg)
                except Exception:
                    pass
                created += 1
            except Exception:
                pass
        return jsonify({'created': created})

    @app.route('/debug/trigger_stock/<int:position_id>', methods=['POST'])
    def debug_trigger_stock(position_id: int):
        # set quantity to 5 for position and trigger notify
        from services.position_service import PositionService
        psvc = PositionService(db.session)
        from models import Position as _Position
        psvc.dao.model = _Position
        # force set quantity
        psvc.set_quantity(position_id, 5)
        return jsonify({'ok': True})

    # Cart operations (session-based)
    def _get_cart():
        return session.setdefault('cart', [])

    @app.route('/cart')
    def cart_view():
        cart = _get_cart()
        # compute total and, if user has a non-standard card, include discounted prices
        user_id = session.get('user_id')
        card_name = 'standard'
        try:
            from models import User as _User
            if user_id:
                u = db.session.get(_User, user_id)
                card_name = getattr(u, 'card', 'standard') or 'standard'
        except Exception:
            card_name = 'standard'

        from services.card_service import CardService
        strategy = CardService.get_strategy(card_name)

        total = 0.0
        # annotate cart items with discounted price when applicable
        for item in cart:
            qty = item.get('quantity', 1)
            orig = float(item.get('price', 0.0))
            discounted_unit = orig * strategy.price_factor(orig)
            item['discounted_price'] = round(discounted_unit, 2)
            item['original_price'] = round(orig, 2)
            item['line_total'] = round(discounted_unit * qty, 2)
            total += discounted_unit * qty

        # load delivery options and compute delivery cost using card strategy
        try:
            from models import Delivery as _Delivery
            deliveries = db.session.query(_Delivery).all()
        except Exception:
            deliveries = []

        # determine selected delivery id from query (or default to first)
        selected_delivery_id = request.args.get('delivery_id')
        if not selected_delivery_id and deliveries:
            selected_delivery_id = str(deliveries[0].id)

        delivery_cost = 0.0
        try:
            if selected_delivery_id:
                d = db.session.get(_Delivery, int(selected_delivery_id))
                if d is not None:
                    delivery_cost = float(d.price) * strategy.delivery_factor(float(d.price))
        except Exception:
            delivery_cost = 0.0

        grand_total = total + delivery_cost

        return render_template('cart.html', cart=cart, total=total, card_name=card_name, deliveries=deliveries, selected_delivery_id=selected_delivery_id, delivery_cost=round(delivery_cost,2), grand_total=round(grand_total,2))

    @app.route('/cart/add/<int:position_id>', methods=['POST'])
    def cart_add(position_id: int):
        # find position
        pos = db.session.get(Position, position_id)
        if not pos or (pos.quantity or 0) <= 0:
            return redirect(url_for('shop'))
        # requested quantity
        try:
            req_q = int(request.form.get('quantity', 1))
        except Exception:
            req_q = 1
        qty = max(1, min(req_q, pos.quantity))
        cart = _get_cart()
        # find existing item
        for it in cart:
            if it['position_id'] == position_id:
                it['quantity'] = min(it.get('quantity', 1) + qty, pos.quantity)
                break
        else:
            cart.append({'position_id': position_id, 'bouquet_name': pos.bouquet.name, 'price': float(pos.price), 'quantity': qty})
        session['cart'] = cart
        return redirect(url_for('cart_view'))

    @app.route('/cart/remove/<int:position_id>', methods=['POST'])
    def cart_remove(position_id: int):
        cart = _get_cart()
        remove_all = request.form.get('remove_all', '0') in ('1', 'true', 'yes')
        for it in list(cart):
            if it['position_id'] == position_id:
                if remove_all or it.get('quantity', 1) <= 1:
                    cart.remove(it)
                else:
                    # optional qty param to remove specific amount
                    try:
                        dec = int(request.form.get('quantity', 1))
                    except Exception:
                        dec = 1
                    it['quantity'] = max(0, it.get('quantity', 1) - dec)
                    if it['quantity'] == 0:
                        cart.remove(it)
                break
        session['cart'] = cart
        return redirect(url_for('cart_view'))

    @app.route('/cart/update/<int:position_id>', methods=['POST'])
    def cart_update(position_id: int):
        cart = _get_cart()
        try:
            new_q = int(request.form.get('quantity', 0))
        except Exception:
            new_q = 0
        # clamp to stock
        pos = db.session.get(Position, position_id)
        if pos and new_q > (pos.quantity or 0):
            new_q = pos.quantity or 0
        for it in cart:
            if it['position_id'] == position_id:
                if new_q <= 0:
                    cart.remove(it)
                else:
                    it['quantity'] = new_q
                break
        session['cart'] = cart
        return redirect(url_for('cart_view'))

    @app.route('/cart/checkout', methods=['POST'])
    def cart_checkout():
        # require login
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        cart = _get_cart()
        # basic implementation: create one order per cart item using first delivery (if any)
        delivery = db.session.query(db.session.get.__self__.__class__).filter_by().first() if False else None
        from services.order_service import OrderService
        order_svc = OrderService(db.session)
        created_orders = []
        # pick a delivery if exists else None
        delivery_obj = db.session.query(db.session.get.__self__.__class__).filter_by().first() if False else None
        # fallback: try to get first Delivery model instance
        try:
            from models import Delivery as _DeliveryModel
            delivery_obj = db.session.query(_DeliveryModel).first()
        except Exception:
            delivery_obj = None

        # determine user's card
        try:
            from models import User as _User
            u = db.session.get(_User, user_id)
            card_name = getattr(u, 'card', 'standard') or 'standard'
        except Exception:
            card_name = 'standard'

        # read delivery_id from form (user may choose during checkout)
        try:
            chosen_delivery = int(request.form.get('delivery_id')) if request.form.get('delivery_id') else None
        except Exception:
            chosen_delivery = None

        for it in list(cart):
            pos_id = it['position_id']
            qty = it.get('quantity', 1)
            delivery_id = delivery_obj.id if delivery_obj else None
            # prefer chosen delivery for this checkout
            order_delivery_id = chosen_delivery if chosen_delivery is not None else (delivery_obj.id if delivery_obj else None)
            order = order_svc.create(user_id=user_id, position_id=pos_id, delivery_id=order_delivery_id, quantity=qty, user_card_name=card_name)
            if order:
                created_orders.append(order.id)
        # clear cart and redirect user to their profile page
        session['cart'] = []
        if created_orders:
            return redirect(url_for('profile', user_id=user_id))
        # if nothing created, return JSON to indicate no orders
        return jsonify({'orders_created': created_orders})

    # Create custom bouquet (for logged-in users)
    @app.route('/create_bouquet', methods=['GET', 'POST'])
    def create_bouquet():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        # provide flower/wrapping/type lists
        flowers = db.session.query(db.session.get.__self__.__class__).filter_by().first() if False else None
        try:
            from models import Flower as _Flower, Wrapping as _Wrapping, BouquetType as _Type
            flowers = db.session.query(_Flower).all()
            wrappings = db.session.query(_Wrapping).all()
            types = db.session.query(_Type).all()
        except Exception:
            flowers = wrappings = types = []

        is_admin_user = _is_admin(user_id)
        if request.method == 'GET':
            return render_template('create_bouquet.html', flowers=flowers, wrappings=wrappings, types=types, is_admin=is_admin_user)

        # POST: create bouquet and optional position
        name = request.form.get('name')
        flower_id = int(request.form.get('flower_id'))
        wrapping_id = int(request.form.get('wrapping_id'))
        type_id = int(request.form.get('type_id'))
        flowers_count = int(request.form.get('flowers_count', 1))
        price_raw = request.form.get('price')
        quantity = int(request.form.get('quantity', 0))

        from services.bouquet_service import BouquetService
        from services.position_service import PositionService
        bsvc = BouquetService(db.session)
        psvc = PositionService(db.session)

        from builders.general_bouquet import GeneralBouquet
        builder = GeneralBouquet().set_name(name).set_flower(flower_id).set_wrapping(wrapping_id).set_type(type_id).set_flowers_count(flowers_count)
        try:
            bouquet = bsvc.create_from_builder(builder)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        # Admins may set explicit price; regular users cannot set price and their created position
        # will use computed price and be automatically added to their cart.
        price = None
        if is_admin_user and price_raw:
            try:
                price = float(price_raw)
            except Exception:
                price = None

        # create position if quantity requested
        if quantity > 0:
            from models import Position as _PositionModel
            psvc.dao.model = _PositionModel
            # if no explicit price, compute from bouquet
            if price is None:
                price = psvc.compute_price_from_bouquet(bouquet)
            created_pos = psvc.create_from_bouquet(bouquet, price=price, quantity=quantity)
            # if user is not admin, add created position to user's cart immediately
            if not is_admin_user and created_pos is not None:
                cart = session.setdefault('cart', [])
                cart.append({'position_id': created_pos.id, 'bouquet_name': bouquet.name, 'price': float(created_pos.price), 'quantity': quantity})
                session['cart'] = cart
                return redirect(url_for('cart_view'))

        # for admins or when no immediate cart addition, redirect to shop
        return redirect(url_for('shop'))

    # admin helper
    def _is_admin(user_id: int) -> bool:
        try:
            user = db.session.get(User, user_id)
            return user and getattr(user.user_type, 'is_admin', False)
        except Exception:
            return False

    @app.route('/admin/bouquets')
    def admin_bouquets():
        user_id = session.get('user_id')
        if not user_id or not _is_admin(user_id):
            return jsonify({'error': 'forbidden'}), 403
        from models import Bouquet as _Bouquet
        bouquets = db.session.query(_Bouquet).all()
        return render_template('admin_bouquets.html', bouquets=bouquets)

    @app.route('/admin/bouquets/edit/<int:bouquet_id>', methods=['GET', 'POST'])
    def admin_edit_bouquet(bouquet_id: int):
        user_id = session.get('user_id')
        if not user_id or not _is_admin(user_id):
            return jsonify({'error': 'forbidden'}), 403
        from models import Bouquet as _Bouquet, Position as _Position
        bouquet = db.session.get(_Bouquet, bouquet_id)
        if not bouquet:
            return jsonify({'error': 'not found'}), 404
        positions = db.session.query(_Position).filter_by(bouquet_id=bouquet_id).all()
        if request.method == 'GET':
            return render_template('admin_edit_bouquet.html', bouquet=bouquet, positions=positions)
        # POST: update name
        name = request.form.get('name')
        from services.bouquet_service import BouquetService
        bsvc = BouquetService(db.session)
        bsvc.update(bouquet_id, name=name)
        return redirect(url_for('admin_bouquets'))

    @app.route('/admin/bouquets/delete/<int:bouquet_id>', methods=['POST'])
    def admin_delete_bouquet(bouquet_id: int):
        user_id = session.get('user_id')
        if not user_id or not _is_admin(user_id):
            return jsonify({'error': 'forbidden'}), 403
        from services.bouquet_service import BouquetService
        bsvc = BouquetService(db.session)
        try:
            bsvc.delete(bouquet_id)
        except Exception as e:
            # return a simple error JSON for now
            return jsonify({'error': str(e)}), 400
        return redirect(url_for('admin_bouquets'))

    @app.route('/admin/positions/update/<int:position_id>', methods=['POST'])
    def admin_update_position(position_id: int):
        user_id = session.get('user_id')
        if not user_id or not _is_admin(user_id):
            return jsonify({'error': 'forbidden'}), 403
        try:
            new_q = int(request.form.get('quantity', 0))
        except Exception:
            new_q = 0
        from services.position_service import PositionService
        psvc = PositionService(db.session)
        from models import Position as _Position
        psvc.dao.model = _Position
        psvc.set_quantity(position_id, new_q)
        return redirect(url_for('admin_edit_bouquet', bouquet_id=db.session.get(_Position, position_id).bouquet_id))

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
        # detect admin for current session
        user_id = session.get('user_id')
        try:
            is_admin_user = _is_admin(user_id) if user_id else False
        except Exception:
            is_admin_user = False
        return render_template('bouquet.html', bouquet=bouquet, position=position, is_admin=is_admin_user)

    @app.route('/profile/orders/cancel/<int:order_id>', methods=['POST'])
    def profile_cancel_order(order_id: int):
        # require login
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        # fetch order and check ownership
        from models import Order as _Order
        order = db.session.get(_Order, order_id)
        if not order:
            return jsonify({'error': 'order not found'}), 404
        # allow owner or admin
        if order.user_id != user_id and not _is_admin(user_id):
            return jsonify({'error': 'forbidden'}), 403
        # perform deletion via service (restores position stock)
        from services.order_service import OrderService
        svc = OrderService(db.session)
        try:
            svc.delete(order_id)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        return redirect(url_for('profile', user_id=user_id))
