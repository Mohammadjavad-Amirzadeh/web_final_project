from flask_mail import Message
from app.extensions import mail

def send_verification_code(email, code):
    msg = Message("Your Verification Code", recipients=[email])

    # Plain text (optional fallback)
    msg.body = f"Your verification code is: {code}"

    # HTML content
    msg.html = f"""
    <html>
      <head>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
            color: #333;
          }}
          .container {{
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
          }}
          .title {{
            font-size: 24px;
            color: #4CAF50;
            margin-bottom: 20px;
            text-align: center;
          }}
          .code {{
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            background-color: #e8f5e9;
            padding: 20px;
            border-radius: 10px;
            color: #2e7d32;
            letter-spacing: 6px;
          }}
          .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: #888;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="title">Welcome to Game Center 🎮</div>
          <p>Thanks for signing up! To verify your email, please use the code below:</p>
          <div class="code">{code}</div>
          <p style="text-align: center; margin-top: 20px;">
            This code is valid for a limited time.
          </p>
          <div class="footer">
            If you didn't request this, you can ignore this email.
          </div>
        </div>
      </body>
    </html>
    """

    mail.send(msg)
