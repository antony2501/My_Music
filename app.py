from flask import Flask, render_template, redirect, url_for, flash, request, abort,jsonify
from flask_sqlalchemy import SQLAlchemy
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
# Class object cho bảng Users
class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.username

# Class object cho bảng Artist
class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng Song
class Song(db.Model):
    __tablename__ = 'Song'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    artist = db.relationship('Artist',backref='songs')
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    genre = db.relationship('Genre')
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    region = db.relationship('Region')
    link = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.title

# Class object cho bảng Genre
class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng Region
class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    def __str__(self):
        return self.name

# Class object cho bảng DSYT (Danh sách yêu thích)
class DSYT(db.Model):
    __tablename__ = 'DSYT'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    user = db.relationship('User')
    song_id = db.Column(db.Integer, db.ForeignKey('Song.id'), primary_key=True)
    song = db.relationship('Song')

class SongView(ModelView):
    edit_modal = True
    details_modal = True
    create_modal = True

class ArtistView(ModelView):
    edit_modal = True
    details_modal = True
    create_modal = True

admin.add_view(ModelView(User, db.session))
admin.add_view(ArtistView(Artist, db.session))
admin.add_view(SongView(Song, db.session))
admin.add_view(ModelView(Region, db.session))
admin.add_view(ModelView(Genre , db.session))
admin.add_view(ModelView(DSYT, db.session))



@app.route('/song', methods=['GET'])
def get_songs():
    # Truy vấn dữ liệu từ cơ sở dữ liệu sử dụng SQLAlchemy
    songs = Song.query.all()
    # Tạo một danh sách chứa thông tin của từng bài hát
    songs_list = []
    for song in songs:
        song_info = {
            'title': song.title,
            'artist': song.artist.name,  # Truy vấn tên nghệ sĩ từ quan hệ
            'genre': song.genre.name,    # Truy vấn tên thể loại từ quan hệ
            'region': song.region.name,  # Truy vấn tên vùng miền từ quan hệ
            'link': song.link
        }
        songs_list.append(song_info)
    # Convert danh sách bài hát thành một JSON response
    return jsonify({'songs': songs_list})



@app.route('/song/<int:song_id>', methods=['GET'])
def get_song(song_id):
    # Truy vấn dữ liệu của bài hát theo ID
    song = Song.query.get(song_id)
    if song is None:
        return jsonify({'error': 'Bài hát không tồn tại'}), 404
    # Tạo dictionary chứa thông tin của bài hát
    song_info = {
        'title': song.title,
        'artist': song.artist.name,
        'genre': song.genre.name,
        'region': song.region.name,
        'link': song.link
    }
    # Convert dictionary thành JSON response
    return jsonify(song_info)


@app.route('/songs-by-genre', methods=['GET'])
def songs_by_genre():
    genre_name = request.args.get('genre')  # Lấy thể loại từ query parameter
    songs = Song.query.join(Genre).filter(Genre.name == genre_name).all()
    songs_list = []
    for song in songs:
        song_info = {
            'title': song.title,
            'artist': song.artist.name,
            'genre': song.genre.name,
            'region': song.region.name,
            'link': song.link
        }
        songs_list.append(song_info)

    return jsonify({'songs': songs_list})



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
