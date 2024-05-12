from flask_restful import Resource,Api,reqparse,fields,marshal_with
from application.models import section,book_catalogue,book_issue,manage,analysis
from application.database import db
from werkzeug.exceptions import HTTPException
import json
from flask import make_response

api=Api()

#### defining errors #######

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {'error_code': error_code, 'error_message': error_message}
        self.response = make_response(json.dumps(message), status_code)

# Section API

# Request Parser JSON

section_request_parse = reqparse.RequestParser()
section_request_parse.add_argument('section_id')
section_request_parse.add_argument('title')
section_request_parse.add_argument('date')
section_request_parse.add_argument("description")

section_response_fields={
    "section_id":fields.String,
    "title":fields.String,
    "date":fields.String,
    "description":fields.String
}


class SectionApi(Resource):
    @marshal_with(section_response_fields)
    def get(self,lid,section_id):
        section_details = db.session.query(
            section).filter(section.section_id == section_id).first()

        if section_details:
            return section_details
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(section_response_fields)
    def put(self,lid,section_id):
        args = section_request_parse.parse_args()
        section_name = args.get('title', None)
        section_date = args.get('date', None)
        section_description = args.get('description', None)
        if section_name is None:
            raise BusinessValidationError(
                status_code=400, error_code='SECTION001', error_message='Section Name is required and should be string')

        if section_date is None:
            raise BusinessValidationError(
                status_code=400, error_code='SECTION002', error_message='Date is required and should be string')

        if section_description is None:
            raise BusinessValidationError(
                status_code=400, error_code='SECTION003', error_message='Description should be string')

        section = db.session.query(section).filter(
            (section.section_id == section_id)).first()

        if section is None:
            raise NotFoundError(status_code=404)

        section.title = section_name
        section.date = section_date
        section.description = section_description

        db.session.add(section)
        db.session.commit()

        return section
    
    
    @marshal_with(section_response_fields)
    def delete(self,lid,section_id):
        section_exist = db.session.query(
            section).filter(section.course_id == section_id).first()

        if section_exist:
            book=db.session.query(book_catalogue).filter(book_catalogue.section_id==section_id).all()
            for z in book:
                isbn=z.ISBN_no
                bi=db.session.query(book_issue).filter(book_issue.ISBN_no==isbn).all()
                for c in bi:
                    db.session.delete(c)
                    db.session.commit()
                db.session.delete(z)
                db.session.commit()
            db.session.delete(section_exist)
            db.session.commit()
            
            a=db.session.query(analysis).filter(analysis.section_id==section_id).first()
            db.session.delete(a)
            db.session.commit()

            return '', 200

        if section_exist is None:
            raise NotFoundError(status_code=404)
        
    @marshal_with(section_response_fields)
    def post(self,lid):
        args = section_request_parse.parse_args()
        section_name = args.get('title', None)
        section_date = args.get('date', None)
        section_description = args.get('description', None)
        section_id="SID00"+str(int(section.query.count())+1)
        if section_name is None:
            raise BusinessValidationError(
                status_code=400, error_code='SECTION001', error_message='Section Name is required and should be string')

        if section_date is None:
            raise BusinessValidationError(
                status_code=400, error_code='SECTION002', error_message='Date is required and should be string')

        if section_description is None:
            raise BusinessValidationError(
                status_code=400, error_code='SECTION003', error_message='Description should be string')
            
        section = db.session.query(section).filter(
            (section.date == section_date) | (section.title== section_name)).first()
        
        if section:
            raise NotFoundError(status_code=409)

        new_section = section(section_id=section_id,date=section_date, title=section_name,
                            description=section_description)
        db.session.add(new_section)
        db.session.commit()
        M=manage(librarian_id=lid,section_id=section_id)
        db.session.add(M)
        db.session.commit()

        return new_section, 201
        

# for the books


book_request_parse = reqparse.RequestParser()
book_request_parse.add_argument('ISBN_no')
book_request_parse.add_argument('section_id')
book_request_parse.add_argument('title')
book_request_parse.add_argument("publisher")
book_request_parse.add_argument("auth_fname")
book_request_parse.add_argument("auth_lname")
book_request_parse.add_argument("year")
book_request_parse.add_argument("no_of_pages")

book_response_fields={
    "ISBN_no":fields.String,
    "section_id":fields.String,
    "title":fields.String,
    "year":fields.String,
    "publisher":fields.String,
    "auth_fname":fields.String,
    "auth_lname":fields.String,
    "no_of_pages":fields.Integer
}
    
