"""
Script to add English story lessons as admin
Run: python3 add_english_stories.py
"""
from app import create_app
from app.models.learning import Portal, Lesson, Quiz, QuizQuestion, Task
from app.models.user import User
from app.extensions import db
from app.utils.youtube import extract_youtube_id
from app.services.scoring import update_quiz_total_points
import sys

app = create_app()

with app.app_context():
    # Check for admin user
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        print("❌ No admin user found. Please create an admin first using create_admin.py")
        sys.exit(1)
    
    print(f"✓ Using admin: {admin.email}")
    
    # Find or create "English Lessons" portal
    portal = Portal.query.filter_by(name="English Lessons").first()
    if not portal:
        portal = Portal(
            name="English Lessons",
            description="Practice English with engaging short stories and comprehension quizzes"
        )
        db.session.add(portal)
        db.session.commit()
        print(f"✓ Created portal: {portal.name}")
    else:
        print(f"✓ Found existing portal: {portal.name}")
    
    # YouTube playlist link (same for all, but can be updated later with individual video IDs)
    youtube_playlist_url = "https://www.youtube.com/watch?v=BJQy6I0N4NA&list=PL1JUj3q4wWXsqfes3QotyOSOzUZkjcmZC"
    youtube_id = extract_youtube_id(youtube_playlist_url)
    
    # Story 1: A Small Decision
    story1 = {
        'title': 'Story 1: A Small Decision',
        'description': """Mark works in an office and has the same routine every day. One morning, he wakes up tired and unhappy. On his way to work, he sees a small café he has never entered before. He usually ignores it, but this time he decides to go inside. The café is quiet and warm. A friendly woman serves him coffee and smiles. Mark sits near the window and drinks his coffee slowly. For the first time in weeks, he feels relaxed.

When he arrives at work, he notices he is more focused. He finishes his tasks faster than usual. During lunch, he talks more with his colleagues. They laugh and share stories. At the end of the day, Mark feels surprised. A small decision changed his whole day. On his way home, he walks past the café again and smiles. He realizes that small changes can make life better.""",
        'youtube_url': youtube_playlist_url,
        'points': 10,
        'order': 1,
        'questions': [
            {'q': 'Where does Mark work?', 'a': 'Office', 'b': 'Hospital', 'c': 'School', 'd': 'Café', 'correct': 'A', 'points': 1},
            {'q': 'How does Mark feel in the morning?', 'a': 'Excited', 'b': 'Happy', 'c': 'Tired', 'd': 'Angry', 'correct': 'C', 'points': 1},
            {'q': 'What does Mark decide to do differently?', 'a': 'Take a taxi', 'b': 'Skip work', 'c': 'Enter a café', 'd': 'Call a friend', 'correct': 'C', 'points': 1},
            {'q': 'Who serves Mark coffee?', 'a': 'A man', 'b': 'A child', 'c': 'A woman', 'd': 'His boss', 'correct': 'C', 'points': 1},
            {'q': 'How does Mark feel in the café?', 'a': 'Nervous', 'b': 'Relaxed', 'c': 'Bored', 'd': 'Sleepy', 'correct': 'B', 'points': 1},
            {'q': 'How is his work performance?', 'a': 'Worse', 'b': 'Slower', 'c': 'Same', 'd': 'Better', 'correct': 'D', 'points': 1},
            {'q': 'What does he do at lunch?', 'a': 'Eats alone', 'b': 'Works more', 'c': 'Talks with colleagues', 'd': 'Goes home', 'correct': 'C', 'points': 1},
            {'q': 'How does Mark feel at the end of the day?', 'a': 'Sad', 'b': 'Angry', 'c': 'Surprised', 'd': 'Confused', 'correct': 'C', 'points': 1},
            {'q': 'What changes Mark\'s day?', 'a': 'A big event', 'b': 'A small decision', 'c': 'A new job', 'd': 'A phone call', 'correct': 'B', 'points': 1},
            {'q': 'What lesson does the story show?', 'a': 'Money is important', 'b': 'Work is boring', 'c': 'Small changes matter', 'd': 'Coffee is healthy', 'correct': 'C', 'points': 1},
        ],
        'tasks': [
            {'text': 'Write 3 sentences about a small decision you made that changed your day', 'points': 5, 'optional': False},
            {'text': 'List 5 vocabulary words from the story and write their meanings', 'points': 5, 'optional': True},
        ]
    }
    
    # Story 2: The Missed Train
    story2 = {
        'title': 'Story 2: The Missed Train',
        'description': """Sarah plans to visit her sister in another city. She wakes up early and packs her bag carefully. At the train station, she checks the time and feels confident. She decides to buy a coffee before boarding. While waiting, she starts reading messages on her phone. Suddenly, she hears the train whistle. She looks up and sees the train leaving. Sarah feels upset and angry at herself.

She talks to the station worker, who tells her the next train is in one hour. Sarah sits down and thinks about her mistake. Instead of feeling stressed, she decides to relax. She listens to music and watches people at the station. When the next train arrives, she is ready. The trip is calm and enjoyable. When she finally meets her sister, Sarah laughs and tells her the story. She learns to pay more attention and stay present.""",
        'youtube_url': youtube_playlist_url,
        'points': 10,
        'order': 2,
        'questions': [
            {'q': 'Why is Sarah traveling?', 'a': 'Work', 'b': 'Holiday', 'c': 'Visit sister', 'd': 'Study', 'correct': 'C', 'points': 1},
            {'q': 'Where is Sarah?', 'a': 'Airport', 'b': 'Bus stop', 'c': 'Train station', 'd': 'Office', 'correct': 'C', 'points': 1},
            {'q': 'What distracts Sarah?', 'a': 'Coffee', 'b': 'Phone', 'c': 'Music', 'd': 'People', 'correct': 'B', 'points': 1},
            {'q': 'What happens to the train?', 'a': 'It is late', 'b': 'It stops', 'c': 'It leaves', 'd': 'It breaks', 'correct': 'C', 'points': 1},
            {'q': 'How does Sarah feel at first?', 'a': 'Calm', 'b': 'Happy', 'c': 'Angry', 'd': 'Excited', 'correct': 'C', 'points': 1},
            {'q': 'Who helps Sarah?', 'a': 'Her sister', 'b': 'A worker', 'c': 'A friend', 'd': 'A driver', 'correct': 'B', 'points': 1},
            {'q': 'How long does she wait?', 'a': '10 minutes', 'b': '30 minutes', 'c': '1 hour', 'd': '2 hours', 'correct': 'C', 'points': 1},
            {'q': 'What does she do while waiting?', 'a': 'Sleeps', 'b': 'Cries', 'c': 'Listens to music', 'd': 'Calls her boss', 'correct': 'C', 'points': 1},
            {'q': 'How is the second trip?', 'a': 'Stressful', 'b': 'Calm', 'c': 'Boring', 'd': 'Fast', 'correct': 'B', 'points': 1},
            {'q': 'What lesson does Sarah learn?', 'a': 'Wake up early', 'b': 'Drink coffee', 'c': 'Pay attention', 'd': 'Travel less', 'correct': 'C', 'points': 1},
        ],
        'tasks': [
            {'text': 'Describe a time you missed something important. What did you learn?', 'points': 5, 'optional': False},
            {'text': 'Write 5 sentences using past tense verbs from the story', 'points': 5, 'optional': True},
        ]
    }
    
    # Story 3: The New Neighbor
    story3 = {
        'title': 'Story 3: The New Neighbor',
        'description': """David moves into a new apartment in a quiet neighborhood. At first, he feels lonely because he doesn't know anyone. One evening, he hears music coming from the next apartment. The next day, he meets his neighbor, an older man named Mr. Lewis. Mr. Lewis smiles and invites David for tea.

They talk about music, travel, and life. David learns that Mr. Lewis used to be a musician. Over time, they meet often. Mr. Lewis teaches David how to play the guitar. David helps him with shopping and technology. Their friendship grows strong. David no longer feels lonely. He understands that friendship can come from unexpected places.""",
        'youtube_url': youtube_playlist_url,
        'points': 10,
        'order': 3,
        'questions': [
            {'q': 'Where does David move?', 'a': 'House', 'b': 'Apartment', 'c': 'Farm', 'd': 'Office', 'correct': 'B', 'points': 1},
            {'q': 'How does David feel at first?', 'a': 'Happy', 'b': 'Lonely', 'c': 'Angry', 'd': 'Busy', 'correct': 'B', 'points': 1},
            {'q': 'What does David hear?', 'a': 'Noise', 'b': 'Music', 'c': 'Crying', 'd': 'TV', 'correct': 'B', 'points': 1},
            {'q': 'Who is Mr. Lewis?', 'a': 'Neighbor', 'b': 'Boss', 'c': 'Teacher', 'd': 'Cousin', 'correct': 'A', 'points': 1},
            {'q': 'What does Mr. Lewis invite David for?', 'a': 'Dinner', 'b': 'Coffee', 'c': 'Tea', 'd': 'Lunch', 'correct': 'C', 'points': 1},
            {'q': 'What was Mr. Lewis before?', 'a': 'Teacher', 'b': 'Driver', 'c': 'Musician', 'd': 'Doctor', 'correct': 'C', 'points': 1},
            {'q': 'What does Mr. Lewis teach David?', 'a': 'Cooking', 'b': 'Guitar', 'c': 'Writing', 'd': 'Painting', 'correct': 'B', 'points': 1},
            {'q': 'How does David help Mr. Lewis?', 'a': 'Money', 'b': 'Shopping & tech', 'c': 'Cleaning', 'd': 'Driving', 'correct': 'B', 'points': 1},
            {'q': 'How does David feel later?', 'a': 'Lonely', 'b': 'Nervous', 'c': 'Happy', 'd': 'Afraid', 'correct': 'C', 'points': 1},
            {'q': 'What is the main idea?', 'a': 'Music is hard', 'b': 'Neighbors are noisy', 'c': 'Friendship can surprise', 'd': 'Cities are lonely', 'correct': 'C', 'points': 1},
        ],
        'tasks': [
            {'text': 'Write about a friendship that started in an unexpected way', 'points': 5, 'optional': False},
            {'text': 'Create a dialogue between David and Mr. Lewis about music', 'points': 5, 'optional': True},
        ]
    }
    
    # Story 4: The Wrong Email
    story4 = {
        'title': 'Story 4: The Wrong Email',
        'description': """Anna writes an email to complain about her job. She wants to send it to her friend. She writes honestly and emotionally. Without checking, she clicks "send." A few minutes later, she realizes the email went to her manager. Anna feels shocked and scared.

She thinks about quitting, but instead she decides to be honest. She talks to her manager and explains her feelings. Surprisingly, her manager listens carefully. He thanks Anna for her honesty and promises to improve working conditions. Anna feels relieved. A mistake turns into a positive change.""",
        'youtube_url': youtube_playlist_url,
        'points': 10,
        'order': 4,
        'questions': [
            {'q': 'Why does Anna write the email?', 'a': 'To quit', 'b': 'To complain', 'c': 'To ask for help', 'd': 'To say thanks', 'correct': 'B', 'points': 1},
            {'q': 'Who should receive the email?', 'a': 'Boss', 'b': 'Friend', 'c': 'Client', 'd': 'Team', 'correct': 'B', 'points': 1},
            {'q': 'Who actually receives it?', 'a': 'Friend', 'b': 'Manager', 'c': 'Family', 'd': 'HR', 'correct': 'B', 'points': 1},
            {'q': 'How does Anna feel?', 'a': 'Calm', 'b': 'Happy', 'c': 'Shocked', 'd': 'Proud', 'correct': 'C', 'points': 1},
            {'q': 'What does Anna consider?', 'a': 'Vacation', 'b': 'Promotion', 'c': 'Quitting', 'd': 'Moving', 'correct': 'C', 'points': 1},
            {'q': 'What does she decide to do?', 'a': 'Hide', 'b': 'Be honest', 'c': 'Delete email', 'd': 'Apologize by text', 'correct': 'B', 'points': 1},
            {'q': 'How does the manager react?', 'a': 'Angry', 'b': 'Ignores', 'c': 'Listens', 'd': 'Shouts', 'correct': 'C', 'points': 1},
            {'q': 'What does the manager promise?', 'a': 'Raise salary', 'b': 'Fire someone', 'c': 'Improve work', 'd': 'Change office', 'correct': 'C', 'points': 1},
            {'q': 'How does Anna feel at the end?', 'a': 'Relieved', 'b': 'Nervous', 'c': 'Sad', 'd': 'Confused', 'correct': 'A', 'points': 1},
            {'q': 'What is the lesson?', 'a': 'Emails are bad', 'b': 'Never complain', 'c': 'Honesty helps', 'd': 'Managers are strict', 'correct': 'C', 'points': 1},
        ],
        'tasks': [
            {'text': 'Write about a mistake that turned into something positive', 'points': 5, 'optional': False},
            {'text': 'Write a professional email to a manager about workplace concerns', 'points': 5, 'optional': True},
        ]
    }
    
    # Story 5: The Morning Run
    story5 = {
        'title': 'Story 5: The Morning Run',
        'description': """Julia starts running every morning to improve her health. At first, it is difficult. She feels tired and wants to stop. After two weeks, she notices small changes. She sleeps better and feels more energetic. One morning, she meets another runner. They start running together and talking.

Running becomes more enjoyable. Julia feels proud of herself. She learns that progress takes time and support helps a lot.""",
        'youtube_url': youtube_playlist_url,
        'points': 10,
        'order': 5,
        'questions': [
            {'q': 'Why does Julia run?', 'a': 'Fun', 'b': 'Health', 'c': 'Work', 'd': 'Competition', 'correct': 'B', 'points': 1},
            {'q': 'How does she feel at first?', 'a': 'Strong', 'b': 'Tired', 'c': 'Excited', 'd': 'Fast', 'correct': 'B', 'points': 1},
            {'q': 'When does she see changes?', 'a': 'One day', 'b': 'Two weeks', 'c': 'One month', 'd': 'One year', 'correct': 'B', 'points': 1},
            {'q': 'What changes does she notice?', 'a': 'More money', 'b': 'Better sleep', 'c': 'New job', 'd': 'Less time', 'correct': 'B', 'points': 1},
            {'q': 'Who does she meet?', 'a': 'Coach', 'b': 'Friend', 'c': 'Runner', 'd': 'Doctor', 'correct': 'C', 'points': 1},
            {'q': 'What do they do together?', 'a': 'Talk and run', 'b': 'Walk', 'c': 'Compete', 'd': 'Rest', 'correct': 'A', 'points': 1},
            {'q': 'How does Julia feel later?', 'a': 'Bored', 'b': 'Proud', 'c': 'Angry', 'd': 'Sick', 'correct': 'B', 'points': 1},
            {'q': 'What helps Julia continue?', 'a': 'Shoes', 'b': 'Music', 'c': 'Support', 'd': 'Weather', 'correct': 'C', 'points': 1},
            {'q': 'What improves first?', 'a': 'Speed', 'b': 'Health', 'c': 'Time', 'd': 'Strength', 'correct': 'B', 'points': 1},
            {'q': 'Main message?', 'a': 'Running is easy', 'b': 'Health is luck', 'c': 'Progress takes time', 'd': 'Sports are boring', 'correct': 'C', 'points': 1},
        ],
        'tasks': [
            {'text': 'Write about a habit you want to develop and how you will start', 'points': 5, 'optional': False},
            {'text': 'List 10 benefits of regular exercise', 'points': 5, 'optional': True},
        ]
    }
    
    stories = [story1, story2, story3, story4, story5]
    
    # Create lessons, quizzes, and tasks
    for story_data in stories:
        # Check if lesson already exists
        existing_lesson = Lesson.query.filter_by(portal_id=portal.id, title=story_data['title']).first()
        if existing_lesson:
            print(f"\n⚠️  Lesson '{story_data['title']}' already exists. Skipping...")
            continue
        
        # Create lesson
        lesson = Lesson(
            portal_id=portal.id,
            title=story_data['title'],
            description=story_data['description'],
            youtube_url=story_data['youtube_url'],
            youtube_id=youtube_id,
            points_complete=story_data['points'],
            order_index=story_data['order'],
            is_active=True
        )
        db.session.add(lesson)
        db.session.flush()  # Get the lesson ID
        
        print(f"\n✓ Created lesson: {story_data['title']}")
        
        # Create quiz
        quiz = Quiz(
            lesson_id=lesson.id,
            title=f"Quiz: {story_data['title']}"
        )
        db.session.add(quiz)
        db.session.flush()
        
        # Add quiz questions
        for idx, q_data in enumerate(story_data['questions'], 1):
            question = QuizQuestion(
                quiz_id=quiz.id,
                question_text=q_data['q'],
                option_a=q_data['a'],
                option_b=q_data['b'],
                option_c=q_data['c'],
                option_d=q_data['d'],
                correct_option=q_data['correct'],
                points=q_data['points'],
                order_index=idx
            )
            db.session.add(question)
        
        # Update quiz total points
        db.session.flush()
        update_quiz_total_points(quiz.id)
        
        print(f"  ✓ Added {len(story_data['questions'])} quiz questions (total: {quiz.total_points} points)")
        
        # Add tasks
        for idx, task_data in enumerate(story_data['tasks'], 1):
            task = Task(
                lesson_id=lesson.id,
                task_text=task_data['text'],
                points=task_data['points'],
                is_optional=task_data['optional'],
                order_index=idx
            )
            db.session.add(task)
        
        print(f"  ✓ Added {len(story_data['tasks'])} tasks")
    
    db.session.commit()
    print(f"\n✅ Successfully added {len(stories)} English story lessons to '{portal.name}' portal!")
    print(f"\n📚 Portal ID: {portal.id}")
    print(f"🔗 View lessons at: /learn/portal/{portal.id}/lessons")

