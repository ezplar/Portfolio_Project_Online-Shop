from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm,LoginForm
import os
import stripe

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
# key = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

stripe.api_key = 'sk_test_51OQ8TUA1A3kZI9ozsW5CRBXHjDsjEN8x18SiQxIhUy3L0nCwNvv5CgixRWWker3FyvXQT9sVnmayGNEjwNsR3TRZ00uedHrQIf'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

domain_url = 'http://127.0.0.1:5010'

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class User(db.Model, UserMixin):
    # __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    price = db.Column(db.String(250), nullable=False)
    quantity_stock = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

with app.app_context():
    db.create_all()


@app.route('/',methods=['GET','POST'])
def main():
    result = db.session.execute(db.select(Items))
    items = result.scalars().all()
    return render_template('index.html',ds_items = items, current_user=current_user)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif password != user.password:
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('main'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=form.password.data,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('main'))
    return render_template('register.html', form=form, current_user=current_user)

@app.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route('/create-checkout-session/<int:id>', methods=['GET','POST'])
def create_checkout_session(id):
    requested_post = db.get_or_404(Items, id)
    print(requested_post.price)
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price_data': {
                        'currency': "usd",
                        'unit_amount': f'{requested_post.price}00',
                        'product_data': {
                          'name': requested_post.item_name,
                        },
                      },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain_url + '/success',
            cancel_url=domain_url + '/cancel',
        )
        print(checkout_session.id)
        print(domain_url + '/cancel.html')
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

@app.route('/success')
def success():
    return render_template('success.html')



if __name__ == '__main__':
    app.run(debug=True,port=5010)

# Reference
# Todo-List
# Cafe and Wifi Website
# day-71 blog deployment

#For improvements and updates
# Hash password of users
# Add items to cart function
# Add items to Items database
