from flask import request,render_template,redirect, flash
from flask import current_app as app
from application.models import user,librarian,section,book_catalogue,manage,book_issue,keeps_track_of,role
from application.database import db
import matplotlib.pyplot as plt

from datetime import date,timedelta
@app.route("/librarian_login",methods=["GET","POST"])

def librarian_login():
    if request.method=="GET":
        return render_template("librarian_login.html",message="Welcome to librarian login page")
    else:
        lib_email1=request.form.get("email2")
        lib_password=request.form.get("pass2")
        new_lib=db.session.query(librarian).filter(librarian.librarian_email==lib_email1).all()
        if new_lib==[]:
            flash("incorrect credentials of librarain")
            return render_template("librarian_login.html")
        lib_id=""
        for x in new_lib:
            lib_id=x.librarian_id
        new_lib=librarian.query.get(lib_id)
        if new_lib.librarian_email!=lib_email1:
            flash("incorrect credentials of librarain")
            return render_template("librarian_login.html")
        else:
            if new_lib.password!=lib_password:
                flash("password is not matched")
                return render_template("librarian_login.html")
        flash("Logged in Successfully")
        return redirect("/librarian_dashboard/"+new_lib.librarian_id)
    
@app.route("/librarian_dashboard/<string:lid>",methods=['GET','POST'])

def librarian_dashboard(lid):
    if request.method=='GET':
        new_lib=librarian.query.get(lid)
        S=db.session.query(section).all()
        Section=[]
        for x in S:
            dict={}
            dict["name"]=x.title
            dict["section_id"]=x.section_id
            Section.append(dict)
        return render_template("librarian_dashboard.html",message=f'Hey {new_lib.librarian_fname} {new_lib.librarian_lname} Welcome to your dashboard',id=lid,Section=Section)
    
@app.route("/view_requests/<string:lid>",methods=['GET','POST'])
def view_requests(lid):
    if request.method=='GET':
        bi=db.session.query(book_issue).all()
        requested={}
        granted={}
        revoked={}
        for x in bi:
            if x.doi!=None:
                if x.due_date<date.today():
                    book=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==x.ISBN_no).all()
                    M=manage.query.all()
                    flag=False
                    sid=""
                    for y in book:
                        if y.ISBN_no==x.ISBN_no:
                            sid=y.section_id
                            break
                
                    for z in M:
                        if z.librarian_id==lid:
                            if z.section_id==sid:
                                flag=True
                    if flag:
                        title=""
                        for y in book:
                            title=y.title
                        if x.id not in revoked:
                            revoked[x.id]=[]
                        dict={}
                        dict["ISBN_NO"]=x.ISBN_no
                        dict["title"]=title
                        dict["revoked_date"]=x.return_date
                        revoked[x.id].append(dict)
                else:       
                    book=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==x.ISBN_no).all()
                    M=manage.query.all()
                    flag=False
                    sid=""
                    for y in book:
                        if y.ISBN_no==x.ISBN_no:
                            sid=y.section_id
                            break
                
                    for z in M:
                        if z.librarian_id==lid:
                            if z.section_id==sid:
                                flag=True
                    if flag:
                        title=""
                        for y in book:
                            title=y.title
                        if x.id not in granted:
                            granted[x.id]=[]
                        dict={}
                        dict["ISBN_NO"]=x.ISBN_no
                        dict["title"]=title
                        dict["granted_date"]=x.doi
                        granted[x.id].append(dict)
                    
            
            elif x.request_date!=None:
                book=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==x.ISBN_no).all()
                M=manage.query.all()
                flag=False
                sid=""
                for y in book:
                    if y.ISBN_no==x.ISBN_no:
                        sid=y.section_id
                        break
                
                for z in M:
                    if z.librarian_id==lid:
                        if z.section_id==sid:
                            flag=True
                if flag:
                    title=""
                    for y in book:
                        title=y.title
                    if x.id not in requested:
                        requested[x.id]=[]
                    dict={}
                    dict["ISBN_NO"]=x.ISBN_no
                    dict["title"]=title
                    dict["requested_date"]=x.request_date
                    requested[x.id].append(dict)
            else:
                book=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==x.ISBN_no).all()
                M=manage.query.all()
                flag=False
                sid=""
                for y in book:
                    if y.ISBN_no==x.ISBN_no:
                        sid=y.section_id
                        break
                
                for z in M:
                    if z.librarian_id==lid:
                        if z.section_id==sid:
                            flag=True
                if flag:
                    title=""
                    for y in book:
                        title=y.title
                    if x.id not in revoked:
                        revoked[x.id]=[]
                    dict={}
                    dict["ISBN_NO"]=x.ISBN_no
                    dict["title"]=title
                    dict["revoked_date"]=x.return_date
                    revoked[x.id].append(dict)
                
        
        return render_template("view_requests.html",granted=granted,requested=requested,id=lid,revoked=revoked)

