from flask import Flask, render_template, redirect, url_for, flash, request, abort,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import matplotlib.pyplot as plt
from flask_admin import Admin, AdminIndexView, expose, BaseView
from datetime import datetime
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcxzhjghehger'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:B20DCVT009@localhost/music'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
admin = Admin(app, name='Quản trị người dùng', template_mode='bootstrap3')


# Class object cho bảng Users
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(25), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    def __str__(self):
        return self.username

# Class object cho bảng Artist
class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng Song
class Song(db.Model):
    __tablename__ = 'Song'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    genre = db.relationship('Genre',backref='genres')
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    region = db.relationship('Region',backref = 'regions')
    release_date = db.Column(Date,nullable=False)
    listen = db.Column(db.Integer, default = 0)
    def __str__(self):
        return self.title
    
class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng Region
class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng DSYT (Danh sách yêu thích)
class Favorites(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') , primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('Song.id'), primary_key=True)
    user = db.relationship('User')
    song = db.relationship('Song')

class Performence(db.Model):
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id') , primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('Song.id'), primary_key=True)
    # Thêm quan hệ many-to-one với bảng Artist
    artist = db.relationship('Artist')
    # Thêm quan hệ many-to-one với bảng Song
    song = db.relationship('Song')

class SongView(ModelView):
    edit_modal = True
    details_modal = True
    create_modal = True
    column_list = ['title', 'genre', 'region', 'listen', 'release_date']
    # column_list = ['title', 'artists']

class ArtistView(ModelView):
    edit_modal = True
    create_modal = True
    details_modal = True

class DSYT_view(ModelView):
    # form_columns = ['user_id','song_id']
    # column_list = ['user_id','song_id']
    pass

class PerformanceModelView(ModelView):
    # Đặt tên cho mục quản lý trên trang admin
    column_label = "Performence"


admin.add_view(ModelView(User,db.session))
admin.add_view(SongView(Song, db.session))
admin.add_view(ArtistView(Artist, db.session))
admin.add_view(ModelView(Genre,db.session))
admin.add_view(ModelView(Region,db.session))
admin.add_view(DSYT_view(Favorites, db.session))
admin.add_view(PerformanceModelView(Performence, db.session))



#lấy thông tin các bài hát
@app.route('/songs', methods=['GET'])
def get_songs():
    # Kết nối các bảng Song, Genre, và Performence thông qua câu lệnh SQL
    sql_query = """
    SELECT Song.id, Song.title, Song.image, Song.link,Song.listen,Song.release_date, Genre.name AS genre,Region.name AS region, Artist.name AS artist
    FROM Song
    JOIN Genre ON Song.genre_id = Genre.id
    JOIN Region ON Region.id = Song.region_id
    JOIN Performence ON Song.id = Performence.song_id
    JOIN Artist ON Performence.artist_id = Artist.id
    """
    result = db.session.execute(sql_query)
    # Khởi tạo một dict để theo dõi bài hát và ca sĩ
    songs_dict = {}

    for row in result:
        song_id = row.id
        if song_id not in songs_dict:
        # Nếu bài hát chưa có trong dict, thêm nó vào với thông tin cơ bản
            songs_dict[song_id] = {
                'id': row.id,
                'title': row.title,
                'image': row.image,
                'link': row.link,
                'listen':row.listen,
                'release' :row.release_date,
                'artists': []  # Khởi tạo danh sách ca sĩ cho bài hát
            }
        # Thêm thông tin về ca sĩ cho bài hát
        artist_data = {
            'name': row.artist,
            }
        songs_dict[song_id]['artists'].append(artist_data)

# Chuyển đổi dict thành danh sách để trả về dưới dạng JSON
    song_list = list(songs_dict.values())
    return jsonify({'songs': song_list})



from flask import jsonify

# Route để lấy thông tin chi tiết của một bài hát theo ID
@app.route('/songs/<int:song_id>', methods=['GET'])
def get_song_by_id(song_id):
    sql_query = """
    SELECT Song.id, Song.title, Song.image, Song.link, Song.listen,Song.release_date, Genre.name AS genre, Region.name AS region, Artist.name AS artist
    FROM Song
    JOIN Performence ON Song.id = Performence.song_id
    JOIN Artist ON Performence.artist_id = Artist.id
    JOIN Genre ON Song.genre_id = Genre.id
    JOIN Region ON Region.id = Song.region_id
    WHERE Song.id = :song_id
    """
    result = db.session.execute(sql_query, {'song_id': song_id})
    song = result.fetchone()
    if song is None:
        return jsonify({'error': 'Song not found'}), 404
    db.session.execute(f"UPDATE Song SET listen = {song.listen + 1} WHERE id = {song_id}")
    db.session.commit()

    artist_query = """
    SELECT Artist.name AS artist
    FROM Performence
    JOIN Artist ON Performence.artist_id = Artist.id
    WHERE Performence.song_id = :song_id
    """
    artist_result = db.session.execute(artist_query, {'song_id': song_id})
    artists = [{'name': row.artist} for row in artist_result]
    song_info = {
        'id': song.id,
        'title': song.title,
        'image': song.image,
        'link': song.link,
        'genre': song.genre,
        'region': song.region,
        'release' :song.release_date,
        'listen_count': song.listen + 1,
        'artists': artists
    }

    return jsonify({'song': song_info})






if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
