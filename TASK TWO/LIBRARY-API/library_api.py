from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration - Use absolute path
db_path = os.path.join(os.path.dirname(__file__), 'library.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'indian-library-2024'

# Initialize database
db = SQLAlchemy(app)

# ============= DATABASE MODELS =============

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(50))
    published_year = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    available = db.Column(db.Boolean, default=True)
    added_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'language': self.language,
            'published_year': self.published_year,
            'genre': self.genre,
            'available': self.available,
            'added_by': self.added_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# ============= SETUP DATABASE =============

def setup_database():
    """Create database and tables if they don't exist"""
    print("🔄 Setting up database...")
    
    
    # Create all tables
    with app.app_context():
        db.create_all()
        print("✅ Created database tables")
        
        # Check if we need to add sample data
        if Book.query.count() == 0:
            add_sample_data()
        else:
            print(f"✅ Database already has {Book.query.count()} books")

def add_sample_data():
    """Add sample Indian books"""
    print("📚 Adding sample Indian books...")
    
    sample_books = [
        # Added by sai
        Book(title='The God of Small Things', author='Arundhati Roy', 
             language='English', published_year=1997, genre='Fiction', added_by='sai'),
        Book(title='A Suitable Boy', author='Vikram Seth', 
             language='English', published_year=1993, genre='Fiction', added_by='sai'),
        Book(title='Midnight\'s Children', author='Salman Rushdie', 
             language='English', published_year=1981, genre='Magical Realism', added_by='sai'),
        Book(title='The Guide', author='R.K. Narayan', 
             language='English', published_year=1958, genre='Fiction', added_by='sai'),
        Book(title='Godaan', author='Munshi Premchand', 
             language='Hindi', published_year=1936, genre='Social Realism', added_by='sai'),
        Book(title='Ponniyin Selvan', author='Kalki Krishnamurthy', 
             language='Tamil', published_year=1955, genre='Historical Fiction', added_by='sai'),
        Book(title='Gitanjali', author='Rabindranath Tagore', 
             language='Bengali', published_year=1910, genre='Poetry', added_by='sai'),
        Book(title='The Argumentative Indian', author='Amartya Sen', 
             language='English', published_year=2005, genre='Non-Fiction', added_by='sai'),
        Book(title='Yayati', author='V.S. Khandekar', 
             language='Marathi', published_year=1959, genre='Mythological Fiction', added_by='sai'),
        Book(title='The Rozabal Line', author='Ashwin Sanghi', 
             language='English', published_year=2007, genre='Thriller', added_by='sai'),
        
        # Added by teja
        Book(title='The White Tiger', author='Aravind Adiga', 
             language='English', published_year=2008, genre='Fiction', added_by='teja'),
        Book(title='Malgudi Days', author='R.K. Narayan', 
             language='English', published_year=1943, genre='Short Stories', added_by='teja'),
        Book(title='Train to Pakistan', author='Khushwant Singh', 
             language='English', published_year=1956, genre='Historical Fiction', added_by='teja'),
        Book(title='Nirmala', author='Munshi Premchand', 
             language='Hindi', published_year=1927, genre='Social Fiction', added_by='teja'),
        Book(title='The Inheritance of Loss', author='Kiran Desai', 
             language='English', published_year=2006, genre='Fiction', added_by='teja'),
        Book(title='The Palace of Illusions', author='Chitra Banerjee Divakaruni', 
             language='English', published_year=2008, genre='Mythological Fiction', added_by='teja'),
        Book(title='The Ministry of Utmost Happiness', author='Arundhati Roy', 
             language='English', published_year=2017, genre='Fiction', added_by='teja'),
        Book(title='India After Gandhi', author='Ramachandra Guha', 
             language='English', published_year=2007, genre='History', added_by='teja'),
        Book(title='Chokher Bali', author='Rabindranath Tagore', 
             language='Bengali', published_year=1903, genre='Fiction', added_by='teja'),
        Book(title='Chanakya\'s Chant', author='Ashwin Sanghi', 
             language='English', published_year=2010, genre='Historical Fiction', added_by='teja'),
    ]
    
    db.session.add_all(sample_books)
    db.session.commit()
    print(f"✅ Added {len(sample_books)} Indian books (10 by sai, 10 by teja)")

