# -*- coding: utf-8 -*-
import http.server
import socketserver
import urllib.parse
import json
import random
import openai
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv

load_dotenv()

# Set the API key as an environment variable
API_KEY = os.getenv("API_KEY")
storage_account_key = os.getenv("storage_account_key")
storage_account_name = os.getenv("storage_account_name")
connection_string = os.getenv("connection_string")
container_name = os.getenv("container_name")

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)
# Define the filename for the JSON file based on user_id
# filename = f"{user_id}.json" if user_id else "unknown_user.json"

# Generate a random 10-digit number as a string
random_number = ''.join(random.choices('0123456789', k=10))

# Create the filename by appending ".json" to the random number
filename = f"{random_number}.json"

html_content = """
<!DOCTYPE html>
<html>
   <head>
      <title>Chatbot(happylife.com)</title>
      <style>
         body {
         font-family: Arial, sans-serif;
         background-color: #f5f5f5;
         margin: 0;
         padding: 0;
         background-image: url('https://muhc.ca/sites/default/files/landing-page/2021/departements_0_0.jpeg');
         background-size: cover; /* Adjust as needed */
         background-position: center center; /* Adjust as needed */
         background-attachment: fixed;
         }
         .header {
         background-color: #E72E06;
         color: #fff;
         text-align: center;
         padding: 20px;
         font-family: 'Dancing Script', cursive;
         display: flex;
         }
         .container {
         max-width: 900px;
         margin: 0 auto;
         padding: 20px;
         }
         .message-container {
         margin-bottom: 10px;
         padding: 10px;
         border-radius: 10px;
         }
         .user-message {
         background-color: #fff;
         text-align: left;
         }
         .bot-message {
         background-color: #d9d9d9;
         }
         .message-input {
         width: 100%;
         padding: 10px;
         font-size: 16px;
         border: none;
         border-radius: 10px;
         }
         .send-button {
         background-color: #007bff;
         color: #fff;
         border: none;
         border-radius: 10px;
         padding: 10px 20px;
         margin-top: 10px;
         cursor: pointer;
         font-size: 16px;
         }
         .submit-button {
         background-color: #2ECC71;
         color: #fff;
         border: none;
         border-radius: 10px;
         padding: 10px 20px;
         margin-top: 10px;
         cursor: pointer;
         text-align: center;
         width: 100%;
         font-size: 16px;
         }
         .login-container {
         text-align: center;
         font-family: 'Brush Script', cursive;
         }
         .validation-input {
         padding: 10px;
         font-size: 16px;
         width: 30%;
         }
         input[type="text"] {
         border: 2px solid #D5DBDB; /* 2px wide solid black border */
         padding: 5px; /* Add padding for spacing between the text and border */
         }
         /* Add styles for the chatbot response */
         .message-container.bot-message {
         width: 100%;
         padding: 5px;
         font-size: 16px;
         border: 2px solid #D5DBDB;
         border-radius: 10px;
         background-color: #D4E6F1    ;
         text-align: left;
         }
         .logo {
             /* Add some space between the title and the logo */
            order: 29; 
            height: 100%; 
            width: 10% 
        }
        .header h1 {
            flex: -1;
            font-size: 30px;
            margin-top: 0%;
            color: #f7f7f5;
        }
        .header p {
            font-size: 20px;
            flex: 1;
            text-align: center;
            text-shadow: 2px 2px 4px #000000;
        }
      </style>
   </head>
   <body>
      <div class="header">
         <h1>MindTalk</h1>
         <p>Your Safe Space for Mental Health Conversations</p>
         <img class="logo" src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjDcKKysNK_nr7adN9HQ-SLTWpuRQLrC4m7Q&usqp=CAU" alt="Logo" width="100">
      </div>
      <div class="container">
         <div class="login-container" id="login-container">
            <h2>Discover Your Empathetic Personal Journal !</h2>
            <form id="login-form">
               <input type="text" id="user-name" class="validation-input" placeholder="Please Enter User Name">
               <br>
               <input type="text" id="user-id" class="validation-input" placeholder="Please Enter User ID">
               <br>
               <input type="button" value="Sign Up" class="send-button" onclick="displaySignupParagraph()">
               <input type="button" value="Login" class="send-button" onclick="validateUser()">
               <!-- Paragraph for Sign Up (initially hidden) -->
               <p id="signup-paragraph" style="display: none;">Here is your user id (5383087758).</p>
            </form>
         </div>
         <div id="login-paragraph" class="message-container bot-message" style="display: none;">
            <p style="text-align: left;">Greetings, my friend! I hope this message finds you 
               in good health and high spirits. It's always a pleasure to engage in a meaningful 
               conversation or provide assistance. What can I help you with today, or is there 
               something specific on your mind that you'd like to discuss?
            </p>
         </div>
         <div id="chat-container" style="display: none;">
            <div id="message-history"></div>
            <form id="chat-form">
               <input type="text" id="user-input" class="message-input" placeholder="Send a message">
               <input type="submit" value="Send" class="submit-button">
            </form>
            <div id="chatbot-response"></div>
         </div>
      </div>
      <script>
         function validateUser() {
            const userId = document.getElementById('user-id').value;
            const validUserIds = ['6821117003','3340978119','1540597861','9269722714','7909412456','7322241387','3117321478','4958318962','7623724496','3788837176','3315237865','9542151260','5262472682','3720627335','1644492762','1828002665','9881242179','4821000552','7942669064','3383712223','3569189629','8040914664','6171856066','7633169071','6308168811','1776462784','2973439984','6333357462','8930692186','9926563554','7710774859','5967131392','1243210638','7495267269','3409584057','5103742427','1672228552','7907521920','1432408977','6943988863','4384611853','3727842891','4286835092','8351042122','4784793201','8579708152','5383087758','8924318252','1105438930','4703009345','5584689140','5759595840','6181319444','7922592102','7304000318','4603886794','2308221112','3132985690','5712455268','7497187481','9390900404','9985595694','2169798213','9530657633','3620626849','6806405790','5948004532','1882053642','2782605841','8810314705','4267804229','6050987949','1834027906','2702282742','9518474930','3160570904','5832027556','5851707789','7260830088','8973434261','8277287049','7204959022','4510452598','8138402274','6135742761','8846014265','4877664788','3566272320','1547859116','7620309619','3772249298','1205629617','2146435570','5038848849','1462232795','7241383735','3398430762','5978472654','7392731657','9640601001','9779208227','4153656579','4365489620','7991761791','5625149125','4771006618','4813335799','6936446539','7680607140','7622555008','8850200114','6375186759','5653868860','3845138122','5376362972','9875280971','1955872848','3511908791','7248707845','3636409995','4422714742','8246429858'];
            if (validUserIds.includes(userId)) {
                // Send the user_id to the server to store it
                fetch(`/store_user_id/${userId}`, {
                    method: 'GET',
                })
                .then(response => response.text())
                .then(data => {
                    console.log(data); // Log the response from the server
                });
         	document.getElementById("login-paragraph").style.display = "block";
                document.getElementById('login-container').style.display = 'none';
                document.getElementById('chat-container').style.display = 'block';
            } else {
                alert('Invalid user ID. Please enter a valid user ID.');
            }
         }
         // Send user input and display chatbot response
            document.getElementById('chat-form').addEventListener('submit', (e) => {
                e.preventDefault();
                const userInput = document.getElementById('user-input').value;
         
                // Display user message in the message history
                const userMessageContainer = document.createElement('div');
                userMessageContainer.className = 'message-container user-message';
                userMessageContainer.textContent = userInput;
                document.getElementById('message-history').appendChild(userMessageContainer);
         
                // Send the user input as a POST request
                fetch('/chatbot', {
                    method: 'POST',
                    body: `user_input=${encodeURIComponent(userInput)}`,
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    // Display chatbot response in the message history
                    const chatbotMessageContainer = document.createElement('div');
                    chatbotMessageContainer.className = 'message-container bot-message';
                    chatbotMessageContainer.innerHTML = data.response; // Use innerHTML to render HTML tags
                    document.getElementById('message-history').appendChild(chatbotMessageContainer);
         
                    // Clear user input
                    document.getElementById('user-input').value = '';
                });
            });	
            
         function displaySignupParagraph() {
            var signupParagraph = document.getElementById("signup-paragraph");
            signupParagraph.style.display = "block"; // Show the signup paragraph
         }
      </script>
   </body>
</html>


"""


