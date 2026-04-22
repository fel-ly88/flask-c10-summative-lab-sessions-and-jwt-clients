from flask import request,session,jsonify
from flask_restful import Api, Resource
from config import app,db
from models import User, Workout

api = Api(app)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")
        password_confirmation = data.get("password_confirmation", "")
        
        errors = []
        if not username:
            errors.append("Username is required.")
        if User.query.filter_by(username=username).first():
            errors.append("Username is already taken.")
        if not password:
            errors.append("Password is required.")
        if password != password_confirmation:
            errors.append("Passwords do not match.")
        if errors:
            return {"errors": errors}, 422
        
        user = User(username=username)
        user.password = password
        db.session.add(user)
        db.session.commit()
        
        session["user_id"] = user.id
        return user.to_dict(), 201
    
class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get("username")).first()
        
        if user and user.authenticate(data.get("password", "")):
            session["user_id"] = user.id
            return user.to_dict(), 200
        
        return {"errors": "Invalid username or password."}, 401
    
class Logout(Resource):
    def delete(self):
        #to clear the session
        session.pop("user_id", None)
        return {}, 204
    
class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {"errors": "No active session."}, 401
    
def get_current_user():
    """Returns the logged-in User or None"""
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None

class WorkoutList(Resource):
    def get(self):
        """GET/workouts - paginated list of current user's workouts"""
        user = get_current_user()
        if not user:
            return {"errors": "Unauthorized"}, 401
        
        #pagination parameters with defaults
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)
        
        pagination = (
            Workout.query.filter_by(user_id=user.id).paginate(page=page, per_page=per_page, error_out=False)
        )
        return {
            "workouts": [w.to_dict() for w in paginated.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
        }, 200
    
    def post (self):
        """POST/workouts -create a new workout"""
        user = get_current_user()
        if not user:
            return {"errors": ["Unauthorized"]}, 401
        
        data = request.get_json()
        errors = []
        if not data.get("title"):
            errors.append("Title is required.")
        if not data.get("description"):
            errors.append("Description is required.")
        if not data.get("duration_minutes"):
            errors.append("Duration is required.")
        if errors:
            return {"errors": errors}, 422
        
        workout = Workout(
            title=data["title"],
            description=data["description"],
            duration_minutes=data["duration_minutes"],
            user_id=user.id
        )
        db.session.add(workout)
        db.session.commit()
        return workout.to_dict(), 201
    
    
class WorkoutDetail(Resource):
    def patch(self,id):
        """PATCH /workouts/<id> - update a workout"""
        user = get_current_user()
        if not user:
            return {"errors": "Unauthorized"}, 401
        
        workout = Workout.query.get(id)
        if not workout:
            return {"errors": "Workout not found."}, 404
        if workout.user_id != user.id:
            return {"errors": "Forbidden"}, 403
        
        data = request.get_json()
        if "title" in data:
            workout.title = data["title"]
        if "description" in data:
            workout.description = data["description"]
        if "duration_minutes" in data:
            workout.duration_minutes = data["duration_minutes"]
            
            db.session.commit()
            return workout.to_dict(), 200     
        
    def delete(self,id):
        """DELETE /workouts/>id> -delete a workout"""
        user = get_current_user()
        if not user:
            return {"errors": "Unauthorized"}, 401
        
        workout = Workout.query.get(id)
        if not workout:
            return {"errors": ["Workout not found"]}, 404
        if workout.user_id != user.id:
            return {"errors": "Forbidden"}, 403
        
        db.session.delete(workout)
        db.session.commit()
        return {}, 204
    
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")
api.add_resource(WorkoutList, "/workouts")
api.add_resource(WorkoutDetail, "/workouts/<int:id>")

if __name__ == "__main__":
    app.run(port=5555, debug=True)