# ============= AUTHENTICATION =============

VALID_USERS = {
    'sai': 'sai@123',
    'teja': 'teja@123'
}

def check_auth(username, password):
    return username in VALID_USERS and VALID_USERS[username] == password

def require_auth(f):
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            auth_type, credentials = auth.split(' ')
            if auth_type != 'Basic':
                return jsonify({'error': 'Only Basic auth supported'}), 401
            
            import base64
            decoded = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded.split(':')
            
            if not check_auth(username, password):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            request.user = username
            return f(*args, **kwargs)
        except:
            return jsonify({'error': 'Invalid auth format'}), 401
    
    decorated.__name__ = f.__name__
    return decorated

# ============= ROUTES =============

@app.route('/')
def home():
    return jsonify({
        'message': 'Indian Library API',
        'credentials': {
            'sai': 'sai@123 (admin)',
            'teja': 'teja@123 (librarian)'
        },
        'endpoints': [
            'GET /api/books',
            'GET /api/books/search?q=query',
            'POST /api/books',
            'GET /api/stats'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health():
    with app.app_context():
        count = Book.query.count()
    return jsonify({
        'status': 'healthy',
        'books_count': count,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/books', methods=['GET'])
@require_auth
def get_books():
    books = Book.query.all()
    return jsonify({
        'success': True,
        'user': request.user,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })

@app.route('/api/books/<int:book_id>', methods=['GET'])
@require_auth
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book.to_dict())

@app.route('/api/books', methods=['POST'])
@require_auth
def add_book():
    data = request.json
    
    if not data.get('title') or not data.get('author'):
        return jsonify({'error': 'Title and author required'}), 400
    
    book = Book(
        title=data['title'],
        author=data['author'],
        language=data.get('language', 'English'),
        published_year=data.get('published_year'),
        genre=data.get('genre', 'General'),
        available=data.get('available', True),
        added_by=request.user
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Book added successfully',
        'book': book.to_dict(),
        'added_by': request.user
    }), 201

@app.route('/api/books/search', methods=['GET'])
@require_auth
def search_books():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    books = Book.query.filter(
        Book.title.contains(query) |
        Book.author.contains(query) |
        Book.genre.contains(query) |
        Book.language.contains(query)
    ).all()
    
    return jsonify({
        'success': True,
        'query': query,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@require_auth
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    if request.user != 'sai':
        return jsonify({'error': 'Only sai can delete books'}), 403
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Book deleted',
        'deleted_by': request.user
    })

@app.route('/api/stats', methods=['GET'])
@require_auth
def get_stats():
    total = Book.query.count()
    available = Book.query.filter_by(available=True).count()
    by_sai = Book.query.filter_by(added_by='sai').count()
    by_teja = Book.query.filter_by(added_by='teja').count()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_books': total,
            'available_books': available,
            'books_by_sai': by_sai,
            'books_by_teja': by_teja,
            'languages': {
                'English': Book.query.filter_by(language='English').count(),
                'Hindi': Book.query.filter_by(language='Hindi').count(),
                'Tamil': Book.query.filter_by(language='Tamil').count(),
                'Bengali': Book.query.filter_by(language='Bengali').count(),
                'Marathi': Book.query.filter_by(language='Marathi').count()
            }
        }
    })

# ============= MAIN =============

if __name__ == '__main__':
    print("🚀 Starting Indian Library API...")
    print("=" * 50)
    
    # Setup database
    with app.app_context():
        setup_database()
    
    print("=" * 50)
    print("✅ API Ready! Access: http://localhost:5000")
    print("🔑 Login Credentials:")
    print("   Username: sai     Password: sai@123")
    print("   Username: teja    Password: teja@123")
    print("=" * 50)
    print("📚 Sample Commands:")
    print("   curl http://localhost:5000/api/health")
    print("   curl -u sai:sai@123 http://localhost:5000/api/books")
    print("=" * 50)
    
    app.run(debug=True, port=5000, use_reloader=False)