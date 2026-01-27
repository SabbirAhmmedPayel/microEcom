require('dotenv').config();
const request = require('supertest');
const app = require('../../index');// Ensure you export 'app' in index.js
const pool = require('../../db');    // Your database connection

describe('Auth Integration Tests', () => {
  
  // Cleanup database before tests to avoid "user already exists" errors
  beforeAll(async () => {
    await pool.query('DELETE FROM users WHERE email = $1', ['test@example.com']);
  });

  // Close database connection after all tests finish
  afterAll(async () => {
    await pool.end();
  });

  describe('POST /auth/signup', () => {
    it('should register a new user successfully', async () => {
  const res = await request(app)
    .post('/auth/signup')
    .send({
      username: 'TestBot', // Added this
      email: 'test@example.com',
      password: 'password123'
    });

  expect(res.statusCode).toEqual(200);
  expect(res.body).toHaveProperty('username', 'TestBot'); // Verify username
});

    it('should fail if email is already taken', async () => {
      const res = await request(app)
        .post('/auth/signup')
        .send({
          email: 'test@example.com',
          password: 'password123'
        });

      expect(res.statusCode).toEqual(500); // Or 400 depending on your error handling
    });
  });

  describe('POST /auth/login', () => {
    it('should login an existing user', async () => {
      const res = await request(app)
        .post('/auth/login')
        .send({
          email: 'test@example.com',
          password: 'password123'
        });

      expect(res.statusCode).toEqual(200);
      expect(res.body.message).toBe('Success');
    });

    it('should reject invalid credentials', async () => {
      const res = await request(app)
        .post('/auth/login')
        .send({
          email: 'test@example.com',
          password: 'wrongpassword'
        });

      expect(res.statusCode).toEqual(401);
    });
  });
});