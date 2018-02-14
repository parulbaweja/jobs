from jinja2 import StrictUndefined
from flask_cors import CORS

from flask import (
    Flask,
    render_template,
    redirect,
    request,
    flash,
    session,
    jsonify,
    Blueprint,
    Response
)
from uuid import uuid4
# from flask_debugtoolbar import DebugToolbarExtension

from model import User, AuthId, Company, Contact, Application, Status, DateChange, connect_to_db, db

app = Flask(__name__)
app.secret_key = "abc"
app.jinja_env.undefined = StrictUndefined

bp = Blueprint('server', __name__)

@bp.route('/check_login')
def isLoggedIn():
    """Checks to see if user is logged in."""
    print session
    if session.get('token'):
        result = AuthId.query.filter(AuthId.auth_token == session['token']).order_by(AuthId.auth_id.desc()).first()
        user = User.query.filter(User.user_id == result.user_id).first()
        data = [{
            'firstName': user.fname,
            'loggedIn': 'true',
        }]
    else:
        data = [{
            'loggedIn': 'false',
        }]

    return jsonify(data)


@bp.route('/login', methods=['POST'])
def submit_login_form():
    """Check for unique email and password. If correct, log in."""

    email = request.json.get('email')
    password = request.json.get('password')

    result = User.query.filter((User.email == email) & (User.password == password))

    if result.count() == 0:
        pass
        #return Response('Could not verify your access level for that URL.\nYou have to login with proper credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    else:
        user = result.first()
        new_auth = AuthId(user_id=user.user_id, auth_token=str(uuid4()))
        db.session.add(new_auth)
        db.session.commit()
        session['token'] = new_auth.auth_token
        data = [{'user_id': user.user_id,
                'fname' : user.fname,}]
        return jsonify(data)


@bp.route('/logout')
def logout():
    """Logs out user and drops session."""

    if session.get('token'):
        auth = AuthId.query.filter(AuthId.auth_token == session['token']).order_by(AuthId.auth_id.desc()).first()
        db.session.delete(auth)
        db.session.commit()
    del session['token']
    return jsonify([{'loggedIn': 'false'}])


@bp.route('/register', methods=['POST'])
def submit_register_form():
    """Creates new user. Checks existing in case."""

    email = request.json.get('email')
    password = request.json.get('password')
    fname = request.json.get('fname')
    lname = request.json.get('lname')

    result = User.query.filter((User.email == email) & (User.password == password))

    if result.count() == 0:
        new_user = User(email=email, password=password, fname=fname, lname=lname)
        db.session.add(new_user)
        db.session.commit()
    else:
        pass


@bp.route('/user/app/<user_id>/<application_id>')
def display_user_app(user_id, application_id):
    """Display one application entry for a user."""

    app = Application.query.filter(Application.user_id == user_id, Application.application_id == application_id).first()

    data = [{
        'company': app.company.name,
        'position': app.position,
        'contactName': app.contact.name,
        'contactEmail': app.contact.email,
        'status': app.status.u_name,
        'offerAmount': app.offer_amount,
        'notes': app.notes,
        'url': app.url,
    }]

    return jsonify(data)


@bp.route('/user/<user_id>')
def get_user(user_id):
    pass


@bp.route('/applications')
def display_all_applications():
    """Displays user's application entries."""

    auth = AuthId.query.filter(AuthId.auth_token == session['token']).order_by(AuthId.auth_id.desc()).first()

    apps = Application.query.filter(Application.user_id == auth.user_id).all()
    # date = DateChange.query.filter(DateChange.application_id == app.application_id).first()
    data = []
    for app in apps:
        temp = {}
        temp['userID'] = app.user_id
        temp['applicationID'] = app.application_id
        temp['company'] = app.company.name
        temp['position'] = app.position
        temp['contactName'] = app.contact.name
        temp['contactEmail'] = app.contact.email
        temp['status'] = app.status.u_name
        temp['offerAmount'] = app.offer_amount
        temp['notes'] = app.notes
        temp['url'] = app.url
        data.append(temp)

    return jsonify(data)


@bp.route('/status')
def send_statuses():
    """Sends JSON of current elements in status table."""

    statuses = Status.query.all()
    data = []

    for i, status in enumerate(statuses):
        temp = {}
        temp[status.js_name] = status.u_name
        data.append(temp)

    return jsonify(data)


@bp.route('/application/<user_id>', methods=['POST'])
def submit_entry(user_id):
    """Processes user's new entry."""

    company = request.json.get('company')
    position = request.json.get('position')
    contactName = request.json.get('contactName')
    contactEmail = request.json.get('contactEmail')
    status = request.json.get('status')
    offerAmount = request.json.get('offerAmount')
    notes = request.json.get('notes')
    url = request.json.get('url')

    new_comp = Company(name=company)
    new_contact = Contact(name=contactName, email=contactEmail)
    db.session.add(new_comp)
    db.session.add(new_contact)

    new_status = Status.query.filter(Status.js_name == status).first()

    new_app = Application(user_id=user_id, company_id=new_comp.company_id, contact_id=new_contact.contact_id, position=position, status_id=new_status.status_id, offer_amount=offerAmount, notes=notes, url=url)
    db.session.add(new_app)
    db.session.commit()

    return jsonify({})


if __name__ == "__main__":
    # app = Flask(__name__)
    # app.secret_key = "abc"
    # app.jinja_env.undefined = StrictUndefined
    app.debug = True

    app.register_blueprint(bp)

    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    # app.debug = True
    # make sure templates, etc. are not cached in debug mode
    # app.jinja_env.auto_reload = app.debug
    CORS(app, supports_credentials=True)

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5001, host='0.0.0.0')
