from flask import request,render_template,redirect,flash
from flask import current_app as app
from application.models import user,librarian,section,book_catalogue,manage
from application.models import analysis,keeps_track_of,role,reviews,book_issue
from application.database import db
import base64

from datetime import date
import matplotlib.pyplot as plt
import numpy as np




@app.route("/user_login_page",methods=["GET","POST"])

def user_login():
    if request.method=="GET":
        return render_template("user_login_page.html",message="Welcome to user_login page")
    else:
        user_email1=request.form.get("email2")
        user_password=request.form.get("pass2")
        users=db.session.query(user).filter(user.user_email==user_email1).all()
        user_id=""
        for x in users:
            user_id=x.user_id
        if user_id=="":
            return render_template("user_login_page.html",message="user does'nt exist")
        else:
            new_user=user.query.get(user_id)
        if new_user.user_email!=user_email1:
                return render_template("user_login_page.html",message="incorrect email")
        else:
            if new_user.password!=user_password:
               return render_template("user_login_page.html",message="password is not matched")
            else:
                flash("You are logged in Successfully!")
                return redirect("/user_dashboard/"+user_id)
            
@app.route("/forgot_password",methods=['GET','POST'])

def  f():
    if request.method=='GET':
        return render_template("forgot_pass.html",message="Welcome to forgot password page here you can retrieve your password")
    else:
        email=request.form.get("email2")
        passw=request.form.get("pass2")
        conpass=request.form.get("conpass2")
        
        if conpass!=passw:
            flash("Confirm and password aren't matching please keeep them same")
            return render_template("forgot_pass.html")
        
        else:
            e=db.session.query(user).filter(user.user_email==email).all()
            if e==[]:
                flash("Email didn't exist in database better you register first!")
                return render_template("user_register.html")
            else:
                for x in e:
                    x.password=passw
                    db.session.commit()
                flash("password sucessfully updated you can log into your account now!")
                return render_template("user_login_page.html")
            

@app.route("/user_stats/<string:uid>",methods=['GET','POST'])

def user_stats(uid):
    count_list=[]
    section_name=[]
    
    a=db.session.query(analysis).all()
    for x in a:
        if x.user_id==uid:
            b=db.session.query(section).filter(section.section_id==x.section_id).all()
            for y in b:
                section_name.append(y.title)
            count_list.append(x.count)
    
    print(section_name)
    print(count_list)
    plt.pie(count_list, labels=section_name, autopct='%1.1f%%', startangle=140)
    plt.axis('equal') 
    plt.title('Percentage of Books Taken from Each Section')
    img_file = 'D:\\mad-1p\\project_1\\static\\images\\plot.png' 
    plt.savefig(img_file)
    plt.close()
    with open(img_file, 'rb') as file:
        encoded_img = base64.b64encode(file.read()).decode('utf-8')
    
    return render_template("stats.html",plot=encoded_img,id=uid)
                
        
    
@app.route("/user_register",methods=["GET","POST"])

def user_register():
    if request.method=="GET":
        return render_template("user_register.html",message="Welcome to user_register_page")
    else:
        user_id='UID00'+str(int(user.query.count())+1)
        user_fname1=request.form.get("fname")
        user_lname1=request.form.get("lname")
        user_email1=request.form.get("email2")
        user_password1=request.form.get("pass2")
        conpass=request.form.get("conpass2")
        type=request.form.get("selected_sid")
        if user_password1!=conpass:
            return render_template("user_register.html",message="Confirm Password and Password are not same please re-enter")
        users=user.query.get(user_id)
        if users==None:
            if user_email1[len(user_email1)-4:]!=".com":
                return render_template("user_register.html",message="incorrect username")
            new_user=user(user_id=user_id,user_fname=user_fname1,user_lname=user_lname1,user_email=user_email1,password=user_password1)
            db.session.add(new_user)
            db.session.commit()
            quota=0
            t=""
            if type=='Faculty':
                quota=10
                t="fac"
            elif type=='under_graduate':
                quota=7
                t="ug"
            elif type=="post_graduate":
                quota=8
                t="pg"
            else:
                quota=9
                t="phd"
            
            new_role=role(user_id=user_id,type=t,quota=quota)
            db.session.add(new_role)
            db.session.commit()
            flash("Registered Successfully!!")    
            return redirect("/user_login_page")
        else:
            return render_template("user_register.html",message="user already exists")
    
@app.route("/user_dashboard/<string:user_id>",methods=['GET','POST'])