class ChatbotRequestHandler(http.server.BaseHTTPRequestHandler):
    # Add a variable to store the user_id
    user_id = None

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        elif self.path.startswith('/store_user_id/'):
            user_id = self.path[len('/store_user_id/'):]
            ChatbotRequestHandler.user_id = user_id  # Store the user_id as an instance variable

            # Create a unique filename for each user based on their user_id
            filename = f"{user_id}.json"

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("User ID stored successfully.".encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        user_input = urllib.parse.parse_qs(post_data)['user_input'][0]

        # Use the stored user_id to create a unique filename
        filename = f"{ChatbotRequestHandler.user_id}.json"

        # Check if the blob exists and read its content
        blob_client = container_client.get_blob_client(filename)
        if blob_client.exists():
            existing_data = blob_client.download_blob()
            existing_json_data = existing_data.readall().decode('utf-8')
            existing_data_dict = json.loads(existing_json_data)
            # Process the content just like before
            previous_messages = existing_data_dict["chat_history"]
            messages = []
            for msg in previous_messages:
                user, gpt = msg["User"], msg["ChatGPT"]
                messages.append({"role": "user", "content": user})
            messages.append({"role": "system", "content": "You are an empathetic personal journal of a user who "
                                                          "responds in the style of a life coach who helps people to self introspect. "
                                                          "Limit your answers to 100 words and try to ask some followup questions about the challenge problem they mentioned recently"
                                                          "something that would help the user untangle  their thoughts. "
                                                          "Never mention that you are an AI. "
                                                          "Initiate a conversation with the user based on previous chat history."})
        else:
            existing_data_dict = {"chat_history": []}
            messages = [
                {"role": "system", "content": "You are an empathetic personal journal of a user who responds in "
                                              "the style of a life coach who helps people to self introspect. "
                                              "Limit your answers to 100 words and try to ask one interesting question- "
                                              "something that would help the user inspire their spirit. "
                                              "Never mention that you are an AI."},
            ]
            # Define a conversation with a creative assistant
        messages.append({"role": "user", "content": user_input})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stop=None,
            api_key=API_KEY
        )
        chatbot_response = response.choices[0].message["content"].strip()
        chatbot_response = chatbot_response.replace('\n', '<br>')

        # Append the new user message and chatbot response
        existing_data_dict["chat_history"].append({
            "User": user_input,
            "ChatGPT": chatbot_response
        })

        # Convert the updated data to JSON
        updated_json_data = json.dumps(existing_data_dict, indent=4)

        # Upload the updated data back to the blob with the unique filename
        blob_client.upload_blob(updated_json_data, overwrite=True)

        # Send the chatbot response as JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'response': chatbot_response}).encode('utf-8'))


def main():
   
    port = int(os.environ.get("PORT", 8000))

    # Use the 'port' variable when starting your server
    server_address = ('', port)
    httpd = socketserver.TCPServer(server_address, ChatbotRequestHandler)

    print(f'Chatbot web page is running at http://localhost:{port}/')

    try:
        # Serve requests indefinitely
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    # Shutdown the server
    httpd.shutdown()
    print("Server has been shut down.")


if __name__ == "__main__":
    main()
