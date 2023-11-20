from flask import Flask,g,url_for,request,jsonify
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required,current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import sqlite3
from collections import OrderedDict
from flask_mail import Mail,Message

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SECRET_KEY'] = '3e7b5ec2a82b029ad8500095'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()
admin = Admin(app,template_mode='bootstrap3')
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'


app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'ChienNV.B20VT063@stu.ptit.edu.vn'
app.config['MAIL_PASSWORD'] = 'C11122002'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


 # ket noi Database
def connect_db():
    sql = sqlite3.connect('instance\music.db')
    sql.row_factory = sqlite3.Row #tra ve dictionary thay vi tuple
    return sql 

def get_db():
    if not hasattr(g,'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer(),primary_key = True)
    username = db.Column(db.String(length=30),nullable = False,unique = True)
    email_address = db.Column(db.String(length=50),nullable = False,unique = True)
    password_hash = db.Column(db.String(length=50),nullable = False)
    is_admin = db.Column(db.Boolean,default = False)
    def __repr__(self) -> str:
        return f'<User> {self.username}'

    def get_token(self,expires_sec=300):
        serial = Serializer(app.config['SECRET_KEY'])
        return serial.dumps({'user_id':self.id})
    
    @staticmethod
    def verify_token(token):
        serial = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    @property
    def password(self):
        return self.password_hash
    @password.setter
    def password(self,plan_text_passeword):
        self.password_hash = bcrypt.generate_password_hash(plan_text_passeword,10).decode('utf-8')

    def check_password_correction(self, attempted_password):
        if bcrypt.check_password_hash(self.password_hash, attempted_password):
            return True
        return False

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng Song
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.Date,nullable=False)
    listen = db.Column(db.Integer, default = 0)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    genre = db.relationship('Genre')
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    region = db.relationship('Region')
    def __str__(self):
        return self.title

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng Region
class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng DSYT (Danh sách yêu thích)
class Favorites(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') , primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)
    user = db.relationship('User')
    song = db.relationship('Song')

class Performence(db.Model):
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id') , primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)
    # Thêm quan hệ many-to-one với bảng Artist
    artist = db.relationship('Artist',backref = 'song')
    # Thêm quan hệ many-to-one với bảng Song
    song = db.relationship('Song',backref = 'artist')


class Admin_Controll(ModelView):
    # def is_accessible(self):
    #     if current_user.is_authenticated and current_user.is_admin:
    #         return True
    #     else:
    #         return abort(404)
    pass

class UserView(Admin_Controll):
    def on_model_change(self, form, model, is_created):
        model.password_hash = bcrypt.generate_password_hash(model.password_hash)
class SongView(Admin_Controll):
    edit_modal = True
    create_modal = True
    details_modal = True
    column_list = ['id','title', 'genre', 'region', 'listen', 'release_date','link']
    pass
class GenreView(Admin_Controll):
    edit_modal = True
    create_modal = True
    details_modal = True
    pass
class RegionView(Admin_Controll):
    edit_modal = True
    create_modal = True
    details_modal = True
    pass
class FavoritesView(Admin_Controll):
    edit_modal = True
    create_modal = True
    details_modal = True
    pass
class PerformenceView(Admin_Controll):
    edit_modal = True
    create_modal = True
    details_modal = True
    # column_list = [
    #     'artist_id',
    #     'song_id'
    # ]
    # form_choices = {
    #     "artist" : [("id",Artist.query.all())],
    #     "song" : [("id",Song.query.all())]
    # }

class ArtistView(ModelView):
    edit_modal = True
    create_modal = True
    details_modal = True
    column_list = ['id','name']

admin.add_view(UserView(User,db.session))
admin.add_view(SongView(Song,db.session))
admin.add_view(ArtistView(Artist, db.session))
admin.add_view(GenreView(Genre,db.session))
admin.add_view(RegionView(Region,db.session))
admin.add_view(FavoritesView(Favorites,db.session))
admin.add_view(PerformenceView(Performence,db.session))


@app.route('/register',methods = ['POST'])
def register():
    data = request.get_json()
    check = True
    username = data.get('username')
    if User.query.filter_by(username = username).first() :
        check = False
        return jsonify({'message':'username already exists'})
    email_address = data.get('email')
    if User.query.filter_by(email_address = email_address).first():
        check = False
        return jsonify({'message':'email already exists'})      
    password = data.get('password')
    password_confirm = data.get('password_confirm')
    if password != password_confirm:
        check = False
        return jsonify({'message':'Password_confim is not correct'})
    if check:
        user_to_create = User(username = username,email_address = email_address,
                        password = password)
        db.session.add(user_to_create)
        db.session.commit()
        return jsonify({'message':'Create successfully!'})

@app.route('/login',methods = ['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    attempted_user = User.query.filter_by(username=username).first()
    if attempted_user and attempted_user.check_password_correction(attempted_password=password):
        login_user(attempted_user)
        if attempted_user.username == 'admin':
            return jsonify({'message': 'Success!', 'username': attempted_user.username, 'isAdmin': True, 'redirect': '/admin'})
        return jsonify({'message': f'Success! You just logged in as {attempted_user.username}', 'isAdmin': False, 'redirect': '/getallsong'})
    else:
        return jsonify({'message': 'Username and password are not match! Please try again', 'isAdmin': False}), 401
@app.route('/logout',methods = ['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Success! You just loged out','redirect': '/login'})

@app.route('/changepassword',methods = ['POST'])
@login_required
def changepassword():
    user_id = current_user.get_id()
    data = request.get_json()
    old_password = data.get('old_password')
    user = User.query.filter_by(id = user_id).first()
    if user.check_password_correction(attempted_password =  old_password):
        new_password = data.get('new_password')
        password_confirm =data.get('password_confirm')
        if new_password == password_confirm:
            user.password = new_password
            db.session.commit()
            return jsonify({'message':'Password is updated'})
        else:
            return jsonify({'message':'Password confirm is not correct'})
    else:
        return jsonify({'message':'Password is wrong'})


#email
def send_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request',recipients=[user.email_address],sender='ChienNV.B20VT063@stu.ptit.edu.vn')
    msg.body = f''' to reset your password. Please follow the link below

    {url_for('reset_token',token = token,_external = True)}

    If you didn't send a password reset request. Please ignore this message.

 '''
    mail.send(msg)
@app.route('/reset_password',methods = ['POST'])
def reset_request():
    data = request.get_json()
    user = User.query.filter_by(email_address = data.get('email')).first()
    if user:
        send_mail(user)
        return jsonify({'message': 'Success! Check your email', 'redirect': '/login'})

    else:
        return jsonify({'message':'Email is not exist', 'redirect': '/reset_password'})



@app.route('/reset_password/<token>',methods = ['GET','POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        return jsonify({'message':'Invalid token or time out', 'redirect': '/reset_password'})
    data = request.get_json()
    password = data.get('password')
    password_confirm = data.get('password_confirm')
    if password != password_confirm:
        return jsonify({'message':'Password confirm is not correct'})
    else:   
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password_hash = hash_password
        db.session.commit()
        return jsonify({'message':'Password is changed'})
'''
#xu li reset_password
@app.route('/reset_password/<token>',methods = ['GET','POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('That is invalid token or expired. Please try again')
        return redirect(url_for('reset_request'))
    if request.method == 'POST':
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        if password != password_confirm:
            flash('Password_confirm is not correct')
        else:   
            hash_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            user.password_hash = hash_password
            db.session.commit()
            flash('Password changed!')
            return redirect(url_for('login'))       
    return render_template('resetpasswordr2.html',token = token)
'''

@app.route('/api/topbaihat/<quocgia>')
def topbaihat(quocgia):
    dbm = get_db()
    cur = dbm.execute(
        '''
        select 
            s.id,
            title,
            s.image,
            link,
            release_date,
            listen,
            r.name as region,
            g.name as genre
        from song as s
        join region as r
            on r.id = s.region_id
        join genre as g
            on g.id = s.genre_id
        where r.name = ?
        order by s.listen desc
        limit 10;

        ''',[quocgia])
    result_song = cur.fetchall()
    result_dict_song = []

    for song in result_song:
        song_dict = {
            'id' : song['id'],
            'title': song['title'],
            'image': song['image'],
            'link': song['link'],
            'release_date':song['release_date'],
            'listen': song['listen'],
            'region': song['region'],
            'genre' : song['genre']
        }
        dbm = get_db()
        cur1 = dbm.execute(
        '''
        select 
            a.id,
            a.name,
            a.image
        from artist as a
        join performence as p
        on a.id = p.artist_id
        join song as s
        on s.id = p.song_id
        where s.id = ?
        ''',[song['id']])
        result_artist = cur1.fetchall()
        result_dict_artist = []
        for artist in result_artist:
            ar_dict = {
                'id':artist['id'],
                'name':artist['name'],
                'image':artist['image']
            }
            result_dict_artist.append(ar_dict)
        song_dict.update({'artist':result_dict_artist})
        result_dict_song.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':result_dict_song}}
    return jsonify(result_return)

@app.route('/api/topbaihatall')
def topbaihatall():
    dbm = get_db()
    cur = dbm.execute(
        '''
        select 
            s.id,
            title,
            s.image,
            link,
            release_date,
            listen,
            r.name as region,
            g.name as genre
        from song as s
        join region as r
            on r.id = s.region_id
        join genre as g
            on g.id = s.genre_id
        order by s.listen desc
        limit 10;

        ''')
    result_song = cur.fetchall()
    result_dict_song = []

    for song in result_song:
        song_dict = {
            'id' : song['id'],
            'title': song['title'],
            'image': song['image'],
            'link': song['link'],
            'release_date':song['release_date'],
            'listen': song['listen'],
            'region': song['region'],
            'genre' : song['genre']
        }
        dbm = get_db()
        cur1 = dbm.execute(
        '''
        select 
            a.id,
            a.name,
            a.image
        from artist as a
        join performence as p
        on a.id = p.artist_id
        join song as s
        on s.id = p.song_id
        where s.id = ?
        ''',[song['id']])
        result_artist = cur1.fetchall()
        result_dict_artist = []
        for artist in result_artist:
            ar_dict = {
                'id':artist['id'],
                'name':artist['name'],
                'image':artist['image']
            }
            result_dict_artist.append(ar_dict)
        song_dict.update({'artist':result_dict_artist})
        result_dict_song.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':result_dict_song}}
    return jsonify(result_return)

@app.route('/api/songs')
def songs():
    dbm = get_db()
    cur = dbm.execute(
        '''
        select 
            s.id,
            title,
            s.image,
            link,
            release_date,
            listen,
            r.name as region,
            g.name as genre
        from song as s
        join region as r
            on r.id = s.region_id
        join genre as g
            on g.id = s.genre_id
        ''')
    result_song = cur.fetchall()
    result_dict_song = []

    for song in result_song:
        song_dict = {
            'id' : song['id'],
            'title': song['title'],
            'image': song['image'],
            'link': song['link'],
            'release_date':song['release_date'],
            'listen': song['listen'],
            'region': song['region'],
            'genre' : song['genre']
        }
        dbm = get_db()
        cur1 = dbm.execute(
        '''
        select 
            a.id,
            a.name,
            a.image
        from artist as a
        join performence as p
        on a.id = p.artist_id
        join song as s
        on s.id = p.song_id
        where s.id = ?
        ''',[song['id']])
        result_artist = cur1.fetchall()
        result_dict_artist = []
        for artist in result_artist:
            ar_dict = {
                'id':artist['id'],
                'name':artist['name'],
                'image':artist['image']
            }
            result_dict_artist.append(ar_dict)
        song_dict.update({'artist':result_dict_artist})
        result_dict_song.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':result_dict_song}}
    return jsonify(result_return)

@app.route('/api/song/<int:song_id>')
def song(song_id):
    song = db.session.query(Song).get(song_id)
    song.listen = song.listen + 1
    db.session.commit()
    song_dict = {
        'id' : song.id,
        'title': song.title,
        'image': song.image,
        'link': song.link,
        'release_date':song.release_date,
        'listen': song.listen,
        'region': song.region.name,
    }
    query =db.session.query(Artist).join(Performence).join(Song).filter(Song.id == song_id)
    artists = query.all()
    result_dict_artist = []
    for artist in artists:
        ar_dict = {
            'id' : artist.id,
            'name': artist.name,
            'image':artist.image
        }
        result_dict_artist.append(ar_dict)
    song_dict.update({'artist':result_dict_artist})
    result_return = {'err':0,'msg':'Success','data': {'song':song_dict}}
    return jsonify(result_return)


@app.route('/api/favoritesongs')
@login_required
def favorite_songs():
    user_id = current_user.get_id()

    favorites = Favorites.query.filter_by(user_id=user_id).all()

    favorite_songs_list = []

    for favorite in favorites:
        song = favorite.song

        song_dict = {
            'id': song.id,
            'title': song.title,
            'image': song.image,
            'link': song.link,
            'release_date': song.release_date,
            'listen': song.listen,
            'region': song.region.name,
        }

        query = db.session.query(Artist).join(Performence).join(Song).filter(Song.id == song.id)
        artists = query.all()
        result_dict_artist = []

        for artist in artists:
            ar_dict = {
                'id': artist.id,
                'name': artist.name,
                'image': artist.image,
            }
            result_dict_artist.append(ar_dict)

        song_dict.update({'artists': result_dict_artist})
        favorite_songs_list.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':favorite_songs_list}}
    return jsonify(result_return)

@app.route("/api/addtoplaylist",methods = ['POST'])
@login_required
def add_to_playlist():
    data = request.get_json()
    song_id = data.get('song_id')
    user_id = current_user.get_id()
    existing_entry = Favorites.query.filter_by(user_id=user_id, song_id=song_id).first()
    if existing_entry:
        return jsonify({'message':"Song is already in your playlist."}) 
    else:
        usersong = Favorites(user_id=user_id,song_id=song_id)
        db.session.add(usersong)
        db.session.commit()
        return jsonify({'message':"Added to playlist successfully."}) 

@app.route("/api/removefromplaylist", methods=['POST'])
@login_required
def remove_from_playlist():
    data = request.get_json()
    song_id = data.get('song_id')
    user_id = current_user.get_id()
    existing_entry = Favorites.query.filter_by(user_id=user_id, song_id=song_id).first()
    
    if existing_entry:
        db.session.delete(existing_entry)
        db.session.commit()
        return jsonify({'message': "Removed from playlist successfully."})
    else:
        return jsonify({'message': "Song is not in your playlist."})

@app.route('/api/moiphathanh')
def moiphathanh():
    dbm = get_db()
    cur = dbm.execute(
        '''
        select 
            s.id,
            title,
            s.image,
            link,
            release_date,
            listen,
            r.name as region,
            g.name as genre
        from song as s
        join region as r
            on r.id = s.region_id
        join genre as g
            on g.id = s.genre_id
        order by s.release_date desc
        limit 10
        ''')
    result_song = cur.fetchall()
    result_dict_song = []

    for song in result_song:
        song_dict = {
            'id' : song['id'],
            'title': song['title'],
            'image': song['image'],
            'link': song['link'],
            'release_date':song['release_date'],
            'listen': song['listen'],
            'region': song['region'],
            'genre' : song['genre']
        }
        dbm = get_db()
        cur1 = dbm.execute(
        '''
        select 
            a.id,
            a.name,
            a.image
        from artist as a
        join performence as p
        on a.id = p.artist_id
        join song as s
        on s.id = p.song_id
        where s.id = ?
        ''',[song['id']])
        result_artist = cur1.fetchall()
        result_dict_artist = []
        for artist in result_artist:
            ar_dict = {
                'id':artist['id'],
                'name':artist['name'],
                'image':artist['image']
            }
            result_dict_artist.append(ar_dict)
        song_dict.update({'artist':result_dict_artist})
        result_dict_song.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':result_dict_song}}
    return jsonify(result_return)

@app.route('/api/genre/<theloai>')
def genre(theloai):
    dbm = get_db()
    cur = dbm.execute(
        '''
        select 
            s.id,
            title,
            s.image,
            link,
            release_date,
            listen,
            r.name as region,
            g.name as genre
        from song as s
        join region as r
            on r.id = s.region_id
        join genre as g
            on g.id = s.genre_id
        where g.name = ?
        ''',[theloai])
    result_song = cur.fetchall()
    result_dict_song = []

    for song in result_song:
        song_dict = {
            'id' : song['id'],
            'title': song['title'],
            'image': song['image'],
            'link': song['link'],
            'release_date':song['release_date'],
            'listen': song['listen'],
            'region': song['region'],
            'genre' : song['genre']
        }
        dbm = get_db()
        cur1 = dbm.execute(
        '''
        select 
            a.id,
            a.name,
            a.image
        from artist as a
        join performence as p
        on a.id = p.artist_id
        join song as s
        on s.id = p.song_id
        where s.id = ?
        ''',[song['id']])
        result_artist = cur1.fetchall()
        result_dict_artist = []
        for artist in result_artist:
            ar_dict = {
                'id':artist['id'],
                'name':artist['name'],
                'image':artist['image']
            }
            result_dict_artist.append(ar_dict)
        song_dict.update({'artist':result_dict_artist})
        result_dict_song.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':result_dict_song}}
    return jsonify(result_return)

@app.route('/api/region/<quocgia>')
def region(quocgia):
    dbm = get_db()
    cur = dbm.execute(
        '''
        select 
            s.id,
            title,
            s.image,
            link,
            release_date,
            listen,
            r.name as region,
            g.name as genre
        from song as s
        join region as r
            on r.id = s.region_id
        join genre as g
            on g.id = s.genre_id
        where r.name = ?
        ''',[quocgia])
    result_song = cur.fetchall()
    result_dict_song = []

    for song in result_song:
        song_dict = {
            'id' : song['id'],
            'title': song['title'],
            'image': song['image'],
            'link': song['link'],
            'release_date':song['release_date'],
            'listen': song['listen'],
            'region': song['region'],
            'genre' : song['genre']
        }
        dbm = get_db()
        cur1 = dbm.execute(
        '''
        select 
            a.id,
            a.name,
            a.image
        from artist as a
        join performence as p
        on a.id = p.artist_id
        join song as s
        on s.id = p.song_id
        where s.id = ?
        ''',[song['id']])
        result_artist = cur1.fetchall()
        result_dict_artist = []
        for artist in result_artist:
            ar_dict = {
                'id':artist['id'],
                'name':artist['name'],
                'image':artist['image']
            }
            result_dict_artist.append(ar_dict)
        song_dict.update({'artist':result_dict_artist})
        result_dict_song.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':result_dict_song}}
    return jsonify(result_return)

@app.route('/api/artist/<int:artist_id>')
def artist(artist_id):
    dbm = get_db()
    cur = dbm.execute(
        '''
        select 
            s.id,
            title,
            s.image,
            link,
            release_date,
            listen,
            r.name as region,
            g.name as genre
        from song as s
        join region as r
            on r.id = s.region_id
        join genre as g
            on g.id = s.genre_id
        join performence as p
            on p.song_id = s.id
        join artist as a
            on p.artist_id = a.id
        where a.id = ?
        ''',[artist_id])
    result_song = cur.fetchall()
    result_dict_song = []

    for song in result_song:
        song_dict = {
            'id' : song['id'],
            'title': song['title'],
            'image': song['image'],
            'link': song['link'],
            'release_date':song['release_date'],
            'listen': song['listen'],
            'region': song['region'],
            'genre' : song['genre']
        }
        dbm = get_db()
        cur1 = dbm.execute(
        '''
        select 
            a.id,
            a.name,
            a.image
        from artist as a
        join performence as p
        on a.id = p.artist_id
        join song as s
        on s.id = p.song_id
        where s.id = ?
        ''',[song['id']])
        result_artist = cur1.fetchall()
        result_dict_artist = []
        for artist in result_artist:
            ar_dict = {
                'id':artist['id'],
                'name':artist['name'],
                'image':artist['image']
            }
            result_dict_artist.append(ar_dict)
        song_dict.update({'artist':result_dict_artist})
        result_dict_song.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':result_dict_song}}
    return jsonify(result_return)
@app.route('/api/search')
def search():
    songname = request.args.get('q')
    dbm = get_db()
    cur = dbm.execute(
        '''
        select 
            s.id,
            title,
            s.image,
            link,
            release_date,
            listen,
            r.name as region,
            g.name as genre
        from song as s
        join region as r
            on r.id = s.region_id
        join genre as g
            on g.id = s.genre_id
        where s.title like ?
        ''',['%' + songname + '%'])
    result_song = cur.fetchall()
    if not result_song:
        return jsonify({'err':1,'msg':'Not Found'})
    result_dict_song = []
    for song in result_song:
        song_dict = {
            'id' : song['id'],
            'title': song['title'],
            'image': song['image'],
            'link': song['link'],
            'release_date':song['release_date'],
            'listen': song['listen'],
            'region': song['region'],
            'genre' : song['genre']
        }
        dbm = get_db()
        cur1 = dbm.execute(
        '''
        select 
            a.id,
            a.name,
            a.image
        from artist as a
        join performence as p
        on a.id = p.artist_id
        join song as s
        on s.id = p.song_id
        where s.id = ?
        ''',[song['id']])
        result_artist = cur1.fetchall()
        result_dict_artist = []
        for artist in result_artist:
            ar_dict = {
                'id':artist['id'],
                'name':artist['name'],
                'image':artist['image']
            }
            result_dict_artist.append(ar_dict)
        song_dict.update({'artist':result_dict_artist})
        result_dict_song.append(song_dict)

    result_return = {'err':0,'msg':'Success','data': {'song':result_dict_song}}
    return jsonify(result_return)

if __name__ == '__main__':
    app.run(debug=True)