@app.route("/grant_permission/<string:lid>/<string:uid>/<string:isbn>",methods=['GET','POST'])

def grant(lid,uid,isbn):
    if request.method=='GET':
        bi=book_issue.query.filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).all()
        r=role.query.filter(role.user_id==uid).all()
        amount=0
        for y in r:
            amount=y.quota
        for x in bi:
            x.doi=date.today()
            x.due_date=date.today()+timedelta(days=amount)
            x.return_date=None
            db.session.commit()
    
        return redirect("/view_requests/"+lid)
   
@app.route("/reject_permission/<string:lid>/<string:uid>/<string:isbn>",methods=['GET','POST'])

def reject(lid,uid,isbn):
    if request.method=='GET':
        bi=book_issue.query.filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).all()
        for x in bi:
            db.session.delete(x)
            db.session.commit()
        
        count=1
        bi=book_issue.query.filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).all()
        for x in bi:
            x.count=count
            db.session.commit()
            count+=1
    
        return redirect("/view_requests/"+lid)

@app.route("/revoke_book/<string:lid>/<string:uid>/<string:isbn>",methods=['GET','POST'])

def revoke(lid,uid,isbn):
    if request.method=='GET':
        bi=book_issue.query.filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).all()
        for x in bi:
            x.return_date=date.today()
            x.request_date=None
            x.count=0
            db.session.commit()
        bi=book_issue.query.filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).all()
        for x in bi:
            x.doi=None
            db.session.commit()
        
        bi=book_issue.query.filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).all()
        for x in bi:
            x.due_date=None
            db.session.commit()
        
        
        count=1
        bi=book_issue.query.filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).filter(book_issue.request_date!=None).all()
        for x in bi:
            x.count=count
            db.session.commit()
            count+=1
    
        return redirect("/view_requests/"+lid)

@app.route("/lib_stats/<string:lid>",methods=['GET','POST'])

def lib_stats(lid):
    count_list=[]
    section_name=[]
    
    a=db.session.query(manage).filter(manage.librarian_id==lid).all()
    for x in a:
        s=db.session.query(book_catalogue).filter(book_catalogue.section_id==x.section_id).all()
        count=len(s)
        count_list.append(count)
        s1=db.session.query(section).filter(section.section_id==x.section_id).all()
        for x in s1:
            section_name.append(x.title)
            
    print(section_name)
    print(count_list)
    plt.pie(count_list, labels=section_name, autopct='%1.1f%%', startangle=140)
    plt.axis('equal') 
    plt.title('Percentage of Books Taken from Each Section')
    img_file = 'D:\\mad-1p\\project_1\\static\\images\\plot.png' 
    plt.savefig(img_file)
    plt.close()
    
    return render_template("lib_stats.html",plot='plot.png',id=lid)
                
                
                
#create custom error pages
    
#Invalid url   
@app.errorhandler(404)

def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server error

@app.errorhandler(500)

def interbal_error(e):
    return render_template("500.html"), 500

@app.route("/view_monitors/<string:lid>",methods=['GET','POST'])

def view_monitor(lid):
    k=db.session.query(keeps_track_of).filter(keeps_track_of.librarian_id==lid).all()
    tracker={}
    for x in k:
        tracker[x.user_id]={}
        u=user.query.get(x.user_id)
        tracker[x.user_id]['user_fname']=u.user_fname
        tracker[x.user_id]['user_lname']=u.user_lname
        tracker[x.user_id]['user_email']=u.user_email
        
        bi=db.session.query(book_issue).filter(book_issue.id==x.user_id).all()
        ib=0
        rb=0
        reqb=0
        for y in bi:
            if y.doi!=None:
                ib+=1
            elif y.request_date!=None:
                reqb+=1
            else:
                rb+=1
        
        tracker[x.user_id]["issued_books"]=ib
        tracker[x.user_id]["returned_books"]=rb
        tracker[x.user_id]["requested_books"]=reqb
        
    return render_template("monitor.html",tracker=tracker,id=lid)
        
        
        