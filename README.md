# Ukooinpython

This is a Flask-based web application that provides internet package subscriptions, user management, and payment processing through MPESA. The project integrates Flask with a SQLite database and interacts with the MPESA API for processing payments. It also connects to a local Ganache blockchain instance.

## Features

- **User Registration & Authentication**: Users can register, log in, and manage their profiles.
- **Package Subscription**: Users can view and subscribe to different internet packages.
- **Payment Processing**: Integration with MPESA for online payments.
- **Profile Management**: Users can update their personal details and change passwords.
- **Database**: Data is stored in a SQLite database using SQLAlchemy ORM.
- **Blockchain**: Connection to a local Ganache blockchain instance for future expansions.

## Technologies Used

- **Python**: The core language used for the backend.
- **Flask**: Web framework used to build the application.
- **Flask-SQLAlchemy**: ORM for managing the SQLite database.
- **Flask-Migrate**: For handling database migrations.
- **Werkzeug**: For password hashing.
- **Web3.py**: To connect with the Ganache blockchain.
- **MPESA API**: For processing payments.
- **SQLite**: Database used to store user and package information.
- **HTML/CSS**: For front-end templating and styling.

