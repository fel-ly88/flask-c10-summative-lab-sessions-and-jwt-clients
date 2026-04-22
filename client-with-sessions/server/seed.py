from config import app,db
from models import User, Workout
from faker import Faker

fake = Faker()

with app.app_context():
    print("Clearing old data...")
    Workout.query.delete()
    User.query.delete()
    db.session.commit()
    
    print("Creating users...")
    users = []
    for _ in range(3):
        user = User(username=fake.unique.user_name())
        user.password = "password123"
        users.append(user)
        db.session.add(user)
        
    db.session.commit()
    
    print("Creating workouts...")
    workout_titles = ["Morning Cardio", "Evening Yoga", "Strength Training", "HIIT Session", "Pilates"]
    for user in users:
        workout = Workout(
            title=fake.random_element(workout_titles),
            description=fake.sentence(),
            duration_minutes=fake.random_int(min=20, max=90),
            user_id=user.id
        )
        db.session.add(workout)
    db.session.commit()
    print("Done! seeded 3 users with 4 workouts each.")