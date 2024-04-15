import wikipedia

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.login_form import LoginForm
from data.users import User
from data.register import RegisterForm
from data.make_req import Reqest

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    Создаём сессию в базе
    """
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Логинимся
    """
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/", methods=['GET', 'POST'])
def index():
    """
    Сама, собственно, база
    """
    form = Reqest()
    if form.validate_on_submit():
        return redirect(url_for(".give_info", request=form.req.data))
    return render_template("index.html", form=form)


@app.route("/give_info/<request>", methods=['GET', 'POST'])
def give_info(request):
    """
    Получаем информацию с Википедии и постим её
    """
    wikipedia.set_lang('ru')
    info = wikipedia.summary(request)
    return render_template("give_info.html", text=info)


@app.route('/logout')
@login_required
def logout():
    """
    Выходим из учётной записи
    """
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    """
    Регистрация
    """
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пользователь уже существует")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            email=form.email.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def log_in():
    db_session.global_init("db/Users.sqlite3")

    app.run()


if __name__ == '__main__':
    log_in()