def user_dashboard(user_id):
    if request.method=='GET':
        new_user=user.query.get(user_id)
        sections=[]
        S=section.query.all()
        for x in S:
            sections.append(x.title)
        
        author=[]
        A=book_catalogue.query.all()
        for  y in A:
            author.append(y.auth_fname)
        return render_template('user_dashboard.html',message=f'Hey {new_user.user_fname} {new_user.user_lname} Welcome to your dashboard',id=user_id,labels=sections,authors=author)
    elif request.method=="POST":
        text=request.form.get("selected_sid")
        text2=request.form.get("selected_id")
        if text2=="":
            book=book_catalogue.query.join(section).add_columns(book_catalogue.auth_fname,book_catalogue.auth_lname,book_catalogue.ISBN_no,book_catalogue.section_id,book_catalogue.title,book_catalogue.publisher,section.description,book_catalogue.year).filter(book_catalogue.section_id==section.section_id).filter(section.title==text).all()
        else:
            book=book_catalogue.query.join(section).add_columns(book_catalogue.auth_fname,book_catalogue.auth_lname,book_catalogue.ISBN_no,book_catalogue.section_id,book_catalogue.title,book_catalogue.publisher,section.description,book_catalogue.year).filter(book_catalogue.section_id==section.section_id).filter(book_catalogue.auth_fname==text2).all()
            
        return render_template("user_books.html",book=book,id=user_id)
                
    
@app.route("/user_dashboard/<string:uid>/books",methods=['GET','POST'])

def user_dashboard_books(uid):
    book=book_catalogue.query.all()
    return render_template("user_books.html",message="Welcome to books",book=book,id=uid)

@app.route("/view_feedback/<string:uid>/<string:isbn>")

def view_feedback(uid,isbn):
    feedback={}
    books=db.session.query(reviews).filter(reviews.ISBN_no==isbn).all()
    for x in books:
        if x.ISBN_no not in feedback:
            feedback[x.ISBN_no]=[]
        dict={}
        dict['user_id']=x.user_id
        dict['feedback']=x.feedback
        dict['rating']=x.rating
        feedback[x.ISBN_no].append(dict)
    
    books=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==isbn).all()
    title=""
    for x in books:
        title=x.title
    
    return render_template("review.html",feedback=feedback,id=uid,title=title)

@app.route("/withdraw_request/<string:uid>/<string:isbn>",methods=['GET','POST'])

def withdraw_request(uid,isbn):
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
    
        return redirect("/my_books/"+uid)

@app.route("/ask_feedback/<string:uid>/<string:isbn>",methods=['GET','POST'])

def ask_feedback(uid,isbn):
    if request.method=='GET':
        return render_template("ask_review.html",id=uid,isbn=isbn)
    
@app.route("/return_book/<string:uid>/<string:isbn>",methods=['GET','POST'])

def return_book(uid,isbn):
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
        sid=""   
        s=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==isbn).all()
        for x in s:
            sid=x.section_id
        
        a=db.session.query(analysis).filter(analysis.section_id==sid).filter(analysis.user_id==uid).all()
        if a==[]:
            a=analysis(user_id=uid,section_id=sid,count=1)
            db.session.add(a)
            db.session.commit()
        else:
            for x in a:
                x.count+=1
                db.session.commit()
                
        
            
    
        return redirect("/my_books/"+uid)
    
    else:
        feedback=request.form.get("feed")
        rating=request.form.get("rat")
        f=reviews(user_id=uid,ISBN_no=isbn,feedback=feedback,rating=rating)
        db.session.add(f)
        db.session.commit()
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
    
        return redirect("/my_books/"+uid)
        
@app.route("/re_issue/<string:uid>/<string:isbn>", methods=['GET','POST'])

def re_issue(uid,isbn):
    book=book_catalogue.query.all()
    request_date=date.today()
    bi=db.session.query(book_issue).filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).all()
    bii=book_issue.query.all()
    count=1
        
    for x in bii:
        if x.id==uid:
            count+=1
    if bi!=[]:
        for x in bi:
            if x.request_date!=None:
                return render_template("user_books.html",message="Can't send a request to a book already requested",id=uid,book=book)
            else:
                x.request_date=date.today()
                x.return_date=None
                db.session.commit()
                Section=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==isbn).all()
                sid=""
                for x in Section:
                    if x.ISBN_no==isbn:
                        sid=x.section_id
                M=manage.query.all()
                lid=""
                for x in M:
                    if x.section_id==sid:
                        lid=x.librarian_id
                kt=db.session.query(keeps_track_of).filter(keeps_track_of.user_id==uid).filter(keeps_track_of.librarian_id==lid).all()
                if kt==[]:
                    kt=keeps_track_of(user_id=uid,librarian_id=lid)
                    db.session.add(kt)
                    db.session.commit()
                return redirect("/my_books/"+uid)
            
        if count==6:
            return render_template("user_books.html",message='Maximum request for your account has been reached',id=uid,book=book)
        else:
            bi=book_issue(id=uid,ISBN_no=isbn,request_date=request_date,count=count)
            db.session.add(bi)
            db.session.commit()
            Section=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==isbn).all()
            sid=""
            for x in Section:
                if x.ISBN_no==isbn:
                    sid=x.section_id
            M=manage.query.all()
            lid=""
            for x in M:
                if x.section_id==sid:
                    lid=x.librarian_id
            kt=db.session.query(keeps_track_of).filter(keeps_track_of.user_id==uid).filter(keeps_track_of.librarian_id==lid).all()
            if kt==[]:
                kt=keeps_track_of(user_id=uid,librarian_id=lid)
                db.session.add(kt)
                db.session.commit()
            return render_template("user_books.html",message="Welcome to books",id=uid,book=book)
        
@app.route("/request/<string:uid>/<string:isbn>",methods=['GET','POST'])

