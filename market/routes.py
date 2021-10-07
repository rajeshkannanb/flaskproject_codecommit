from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    sell_item_form = SellItemForm()
    """items = [
        {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
        {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
        {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
    ]"""
    if request.method == "POST":
        #if purchase_form.validate_on_submit():
        purchased_item = request.form.get('purchased_item')
        purchased_item_object = Item.query.filter_by(name=purchased_item).first()
        if purchased_item_object:
            if current_user.can_purchase(purchased_item_object):
                purchased_item_object.buy(current_user)
                flash(f"Congrats! you have purchased {purchased_item_object.name} for {purchased_item_object.price}$", category="success")
            else:
                flash(f"Unfortunately you don't have enough budget to buy {purchased_item_object.name}", category="danger")
        #if sell_item_form.validate_on_submit():
        sold_item = request.form.get('sold_item')
        sold_item_object = Item.query.filter_by(name=sold_item).first()
        if sold_item_object:
            if current_user.can_sell(sold_item_object):
                sold_item_object.sell(current_user)
                flash(f"Congrats! you have Sold {sold_item_object.name} costs {sold_item_object.price}$",
                      category="success")
            else:
                flash(f"Sorry!! you have not owned the item {sold_item_object.name}",
                      category="danger")
        return redirect(url_for('market_page'))
    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', item_list=items, purchase_form=purchase_form, owned_items=owned_items, sell_item_form=sell_item_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('market_page'))
    if form.errors == {}:
        pass
    else:
        for error_msg in form.errors.values():
            flash(f'{error_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/login',methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'You have successfully logged in as : {attempted_user.username}', category="success")
            return redirect(url_for('market_page'))
        else:
            flash(f'Username and password do not match!, please try again!', category="danger")

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    logout_user()
    flash(f'You have been successfully logged out!!', category='info')
    return redirect(url_for("home_page"))