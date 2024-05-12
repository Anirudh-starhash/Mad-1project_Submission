from flask import request,render_template,redirect, Flask
from flask import current_app as app
from application.models import user,librarian,section,book_catalogue,manage,book_issue,keeps_track_of
from application.database import db

from datetime import date

@app.route("/" , methods=['GET','POST'])

def index():
    if request.method=='GET':
        return render_template("index.html")

@app.route("/view_book/<string:lid>/<string:isbn>",methods=['GET','POST'])

def view_book(lid,isbn):
    book=book_catalogue.query.join(section).add_columns(book_catalogue.auth_fname,book_catalogue.auth_lname,book_catalogue.ISBN_no,book_catalogue.section_id,book_catalogue.title,book_catalogue.publisher,section.date,section.description).filter(book_catalogue.section_id==section.section_id).filter(book_catalogue.ISBN_no==isbn).all()
    return render_template("view_books.html",book=book,isbn=isbn,id=lid,sid=book[0].section_id)

@app.route("/delete_book/<string:lid>/<string:isbn>", methods=['GET','POST'])

def delete_book(lid,isbn):
    book=book_catalogue.query.get(isbn)
    b=db.session.query(book_issue).filter(book_issue.ISBN_no==isbn).all()
    if b==[]:
        db.session.delete(book)
        db.session.commit()
    else:
        for x in b:
            if x.doi!=None:
                pass
            else:
                db.session.delete(x)
                db.session.commit()
                db.session.delete(book)
                db.session.commit()
            
        
    return redirect("/section_page/"+lid+"/"+book.section_id)

@app.route("/edit_book/<string:lid>/<string:isbn>", methods=['GET','POST'])

def edit_book(lid,isbn):
    if request.method=='GET':
        book=book_catalogue.query.get(isbn)
        auth_fname=book.auth_fname
        auth_lname=book.auth_lname
        publisher=book.publisher
        year=book.year
        title=book.title
        no_of_pages=book.no_of_pages
        
        return render_template("edit_book.html",id=lid,auth_fname=auth_fname,auth_lname=auth_lname,title=title,publisher=publisher,year=year,no_of_pages=no_of_pages,isbn=isbn,sid=book.section_id)
    else:
        book=book_catalogue.query.get(isbn)
        auth_fname=request.form.get("auth_fname")
        auth_lname=request.form.get("auth_lname")
        publisher=request.form.get("publisher")
        title=request.form.get("title")
        year=request.form.get("date")
        no_of_pages=request.form.get("page")
        
        book.auth_fname=auth_fname
        book.auth_lname=auth_lname
        book.publisher=publisher
        book.title=title
        book.no_of_pages=no_of_pages
        book.year=year
        db.session.commit()
            
        return redirect("/section_page/"+lid+"/"+book.section_id)
        

@app.route("/add_book/<string:lid>/<string:sid>",methods=['GET','POST'])

def add_book(lid,sid):
    if request.method=="POST":
        auth_fname=request.form.get("auth_fname")
        auth_lname=request.form.get("auth_lname")
        publisher=request.form.get("publisher")
        title=request.form.get("title")
        year=request.form.get("date")
        page=request.form.get("page")
        s=book_catalogue.query.all()
        isbn=s[-1].ISBN_no
        isbn2=isbn[:-1]
        isbn2+=str(int(isbn[-1])+1)
        ISBN_NO1=isbn2
        new_book=book_catalogue(auth_fname=auth_fname,auth_lname=auth_lname,publisher=publisher,title=title,year=year,ISBN_no=ISBN_NO1,section_id=sid,no_of_pages=int(page))
        db.session.add(new_book)
        db.session.commit()
        return redirect("/section_page/"+lid+"/"+sid)

    else:
        return render_template("add_book.html",sid=sid,id=lid)
    
#create custom error pages
    
#Invalid url   
@app.errorhandler(404)

def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server error

@app.errorhandler(500)

def interbal_error(e):
    return render_template("500.html"), 500
    