def req(uid,isbn):
    if request.method=='GET':
        # print(uid)
        # print(isbn)
        book=book_catalogue.query.all()
        request_date=date.today()
        bi=db.session.query(book_issue).filter(book_issue.id==uid).filter(book_issue.ISBN_no==isbn).all()
        bii=book_issue.query.all()
        count=1
        
        for x in bii:
            if x.id==uid:
                count+=1
        if bi!=[]:
            for x in bi:
                if x.request_date!=None:
                    return render_template("user_books.html",message="Can't send a request to a book already requested",id=uid,book=book)
                else:
                    x.request_date=date.today()
                    x.return_date=None
                    db.session.commit()
                    Section=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==isbn).all()
                    sid=""
                    for x in Section:
                        if x.ISBN_no==isbn:
                            sid=x.section_id
                    M=manage.query.all()
                    lid=""
                    for x in M:
                        if x.section_id==sid:
                            lid=x.librarian_id
                    kt=db.session.query(keeps_track_of).filter(keeps_track_of.user_id==uid).filter(keeps_track_of.librarian_id==lid).all()
                    if kt==[]:
                        kt=keeps_track_of(user_id=uid,librarian_id=lid)
                        db.session.add(kt)
                        db.session.commit()
                    return render_template("user_books.html",message="Welcome to books",id=uid,book=book)
            
        if count==6:
            return render_template("user_books.html",message='Maximum request for your account has beem reached',id=uid,book=book)
        else:
            bi=book_issue(id=uid,ISBN_no=isbn,request_date=request_date,count=count)
            db.session.add(bi)
            db.session.commit()
            Section=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==isbn).all()
            sid=""
            for x in Section:
                if x.ISBN_no==isbn:
                    sid=x.section_id
            M=manage.query.all()
            lid=""
            for x in M:
                if x.section_id==sid:
                    lid=x.librarian_id
            kt=db.session.query(keeps_track_of).filter(keeps_track_of.user_id==uid).filter(keeps_track_of.librarian_id==lid).all()
            if kt==[]:
                kt=keeps_track_of(user_id=uid,librarian_id=lid)
                db.session.add(kt)
                db.session.commit()
            return render_template("user_books.html",message="Welcome to books",id=uid,book=book)
        
        
@app.route("/my_books/<string:uid>",methods=['GET','POST'])

def my_books(uid):
    if request.method=='GET':
        bi=db.session.query(book_issue).filter(book_issue.id==uid).all()
        issued={}
        returned={}
        requested={}
        for x in bi:
            if x.doi!=None:
                book=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==x.ISBN_no).all()
                auth_fname=""
                auth_lname=""
                publisher=""
                title=""
                year=""
                for y in book:
                    auth_fname=y.auth_fname
                    auth_lname=y.auth_lname
                    publisher=y.publisher
                    title=y.title
                    year=y.year
                issued[x.ISBN_no]={}
                issued[x.ISBN_no]["auth_fname"]=auth_fname
                issued[x.ISBN_no]["auth_lname"]=auth_lname
                issued[x.ISBN_no]["title"]=title
                issued[x.ISBN_no]["publisher"]=publisher
                issued[x.ISBN_no]["date"]=year
                issued[x.ISBN_no]["issue_date"]=x.doi
                issued[x.ISBN_no]["due_date"]=x.due_date
                
            elif x.return_date!=None:
                book=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==x.ISBN_no).all()
                returned[x.ISBN_no]={}
                auth_fname=""
                auth_lname=""
                publisher=""
                title=""
                year=""
                for y in book:
                    auth_fname=y.auth_fname
                    auth_lname=y.auth_lname
                    publisher=y.publisher
                    title=y.title
                    year=y.year
                returned[x.ISBN_no]["auth_fname"]=auth_fname
                returned[x.ISBN_no]["auth_lname"]=auth_lname
                returned[x.ISBN_no]["title"]=title
                returned[x.ISBN_no]["publisher"]=publisher
                returned[x.ISBN_no]["date"]=year
                returned[x.ISBN_no]["return_date"]=x.return_date
            else:
                book=db.session.query(book_catalogue).filter(book_catalogue.ISBN_no==x.ISBN_no).all()
                auth_fname=""
                auth_lname=""
                publisher=""
                title=""
                year=""
                for y in book:
                    auth_fname=y.auth_fname
                    auth_lname=y.auth_lname
                    publisher=y.publisher
                    title=y.title
                    year=y.year
                requested[x.ISBN_no]={}
                requested[x.ISBN_no]["auth_fname"]=auth_fname
                requested[x.ISBN_no]["auth_lname"]=auth_lname
                requested[x.ISBN_no]["title"]=title
                requested[x.ISBN_no]["publisher"]=publisher
                requested[x.ISBN_no]["date"]=year
                requested[x.ISBN_no]["request_date"]=x.request_date
    
        return render_template("my_books.html",requested=requested,returned=returned,issued=issued,id=uid)


#create custom error pages
    
#Invalid url   
@app.errorhandler(404)

def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server error

@app.errorhandler(500)

def interbal_error(e):
    return render_template("500.html"), 500