Google Drive Image Recognizer

A full-stack web application that scans images from Google Drive, detects and recognizes faces using OpenCV, and organizes them into per-person folders automatically.

Features

Face Detection & Recognition – Uses OpenCV to identify unique faces.

Automated Organization – Creates folders for each recognized person and organizes images accordingly.

Google Drive Integration – Uses Google Drive API & OAuth 2.0 for secure access.

Full-Stack Integration – Flask backend seamlessly connected with HTML/CSS frontend.

Tech Stack

Backend: Python, Flask, OpenCV, Google Drive API

Frontend: HTML, CSS

Authentication: Google OAuth 2.0

Project Structure
├── process.py        # Main logic for image processing and recognition
├── app.py            # Flask server and route handling
├── templates/        # HTML files for frontend
├── static/           # CSS files
└── README.md         # Project documentation

Setup & Installation

Clone the repository

git clone https://github.com/yourusername/google-drive-image-recognizer.git
cd google-drive-image-recognizer


Create a virtual environment & install dependencies

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


Set up Google API credentials

Enable Google Drive API & OAuth 2.0 in Google Cloud Console.

Download credentials.json and place it in the project root.

Run the application

python app.py


Visit http://localhost:5000 in your browser.

Future Enhancements

Support for multiple image formats (e.g., HEIC, TIFF).

Add user dashboard to view processed folders.

Enhance face recognition using deep learning models.
