# Week 7: Secure Authentication System

**Student Name:** Mathew Kiliba  
**Student ID:** M01037499 
**Course:** CST1510 - CW2 - Multi-Domain Intelligence Platform 

## Project Description
A command-line authentication system implementing secure password hashing with bcrypt. This week focuses on secure user registration and login using a text file backend.

## Features
- Secure password hashing using bcrypt with automatic salt generation
- User registration with duplicate username prevention
- Secure user login with password verification
- Strong input validation for usernames and passwords
- File-based user data persistence (`Requirements.txt`)

## Technical Implementation
- Hashing Algorithm: bcrypt with automatic salting
- Data Storage: Plain text file (`Requirements.txt`) with comma-separated values
- Password Security: One-way hashing, no plaintext storage
- Validation: 
  - Username → 3-20 alphanumeric characters
  - Password → 6-50 characters
