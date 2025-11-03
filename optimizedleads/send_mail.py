def register_mail(email, password,industry, subject="", html="", purpose_url=""):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    sender_email = "optimizedleads31@gmail.com"
    sender_password = "ddbxaeaidudiyroy"  # App password, not your main Gmail password
    receiver_email = email

    # Email message setup
    msg = MIMEMultipart('alternative')
    msg['From'] = "Optimized Leads <optimizedleads31@gmail.com>"
    msg['To'] = receiver_email
    msg['Subject'] = subject or "Welcome to OptimizedLeads — Registration Successful ✅"

    # Default HTML message (if none provided)
    if not html:
        html = f"""
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    color: #333;
                    padding: 30px;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background: #fff;
                    border-radius: 10px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    padding: 20px 30px;
                }}
                h1 {{
                    color: #2b4eff;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 13px;
                    color: #777;
                }}
                a {{
                    color: #2b4eff;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to OptimizedLeads 🎉</h1>
                <p>Thank you for registering with <a href="https://optimizedleads.in/">OptimizedLeads.in</a>.</p>
                <p>Your account has been created successfully. Here are your login credentials:</p>
                <div style="background-color:#f0f3ff;padding:10px 15px;border-radius:8px;">
                    <p><b>Industry:</b> {industry.capitalize()}</p>
                    <p><b>Email:</b> {email}</p>
                    <p><b>Password:</b> {password}</p>
                </div>
                <p style="margin-top:15px;">You can log in now and start managing your leads at:</p>
                <p><a href="https://optimizedleads.in/login/" target="_blank">https://optimizedleads.in/login/</a></p>
                <div class="footer">
                    <p>Best Regards,<br><b>OptimizedLeads Team</b></p>
                </div>
            </div>
        </body>
        </html>
        """

    # Connect to Gmail SMTP
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))

        # Send mail
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"✅ Mail sent successfully to {email}")

    except Exception as e:
        print(f"❌ Failed to send mail: {str(e)}")


# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# def leadassign_mail(email):
#     sender = "optimizedleads31@gmail.com"
#     password = "ddbxaeaidudiyroy"  # ⚠️ use app password (not personal one)
    
#     receiver = email
#     subject = "🔥 New Lead Assigned | OptimizedLeads"

#     html_content = f"""
#     <html>
#       <head>
#         <style>
#           body {{
#             font-family: 'Segoe UI', Roboto, Arial, sans-serif;
#             background-color: #f4f7fb;
#             margin: 0;
#             padding: 0;
#           }}
#           .container {{
#             max-width: 600px;
#             background-color: #ffffff;
#             margin: 40px auto;
#             border-radius: 12px;
#             box-shadow: 0 4px 12px rgba(0,0,0,0.1);
#             overflow: hidden;
#           }}
#           .header {{
#             background: linear-gradient(90deg, #4f46e5, #3b82f6);
#             color: white;
#             text-align: center;
#             padding: 20px;
#             font-size: 22px;
#             letter-spacing: 0.5px;
#           }}
#           .content {{
#             padding: 30px 25px;
#             color: #333333;
#             line-height: 1.6;
#           }}
#           .lead-info {{
#             background-color: #f9fafb;
#             padding: 12px 18px;
#             border-radius: 8px;
#             margin-top: 12px;
#             border-left: 4px solid #3b82f6;
#             font-size: 15px;
#           }}
#           .cta {{
#             display: inline-block;
#             margin-top: 25px;
#             background: #3b82f6;
#             color: white;
#             text-decoration: none;
#             padding: 12px 28px;
#             border-radius: 6px;
#             font-weight: 600;
#             letter-spacing: 0.3px;
#           }}
#           .footer {{
#             text-align: center;
#             font-size: 13px;
#             color: #777;
#             margin: 30px 0 10px;
#           }}
#         </style>
#       </head>
#       <body>
#         <div class="container">
#           <div class="header">
#             🚀 Lead Assignment Notification
#           </div>
#           <div class="content">
#             <p>Hello 👋,</p>
#             <p>We’re excited to inform you that a new lead has just been assigned to your account on <b>OptimizedLeads</b>!</p>
#             <div class="lead-info">
#               <b>Assigned to:</b> {email}
#             </div>
#             <p style="margin-top: 20px;">This is a hot lead 🔥 — make sure to check it out as soon as possible.</p>
#             <a href="https://optimizedleads.in/login/" class="cta">Go to Dashboard</a>
#           </div>
#           <div class="footer">
#             © 2025 OptimizedLeads · All rights reserved.
#           </div>
#         </div>
#       </body>
#     </html>
#     """

#     # setup the email
#     msg = MIMEMultipart('alternative')
#     msg['From'] = "Optimized Leads <optimizedleads31@gmail.com>"
#     msg['To'] = receiver
#     msg['Subject'] = subject
#     msg.attach(MIMEText(html_content, 'html'))

#     # send the email
#     try:
#         s = smtplib.SMTP('smtp.gmail.com', 587)
#         s.starttls()
#         s.login(sender, password)
#         s.sendmail(sender, receiver, msg.as_string())
#         s.quit()
#         print(f"✅ Lead assignment mail sent successfully to {receiver}")
#     except Exception as e:
#         print(f"❌ Failed to send email: {e}")




import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def leadassign_mail(email, smtp_connection=None):
    sender = "optimizedleads31@gmail.com"
    password = "ddbxaeaidudiyroy"
    subject = "🔥 New Lead Assigned | OptimizedLeads"

    html_content = f"""
    <html>
    <head>
    <style>
      body {{
        font-family: 'Segoe UI', Roboto, Arial, sans-serif;
        background-color: #f4f7fb;
        margin: 0;
        padding: 0;
      }}
      .container {{
        max-width: 600px;
        background-color: #ffffff;
        margin: 40px auto;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        overflow: hidden;
      }}
      .header {{
        background: linear-gradient(90deg, #4f46e5, #3b82f6);
        color: white;
        text-align: center;
        padding: 20px;
        font-size: 22px;
        letter-spacing: 0.5px;
      }}
      .content {{
        padding: 30px 25px;
        color: #333333;
        line-height: 1.6;
      }}
      .lead-info {{
        background-color: #f9fafb;
        padding: 12px 18px;
        border-radius: 8px;
        margin-top: 12px;
        border-left: 4px solid #3b82f6;
        font-size: 15px;
      }}
      .cta {{
        display: inline-block;
        margin-top: 25px;
        background: #3b82f6;
        color: white;
        text-decoration: none;
        padding: 12px 28px;
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.3px;
      }}
      .footer {{
        text-align: center;
        font-size: 13px;
        color: #777;
        margin: 30px 0 10px;
      }}
    </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          🚀 Lead Assignment Notification
        </div>
        <div class="content">
          <p>Hello 👋,</p>
          <p>We’re excited to inform you that a new lead has just been assigned to your account on <b>OptimizedLeads</b>!</p>
          <div class="lead-info">
            <b>Assigned to:</b> {email}
          </div>
          <p style="margin-top: 20px;">This is a hot lead 🔥 — make sure to check it out as soon as possible.</p>
          <a href="https://optimizedleads.in/subscribers/" class="cta">Go to Dashboard</a>
        </div>
        <div class="footer">
          © 2025 OptimizedLeads · All rights reserved.
        </div>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['From'] = "Optimized Leads <optimizedleads31@gmail.com>"
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        if smtp_connection:
            smtp_connection.sendmail(sender, email, msg.as_string())
        else:
            # single mail send (fallback)
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(sender, password)
            s.sendmail(sender, email, msg.as_string())
            s.quit()

        print(f"✅ Mail sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