class BookApi(Resource):
    @marshal_with(book_response_fields)
    def get(self,lid,isbn):
        book_details = db.session.query(
            book_catalogue).filter(book_catalogue.ISBN_no == isbn).first()

        if book_details:
            return book_details
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(book_response_fields)
    def put(self,lid,isbn):
        
        args = book_request_parse.parse_args()
        auth_fname = args.get('auth_fname', None)
        auth_lname = args.get('auth_lname', None)
        section_id = args.get('section_id', None)
        publisher= args.get('publisher', None)
        year = args.get('year', None)
        title = args.get('title', None)
        no_of_pages = args.get('no_of_pages', None)

        if auth_fname is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK001', error_message='Author First Name is required and should be string')

        if auth_lname is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK002', error_message='Author Last should be string')

        if section_id is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK003', error_message='Section_id is required and should be string')
        if publisher is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK004', error_message='Publisher is required and should be string')
        if year is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK005', error_message='year is required and should be string')
        if title is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK006', error_message='Title is required and should be string')
        if no_of_pages is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK007', error_message='No of pages is required and should be Integer')

        book = db.session.query(book_catalogue).filter(
            (book_catalogue.ISBN_no == isbn)).first()

        if book is None:
            raise NotFoundError(status_code=404)

        book.auth_fname=auth_fname
        book.auth_lname=auth_fname
        book.publisher=publisher
        book.title=title
        book.publisher=publisher
        book.year=year
        book.no_of_pages=no_of_pages
        book.section_id=section_id

        db.session.add(book)
        db.session.commit()

        return book
        
    @marshal_with(book_response_fields)
    def delete(self,isbn):
        book_exist = db.session.query(
            book_catalogue).filter(book_catalogue.ISBN_no == isbn).first()

        if book_exist:
            b=db.session.query(book_issue).filter(book_issue.ISBN_no==isbn).all()
            if b==[]:
                db.session.delete(book_exist)
                db.session.commit()
            else:
                for x in b:
                    if x.doi!=None:
                        pass
                    else:
                        db.session.delete(x)
                        db.session.commit()
                db.session.delete(book_exist)
                db.session.commit()

            return '', 200
        else:
            raise NotFoundError(status_code=404)

    
    @marshal_with(book_response_fields)
    def post(self,lid,sid):
        
        args = book_request_parse.parse_args()
        auth_fname = args.get('auth_fname', None)
        auth_lname = args.get('auth_lname', None)
        publisher= args.get('publisher', None)
        year = args.get('year', None)
        title = args.get('title', None)
        no_of_pages = args.get('no_of_pages', None)
        s=book_catalogue.query.all()
        isbn=s[-1].ISBN_no
        isbn2=isbn[:-1]
        isbn2+=str(int(isbn[-1])+1)
        ISBN_NO1=isbn2

        if auth_fname is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK001', error_message='Author First Name is required and should be string')

        if auth_lname is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK002', error_message='Author Last should be string')

        if sid is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK003', error_message='Section_id is required and should be string')
        if publisher is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK004', error_message='Publisher is required and should be string')
        if year is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK005', error_message='year is required and should be string')
        if title is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK006', error_message='Title is required and should be string')
        if no_of_pages is None:
            raise BusinessValidationError(
                status_code=400, error_code='BOOK007', error_message='No of pages is required and should be Integer')

        book = db.session.query(book_catalogue).filter(
            (book_catalogue.ISBN_no == ISBN_NO1)).first()
        
        if book:
            raise NotFoundError(status_code=409)

        new_book = book_catalogue( year=year, title=title,no_of_pages=no_of_pages,auth_fname=auth_fname,auth_lname=auth_lname,publisher=publisher,section_id=sid,ISBN_no=ISBN_NO1)
        db.session.add(new_book)
        db.session.commit()

        return new_book, 201
        
        
## DEFINE API ROUTES ##

api.add_resource(SectionApi, '/api/section_page/<string:lid>/<string:section_id>',
                 '/api/delete_page/<string:lid>/<string:section_id>',
                 '/api/edit_section/<string:lid>/<string:section_id>',
                 '/api/add_section/<string:lid>')

api.add_resource(BookApi, '/api/view_book/<string:lid>/<string:isbn>',
                 '/api/delete_book/<string:lid>/<string:isbn>',
                 '/api/edit_book/<string:lid>/<string:isbn>',
                 '/api/add_book/<string:lid>/<string:sid>')




