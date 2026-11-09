const database = db.getSiblingDB("test_db");

const users = [];

for (let i = 1; i <= 1000; i++) {
    users.push({
        user_id: i,
        name: `User_${i}`,
        email: `user${i}@example.com`,
        age: Math.floor(Math.random() * 50) + 18,
        is_active: Math.random() > 0.5,
        created_at: new Date()
    });
}

database.users.insertMany(users);

print("Successfully inserted 1000 documents!");