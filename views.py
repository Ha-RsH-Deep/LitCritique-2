from flask import Blueprint,render_template,request, flash, redirect, url_for,g
from flask_login import login_user, login_required, logout_user, current_user
import sqlite3
from django.shortcuts import render, redirect
from .models import Book, Review
import os
from flask_paginate import Pagination, get_page_parameter
import math




views = Blueprint('views', __name__)


DATABASE = '/home/harshdeep/Desktop/LitCritique/instance/LITCRITQUE.db'

@views.route('/home')
def home():
    return render_template('home.html',user = current_user)
    

@views.route('/community')
def community():
    return render_template('community.html',user = current_user)
    

@views.route('/trending')
def trending():
    return 'Trending book of the books!'



@views.route('/contactus')
def contactus():
    return render_template('contactus.html',user = current_user)




@views.route('/supportus')
def supportus():
    return render_template('supportus.html',user = current_user)


@views.route('/', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_query = request.form["search_query"]
        results = Book.query.filter(Book.title.like('%' + search_query + '%')).all()
        return render_template("search_books.html", results=results, user=current_user)
    return render_template("home.html", user=current_user)

@views.route('/book/<title>')
def book(title):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT book.title, book.authors, book.image, book.previewLink,
               book.description, book.rating, book.publisher, book.Categories
        FROM book
        WHERE book.title = ?
    """, (title,))    
    book = cursor.fetchone()
    if book is None:
        #flash("Book not found.")
        return redirect(url_for("views.home"))
    # Get the reviews for the book
    cursor.execute("""
        SELECT review_summary, review_text, rating_user, user_name
        FROM review
        WHERE book_title = ?
    """, (title,))
    reviews = cursor.fetchall()
    return render_template("book_details.html",book_title=book[0], book_author=book[1], book_image=book[2], book_preview=book[3], book_description=book[4], book_rating=book[5], book_publisher=book[6], book_categories=book[7], user=current_user, reviews=reviews)

@views.route('/book/<title>/add_review', methods=['POST','GET'])
@login_required
def add_review(title):
    rating_user = int(request.form['rating_user'])
    review_summary = request.form['review_summary']
    review_text = request.form['review_text']
    user_name = current_user.user_name
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO review (book_title, user_name, rating_user, review_summary, review_text)
        VALUES (?, ?, ?, ?, ?)
    """, (title, user_name, rating_user, review_summary, review_text))
    conn.commit()
    conn.close()
    return redirect(url_for('views.book', title=title))




@views.route('/category/<category>')
def category(category):
    per_page = 100
    page = request.args.get('page', 1, type=int)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT book.title, book.authors, book.image, book.previewLink,
               book.description, book.rating, book.publisher, book.Categories
        FROM book
        WHERE book.Categories LIKE ?
    """, ('%' + category + '%',))
    books = cursor.fetchall()
    if not books:
        flash("No books found in this category.")
        return redirect(url_for("views.home"))
    total_pages = math.ceil(len(books) / per_page)
    pagination = Pagination(page=page, per_page=per_page, total=len(books), css_framework="bootstrap4")
    start = (page - 1) * per_page
    end = start + per_page
    books = books[start:end]
    return render_template("category.html", category=category, books=books, pagination=pagination, user=current_user, total_pages=total_pages , page=page)



@views.route("/categories")
def categories():
    per_page = 100
    page = request.args.get('page', 1, type=int)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    query = request.args.get('query')
    if query:
        cursor.execute("""
            SELECT DISTINCT Categories
            FROM book
            WHERE Categories IS NOT NULL AND Categories LIKE ?
        """, ('%' + query + '%',))
    else:
        cursor.execute("""
            SELECT DISTINCT Categories
            FROM book
            WHERE Categories IS NOT NULL
        """)
    
    categories = [category[0] for category in cursor.fetchall()]
    categories.sort()
    total_pages = math.ceil(len(categories) / per_page)
    pagination = Pagination(page=page, per_page=per_page, total=len(categories), css_framework="bootstrap4")
    start = (page - 1) * per_page
    end = start + per_page
    categories = categories[start:end]
    return render_template("categories.html", categories=categories, pagination=pagination, user=current_user, total_pages=total_pages , page=page)


@views.route('/author/<author>')
def author(author):
    per_page = 100
    page = request.args.get('page', 1, type=int)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT book.title, book.authors, book.image, book.previewLink,
               book.description, book.rating, book.publisher, book.Categories
        FROM book
        WHERE book.authors LIKE ?
    """, ('%' + author + '%',))
    books = cursor.fetchall()
    if not books:
        flash("No books found by this Author.")
        return redirect(url_for("views.home"))
    total_pages = math.ceil(len(books) / per_page)
    pagination = Pagination(page=page, per_page=per_page, total=len(books), css_framework="bootstrap4")
    start = (page - 1) * per_page
    end = start + per_page
    books = books[start:end]
    return render_template("author.html", author = author, books=books, pagination=pagination, user=current_user, total_pages=total_pages , page=page)



@views.route("/authors")
def authorss():
    per_page = 100
    page = request.args.get('page', 1, type=int)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    query = request.args.get('query')
    if query:
        cursor.execute("""
            SELECT DISTINCT authors
            FROM book
            WHERE authors IS NOT NULL AND authors LIKE ?
        """, ('%' + query + '%',))
    else:
        cursor.execute("""
            SELECT DISTINCT authors
            FROM book
            WHERE authors IS NOT NULL
        """)
    
    authors = [author[0] for author in cursor.fetchall()]
    authors.sort()
    total_pages = math.ceil(len(authors) / per_page)
    pagination = Pagination(page=page, per_page=per_page, total=len(authors), css_framework="bootstrap4")
    start = (page - 1) * per_page
    end = start + per_page
    authors = authors[start:end]
    return render_template("authors.html", authors=authors, pagination=pagination, user=current_user, total_pages=total_pages , page=page)



@views.route('/userprofile')
@login_required
def userprofile():
    return render_template('userprofile.html',user = current_user)

@views.route('/add_to_reading_list/<int:book_id>')
@login_required
def add_to_reading_list(book_id):
    book = Book.query.get(book_id)
    current_user.reading_list.append(book)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    conn.commit()
    conn.close()
    flash('Book added to reading list.')
    return redirect(url_for('book_details', book_id=book.index))



@views.route('/treanding')
def treanding():
    categories = ['Fiction', 'ART', 'Religion','Psychology', 'Biography & Autobiography', 'Cooking', 'Political Science', 'Technology & Engineering', 'History', 'Humor']
    
    books = []
    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()
    for category in categories:
        
        category_books = cursor.execute("""
            SELECT book.id, book.title, book.authors, book.rating, book.image
            FROM book
            JOIN review ON book.title = review.book_title
            WHERE book.Categories = ?
            GROUP BY book.id
            ORDER BY COUNT(review.id) DESC
            LIMIT 5
        """, (category,)).fetchall()
        books.append((category, category_books))
    
    conn.close()
    return render_template('treanding.html', books=books, user=current_user)




