from flask import request,render_template,redirect, Flask
from flask import current_app as app
from application.models import user,librarian,section,book_catalogue
from application.models import analysis,manage,book_issue,keeps_track_of
from application.database import db
@app.route("/add_section/<string:lid>",methods=['GET','POST'])

def add_section(lid):
    if request.method=='POST':
        title=request.form.get("title")
        title=title.upper()
        date=request.form.get("date")
        description=request.form.get("Description")
        s=section.query.all()
        sid=s[-1].section_id
        sid2=sid[:-1]
        sid2+=str(int(sid[-1])+1)
        section_id=sid2
        new_section=section(section_id=section_id,title=title,date=date,description=description)
        db.session.add(new_section)
        db.session.commit()
        M=manage(librarian_id=lid,section_id=section_id)
        db.session.add(M)
        db.session.commit()
        return redirect("/librarian_dashboard/"+lid)
    
    else:
        return render_template("add_section.html",message='Welcome to add section page',id=lid)

@app.route("/section_page/<string:lid>/<string:section_id>",methods=['GET','POST'])
def section_page(lid,section_id):
    if request.method=='GET':
        Section=section.query.get(section_id)
        book=book_catalogue.query.filter(book_catalogue.section_id==section_id).all()
        return render_template("section_page.html",Section=Section,id=lid,book=book)    

@app.route("/delete_page/<string:lid>/<string:section_id>",methods=['GET','POST'])

def delete_page(lid,section_id):
        if request.method=='GET':
            s=db.session.query(section).filter(section.section_id==section_id).all()
            book=db.session.query(book_catalogue).filter(book_catalogue.section_id==section_id).all()
            for z in book:
                isbn=z.ISBN_no
                bi=db.session.query(book_issue).filter(book_issue.ISBN_no==isbn).all()
                for c in bi:
                    db.session.delete(c)
                    db.session.commit()
                db.session.delete(z)
                db.session.commit()
            s=db.session.query(section).filter(section.section_id==section_id).all()
            for a in s:
                db.session.delete(a)
                db.session.commit()
            
            a=db.session.query(analysis).filter(analysis.section_id==section_id).first()
            if a!=None:
                db.session.delete(a)
                db.session.commit()
            return redirect("/librarian_dashboard/"+lid)
    

@app.route("/edit_section/<string:lid>/<string:sid>",methods=['GET','POST'])

def edit1(lid,sid):
    if request.method=='GET':
        S=db.session.query(section).filter(section.section_id==sid).all()
        title1=""
        date=""
        description=""
        for x in  S:
            title1=x.title
            date=x.date
            description=x.description
    
        return render_template("edit_section.html",title1=title1,date=date,description=description,id=lid,section_id=sid)
    
    else:
        title1=request.form.get("title")
        date=request.form.get("date")
        description=request.form.get("Description")
        
        S=db.session.query(section).filter(section.section_id==sid).all()
        
        for x in S:
            x.title=title1
            x.date=date
            x.description=description
            db.session.commit()
        
        return redirect("/librarian_dashboard/"+lid)
        
        
#create custom error pages
    
#Invalid url   
@app.errorhandler(404)

def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server error

@app.errorhandler(500)

def interbal_error(e):
    return render_template("500.html"), 500
        